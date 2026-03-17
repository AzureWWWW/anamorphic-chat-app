from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from deps import get_db, get_current_user
from models import User, PublicKey

router = APIRouter()

class UpsertKeyIn(BaseModel):
    pubkey: dict

@router.post("/upsert")
async def upsert_key(
    payload: UpsertKeyIn,
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user)
):
    # Check if a key already exists for this user
    existing = await db.scalar(
        select(PublicKey).where(PublicKey.user_id == me.id)
    )
    if existing:
        # Update in place
        existing.pubkey = payload.pubkey
    else:
        db.add(PublicKey(user_id=me.id, pubkey=payload.pubkey))

    await db.commit()
    return {"message": "pubkey_updated"}


@router.get("/get/{username}")
async def get_user_pubkey(username: str, db: AsyncSession = Depends(get_db)):
    target = await db.scalar(select(User).where(User.username == username))
    if not target:
        raise HTTPException(404, "user_not_found")

    target_pubkey = await db.scalar(
        select(PublicKey).where(PublicKey.user_id == target.id)
    )
    if not target_pubkey or not target_pubkey.pubkey:
        raise HTTPException(404, "pubkey_not_found")

    return {"username": username, "pubkey": target_pubkey.pubkey}