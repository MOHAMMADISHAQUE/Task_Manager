from fastapi import APIRouter, HTTPException, status, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
import logging
from typing import Optional, Dict, Any
from pydantic import BaseModel

from auth.dependencies import get_current_user

logger = logging.getLogger(__name__)

class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    picture: Optional[str] = None

class NotificationSettings(BaseModel):
    email: bool = True
    push: bool = True
    desktop: bool = False
    task_reminders: bool = True
    project_updates: bool = True
    weekly_digest: bool = False

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

def create_settings_router(db: AsyncIOMotorDatabase) -> APIRouter:
    """Create settings router with database dependency injected."""
    
    router = APIRouter(prefix="/settings", tags=["settings"])
    
    @router.get("/profile")
    async def get_profile(req: Request):
        """Get user profile information"""
        
        user = await get_current_user(req, db)
        
        # Get user settings if they exist
        settings = await db.user_settings.find_one({"user_id": user["id"]})
        
        profile_data = {
            "name": user.get("name", ""),
            "email": user.get("email", ""),
            "picture": user.get("picture"),
            "auth_provider": user.get("auth_provider", "email"),
            "role": settings.get("role", "") if settings else "",
            "timezone": settings.get("timezone", "UTC+0") if settings else "UTC+0",
            "language": settings.get("language", "English") if settings else "English"
        }
        
        return {"profile": profile_data}
    
    @router.put("/profile")
    async def update_profile(profile_update: ProfileUpdateRequest, req: Request):
        """Update user profile information"""
        
        user = await get_current_user(req, db)
        
        # Update user document
        user_updates = {}
        if profile_update.name is not None:
            user_updates["name"] = profile_update.name
        if profile_update.picture is not None:
            user_updates["picture"] = profile_update.picture
        
        if user_updates:
            user_updates["updated_at"] = datetime.now(timezone.utc)
            await db.users.update_one(
                {"id": user["id"]}, 
                {"$set": user_updates}
            )
        
        # Update or create user settings
        settings_updates = {}
        if profile_update.role is not None:
            settings_updates["role"] = profile_update.role
        if profile_update.timezone is not None:
            settings_updates["timezone"] = profile_update.timezone
        if profile_update.language is not None:
            settings_updates["language"] = profile_update.language
        
        if settings_updates:
            settings_updates.update({
                "user_id": user["id"],
                "updated_at": datetime.now(timezone.utc)
            })
            
            await db.user_settings.update_one(
                {"user_id": user["id"]},
                {"$set": settings_updates},
                upsert=True
            )
        
        return {"success": True, "message": "Profile updated successfully"}
    
    @router.get("/notifications")
    async def get_notification_settings(req: Request):
        """Get user notification preferences"""
        
        user = await get_current_user(req, db)
        
        # Get notification settings or use defaults
        settings = await db.notification_settings.find_one({"user_id": user["id"]})
        
        if settings:
            return {
                "notifications": {
                    "email": settings.get("email", True),
                    "push": settings.get("push", True), 
                    "desktop": settings.get("desktop", False),
                    "task_reminders": settings.get("task_reminders", True),
                    "project_updates": settings.get("project_updates", True),
                    "weekly_digest": settings.get("weekly_digest", False)
                }
            }
        else:
            # Return default settings
            return {
                "notifications": {
                    "email": True,
                    "push": True,
                    "desktop": False,
                    "task_reminders": True,
                    "project_updates": True,
                    "weekly_digest": False
                }
            }
    
    @router.put("/notifications")
    async def update_notification_settings(notifications: NotificationSettings, req: Request):
        """Update user notification preferences"""
        
        user = await get_current_user(req, db)
        
        settings_data = {
            "user_id": user["id"],
            "email": notifications.email,
            "push": notifications.push,
            "desktop": notifications.desktop,
            "task_reminders": notifications.task_reminders,
            "project_updates": notifications.project_updates,
            "weekly_digest": notifications.weekly_digest,
            "updated_at": datetime.now(timezone.utc)
        }
        
        await db.notification_settings.update_one(
            {"user_id": user["id"]},
            {"$set": settings_data},
            upsert=True
        )
        
        return {"success": True, "message": "Notification settings updated successfully"}
    
    @router.post("/change-password")
    async def change_password(password_change: ChangePasswordRequest, req: Request):
        """Change user password (for email auth users only)"""
        
        user = await get_current_user(req, db)
        
        # Only allow password change for email auth users
        if user.get("auth_provider") != "email":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password change is only available for email authentication users"
            )
        
        # Verify current password
        import bcrypt
        if not bcrypt.checkpw(password_change.current_password.encode('utf-8'), user["password_hash"].encode('utf-8')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Hash new password
        new_password_hash = bcrypt.hashpw(password_change.new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Update password
        await db.users.update_one(
            {"id": user["id"]},
            {"$set": {
                "password_hash": new_password_hash,
                "updated_at": datetime.now(timezone.utc)
            }}
        )
        
        return {"success": True, "message": "Password changed successfully"}
    
    @router.get("/security")
    async def get_security_info(req: Request):
        """Get security information for the user"""
        
        user = await get_current_user(req, db)
        
        # Get login sessions (last 5)
        sessions = await db.sessions.find(
            {"user_id": user["id"]}, 
            {"_id": 0},  # Exclude ObjectId field
            sort=[("created_at", -1)]
        ).limit(5).to_list(length=5)
        
        login_history = []
        for session in sessions:
            login_history.append({
                "created_at": session["created_at"].isoformat(),
                "expires_at": session["expires_at"].isoformat(),
                "active": session["expires_at"] > datetime.now(timezone.utc)
            })
        
        return {
            "auth_provider": user.get("auth_provider", "email"),
            "two_factor_enabled": False,  # Not implemented yet
            "login_history": login_history
        }
    
    return router