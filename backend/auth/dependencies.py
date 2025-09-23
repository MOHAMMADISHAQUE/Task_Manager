from fastapi import HTTPException, Request, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
from .utils import hash_token
import os

async def get_current_user(request: Request, db: AsyncIOMotorDatabase):
    """
    Get current user from session token.
    Checks cookie first, then Authorization header as fallback.
    """
    session_token = None
    
    # First, try to get from cookies
    session_token = request.cookies.get("session_token")
    
    # If not in cookies, try Authorization header
    if not session_token:
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            session_token = authorization.split(" ")[1]
    
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Hash the token to match what's stored in database
    hashed_token = hash_token(session_token)
    
    # Find session in database
    session = await db.sessions.find_one({"session_token": hashed_token})
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if session is expired
    expires_at = session["expires_at"]
    if hasattr(expires_at, 'replace') and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if expires_at < datetime.now(timezone.utc):
        # Clean up expired session
        await db.sessions.delete_one({"_id": session["_id"]})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = await db.users.find_one({"id": session["user_id"]})
    
    if not user or not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user