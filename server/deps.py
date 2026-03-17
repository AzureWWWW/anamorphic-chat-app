from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import settings, SessionLocal
from models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_db():
    async with SessionLocal() as session:
        yield session

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALG])
        uid = int(payload.get("user_id"))
    except (JWTError, ValueError, TypeError):
        raise HTTPException(401, "invalid_token")
    user = await db.scalar(select(User).where(User.id == uid))
    if not user:
        raise HTTPException(401, "user_not_found")
    return user