from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import time

from deps import get_db, get_current_user
from models import Message, User

router = APIRouter()

class HistoryIn(BaseModel):
    with_user: str
    limit: int = 50
    before_ts: int | None = None

class SendMessageRequest(BaseModel):
    receiver_id: int
    body: dict

@router.post("/send")
async def send_message(
    request: SendMessageRequest,
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user)
):
    """Send a message to another user"""
    
    receiver_id = request.receiver_id
    body = request.body
    
    # Check if receiver exists
    receiver = await db.get(User, receiver_id)
    if not receiver:
        return {"error": "Receiver not found"}
    
    # Create message
    msg = Message(
        sender_id=me.id,
        receiver_id=receiver_id,
        body=body,
        timestamp=int(time.time())
    )
    
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    
    return {
        "message": "sent",
        "id": msg.id,
        "timestamp": msg.timestamp
    }

@router.post("/history")
async def history(p: HistoryIn, db: AsyncSession = Depends(get_db), me: User = Depends(get_current_user)):
    peer = await db.scalar(select(User).where(User.username == p.with_user))
    if not peer:
        return {"items": []}
    cutoff = p.before_ts or int(time.time()) + 1  # +1 so messages sent right now are included
    q = (
        select(Message)
        .where(
            (
                (Message.sender_id == me.id) & (Message.receiver_id == peer.id)
            ) | (
                (Message.sender_id == peer.id) & (Message.receiver_id == me.id)
            ),
            Message.timestamp < cutoff
        )
        # rendering upside-down
        .order_by(Message.timestamp.asc())
        .limit(p.limit)
    )
    rows = (await db.scalars(q)).all()
    items = [
        {
            "type": "ciphertext",
            "from": r.sender_id,
            "to": r.receiver_id,
            "timestamp": r.timestamp,
            "body": r.body
        }
        for r in rows
    ]
    return {"items": items}