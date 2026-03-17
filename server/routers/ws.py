from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from jose import jwt, JWTError
from models import User, Message, PublicKey
from sqlalchemy import select, insert
from database import SessionLocal
import json, time

router = APIRouter()
active_ws = {}

SECRET = "Thanhbjim@$@&^@&%^&RFghgjSachin"

@router.websocket("")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()

    # ---- AUTHENTICATION ----
    token = ws.query_params.get("token")
    if not token:
        await ws.close(code=4401)
        return

    try:
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        me_id = int(payload["user_id"])
    except (JWTError, ValueError, TypeError):
        await ws.close(code=4401)
        return

    # fetch username
    async with SessionLocal() as db:
        user = await db.get(User, me_id)
        if not user:
            await ws.close(code=4401)
            return
        me_username = user.username

    active_ws[me_id] = ws

    try:
        # ---- MAIN LOOP ----
        while True:
            raw = await ws.receive_text()
            msg = json.loads(raw)

            mtype = msg.get("type")

            # ------- GET PUBKEY -------
            if mtype == "get_pubkey":
                target_username = msg["target_username"]
                async with SessionLocal() as db:
                    target = await db.scalar(
                        select(User).where(User.username == target_username)
                    )
                    if not target:
                        await ws.send_text(json.dumps({"type": "user_not_found"}))
                        continue

                    target_pubkey = await db.scalar(select(PublicKey).where(PublicKey.id == target.id))
                    if not target_pubkey or not target_pubkey.pubkey:
                        await ws.send_text(json.dumps({"type": "pubkey_not_found"}))
                        continue

                await ws.send_text(json.dumps({
                    "type": "pubkey",
                    "target_username": target_username,
                    "pubkey": target_pubkey.pubkey
                }))

            # ------- SEND CIPHERTEXT -------
            elif mtype == "ciphertext":
                target_username = msg["to"]
                ts = int(time.time())

                async with SessionLocal() as db:
                    target = await db.scalar(
                        select(User).where(User.username == target_username)
                    )
                    if not target:
                        await ws.send_text(json.dumps({"type": "user_not_found"}))
                        continue

                    await db.execute(
                        insert(Message).values(
                            sender_id=me_id,
                            receiver_id=target.id,
                            body=msg["body"],
                            timestamp=ts,
                            delivered=target.active_status,
                        )
                    )
                    await db.commit()

                outgoing = json.dumps({
                    "type": "message",
                    "from": me_id,
                    "to": target.id,
                    "body": msg["body"],
                    "timestamp": ts,
                })

                # Push to recipient if online
                target_ws = active_ws.get(target.id)
                if target_ws:
                    await target_ws.send_text(outgoing)

                # Echo back to sender so the message appears immediately
                # without needing a page reload.
                sender_ws = active_ws.get(me_id)
                if sender_ws:
                    await sender_ws.send_text(outgoing)

    except WebSocketDisconnect:
        pass

    finally:
        active_ws.pop(me_id, None)