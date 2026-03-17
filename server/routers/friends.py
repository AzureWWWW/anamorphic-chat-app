from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from deps import get_db, get_current_user
from models import User, Friendship

router = APIRouter()

@router.get("/list")
async def get_friends(db: AsyncSession = Depends(get_db), me: User = Depends(get_current_user)):
    """Get list of user's friends"""
    friendships = await db.scalars(
        select(Friendship).where(Friendship.user_id == me.id)
    )
    
    friends = []
    for friendship in friendships:
        friend = await db.get(User, friendship.friend_id)
        if friend:
            friends.append({
                "id": friend.id,
                "username": friend.username,
                "email": getattr(friend, 'email', f'{friend.username}@example.com'),
                "status": "online" if friend.active_status else "offline",
                "avatar": f"https://i.pravatar.cc/150?u={friend.username}",
            })
    
    return {"friends": friends}

@router.post("/add/{friend_id}")
async def add_friend(
    friend_id: int,
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user)
):
    """Add a friend"""
    
    # Can't add yourself
    if friend_id == me.id:
        raise HTTPException(400, "Cannot add yourself as friend")
    
    # Check if friend exists
    friend = await db.get(User, friend_id)
    if not friend:
        raise HTTPException(404, "User not found")
    
    # Check if already friends
    existing = await db.scalar(
        select(Friendship).where(
            (Friendship.user_id == me.id) & (Friendship.friend_id == friend_id)
        )
    )
    
    if existing:
        raise HTTPException(400, "Already friends with this user")
    
    # Create friendship (one-way for now)
    friendship = Friendship(user_id=me.id, friend_id=friend_id)
    db.add(friendship)
    await db.commit()
    
    return {
        "message": f"Added {friend.username} as friend",
        "friend": {
            "id": friend.id,
            "username": friend.username,
            "avatar": f"https://i.pravatar.cc/150?u={friend.username}",
        }
    }

@router.delete("/remove/{friend_id}")
async def remove_friend(
    friend_id: int,
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user)
):
    """Remove a friend"""
    
    friendship = await db.scalar(
        select(Friendship).where(
            (Friendship.user_id == me.id) & (Friendship.friend_id == friend_id)
        )
    )
    
    if not friendship:
        raise HTTPException(404, "Friend not found")
    
    await db.delete(friendship)
    await db.commit()
    
    return {"message": "Friend removed"}

@router.get("/available")
async def get_available_friends(
    db: AsyncSession = Depends(get_db),
    me: User = Depends(get_current_user)
):
    """Get list of users who are NOT already friends"""
    
    # Get all friendships for current user
    my_friendships = await db.scalars(
        select(Friendship).where(Friendship.user_id == me.id)
    )
    friend_ids = [f.friend_id for f in my_friendships]
    
    # Get all users except self and existing friends
    all_users = await db.scalars(select(User))
    available = [
        {
            "id": u.id,
            "username": u.username,
            "email": getattr(u, 'email', f'{u.username}@example.com'),
            "status": "online" if u.active_status else "offline",
            "avatar": f"https://i.pravatar.cc/150?u={u.username}",
        }
        for u in all_users
        if u.id != me.id and u.id not in friend_ids
    ]
    
    return {"available_friends": available}