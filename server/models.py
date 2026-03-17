from datetime import datetime, timezone
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from sqlalchemy import String, Integer, ForeignKey, Boolean, DateTime, UniqueConstraint, JSON

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(200))
    active_status: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    public_keys = relationship(
        "PublicKey",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    friendships = relationship(
        "Friendship",
        foreign_keys="Friendship.user_id",
        back_populates="user",
        cascade="all, delete-orphan"
    )

class PublicKey(Base):
    __tablename__ = "public_keys"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    pubkey: Mapped[dict] = mapped_column(JSON)
    user = relationship("User", back_populates="public_keys")

class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    receiver_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    body: Mapped[dict] = mapped_column(JSON)
    timestamp: Mapped[int] = mapped_column(Integer, index=True)
    delivered: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

class Friendship(Base):
    __tablename__ = "friendships"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    friend_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", foreign_keys=[user_id], back_populates="friendships")
    
    __table_args__ = (UniqueConstraint('user_id', 'friend_id', name='unique_friendship'),)