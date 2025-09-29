from fastapi import APIRouter, HTTPException, status, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging
from pydantic import BaseModel
from typing import Optional

from auth.dependencies import get_current_user
from seed_data import initialize_new_user

logger = logging.getLogger(__name__)

class OnboardingRequest(BaseModel):
    add_sample_data: bool = False
    workspace_type: Optional[str] = None  # "clean", "sample", "guided"

def create_onboarding_router(db: AsyncIOMotorDatabase) -> APIRouter:
    """Create onboarding router with database dependency injected."""
    
    router = APIRouter(prefix="/onboarding", tags=["onboarding"])
    
    @router.post("/setup")
    async def setup_workspace(onboarding: OnboardingRequest, req: Request):
        """Set up user's workspace based on their preferences"""
        
        user = await get_current_user(req, db)
        
        # Check if user already has tasks (already onboarded)
        existing_tasks = await db.tasks.count_documents({"user_id": user["id"]})
        if existing_tasks > 0:
            return {
                "success": True, 
                "message": "Workspace already set up",
                "tasks_count": existing_tasks
            }
        
        try:
            if onboarding.add_sample_data:
                # Add personalized sample data
                await initialize_new_user(
                    user_id=user["id"], 
                    user_name=user.get("name"),
                    use_sample_data=True
                )
                
                # Count the added data
                projects_count = await db.projects.count_documents({"user_id": user["id"]})
                tasks_count = await db.tasks.count_documents({"user_id": user["id"]})
                
                return {
                    "success": True,
                    "message": "Workspace set up with personalized sample data",
                    "projects_count": projects_count,
                    "tasks_count": tasks_count
                }
            else:
                # User chose clean workspace
                return {
                    "success": True,
                    "message": "Clean workspace ready - you can start creating your own tasks!",
                    "projects_count": 0,
                    "tasks_count": 0
                }
                
        except Exception as e:
            logger.error(f"Error setting up workspace for user {user['id']}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to set up workspace"
            )
    
    @router.get("/status")
    async def get_onboarding_status(req: Request):
        """Check if user has completed onboarding"""
        
        user = await get_current_user(req, db)
        
        # Check if user has any tasks or projects
        tasks_count = await db.tasks.count_documents({"user_id": user["id"]})
        projects_count = await db.projects.count_documents({"user_id": user["id"]})
        
        # Also check if user has any notification settings (indicates they've used the app)
        settings_exist = await db.notification_settings.find_one({"user_id": user["id"]})
        
        onboarded = tasks_count > 0 or projects_count > 0 or settings_exist is not None
        
        return {
            "onboarded": onboarded,
            "tasks_count": tasks_count,
            "projects_count": projects_count,
            "has_settings": settings_exist is not None
        }
    
    return router