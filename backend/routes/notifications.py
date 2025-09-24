from fastapi import APIRouter, HTTPException, status, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone, timedelta
import uuid
import logging
from typing import List, Optional
from pydantic import BaseModel

from auth.dependencies import get_current_user

logger = logging.getLogger(__name__)

class Notification(BaseModel):
    id: str
    user_id: str
    title: str
    message: str
    type: str = "info"  # info, success, warning, error
    read: bool = False
    created_at: datetime
    action_url: Optional[str] = None

class MarkReadRequest(BaseModel):
    notification_ids: List[str]

def create_notifications_router(db: AsyncIOMotorDatabase) -> APIRouter:
    """Create notifications router with database dependency injected."""
    
    router = APIRouter(prefix="/notifications", tags=["notifications"])
    
    @router.get("/")
    async def get_notifications(req: Request, limit: int = 20, unread_only: bool = False):
        """Get user notifications"""
        
        user = await get_current_user(req, db)
        
        query = {"user_id": user["id"]}
        if unread_only:
            query["read"] = False
        
        notifications = await db.notifications.find(
            query,
            {"_id": 0},  # Exclude ObjectId field
            sort=[("created_at", -1)]
        ).limit(limit).to_list(length=limit)
        
        return {"notifications": notifications}
    
    @router.get("/unread-count")
    async def get_unread_count(req: Request):
        """Get count of unread notifications"""
        
        user = await get_current_user(req, db)
        
        count = await db.notifications.count_documents({
            "user_id": user["id"],
            "read": False
        })
        
        return {"unread_count": count}
    
    @router.put("/mark-read")
    async def mark_notifications_read(mark_read: MarkReadRequest, req: Request):
        """Mark notifications as read"""
        
        user = await get_current_user(req, db)
        
        await db.notifications.update_many(
            {
                "user_id": user["id"],
                "id": {"$in": mark_read.notification_ids}
            },
            {"$set": {"read": True, "updated_at": datetime.now(timezone.utc)}}
        )
        
        return {"success": True, "message": f"Marked {len(mark_read.notification_ids)} notifications as read"}
    
    @router.put("/mark-all-read")
    async def mark_all_notifications_read(req: Request):
        """Mark all notifications as read"""
        
        user = await get_current_user(req, db)
        
        result = await db.notifications.update_many(
            {"user_id": user["id"], "read": False},
            {"$set": {"read": True, "updated_at": datetime.now(timezone.utc)}}
        )
        
        return {"success": True, "message": f"Marked {result.modified_count} notifications as read"}
    
    @router.delete("/{notification_id}")
    async def delete_notification(notification_id: str, req: Request):
        """Delete a specific notification"""
        
        user = await get_current_user(req, db)
        
        result = await db.notifications.delete_one({
            "id": notification_id,
            "user_id": user["id"]
        })
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        return {"success": True, "message": "Notification deleted"}
    
    @router.post("/test")
    async def create_test_notification(req: Request):
        """Create a test notification (for development)"""
        
        user = await get_current_user(req, db)
        
        # Generate sample notifications
        test_notifications = [
            {
                "id": str(uuid.uuid4()),
                "user_id": user["id"],
                "title": "Task Due Soon",
                "message": "Your task 'Complete project proposal' is due in 2 hours",
                "type": "warning",
                "read": False,
                "created_at": datetime.now(timezone.utc),
                "action_url": "/tasks"
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": user["id"],
                "title": "Task Completed",
                "message": "Great job! You've completed 'Review design mockups'",
                "type": "success",
                "read": False,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=5),
                "action_url": "/dashboard"
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": user["id"],
                "title": "New AI Feature",
                "message": "Try our new Smart Task Creator - create tasks with natural language!",
                "type": "info",
                "read": False,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=1),
                "action_url": "/tasks"
            }
        ]
        
        await db.notifications.insert_many(test_notifications)
        
        return {"success": True, "message": f"Created {len(test_notifications)} test notifications"}
    
    return router


async def create_notification(db: AsyncIOMotorDatabase, user_id: str, title: str, message: str, 
                            notification_type: str = "info", action_url: Optional[str] = None):
    """Helper function to create a new notification"""
    
    notification = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "title": title,
        "message": message,
        "type": notification_type,
        "read": False,
        "created_at": datetime.now(timezone.utc),
        "action_url": action_url
    }
    
    try:
        await db.notifications.insert_one(notification)
        logger.info(f"Created notification for user {user_id}: {title}")
    except Exception as e:
        logger.error(f"Failed to create notification: {e}")