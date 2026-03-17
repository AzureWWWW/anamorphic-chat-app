from fastapi import APIRouter
from routers import auth, keys, messages, ws, friends

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(keys.router, prefix="/keys")
api_router.include_router(messages.router, prefix="/messages")
api_router.include_router(friends.router, prefix="/friends")
api_router.include_router(ws.router, prefix="/ws")