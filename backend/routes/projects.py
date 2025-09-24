from fastapi import APIRouter, HTTPException, status, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
from typing import List, Optional
from models.tasks import (
    Project, ProjectCreateRequest, ProjectUpdateRequest, ProjectResponse
)
from auth.dependencies import get_current_user
import logging

logger = logging.getLogger(__name__)

def create_projects_router(db: AsyncIOMotorDatabase) -> APIRouter:
    """Create projects router with database dependency injected."""
    
    router = APIRouter(prefix="/projects", tags=["projects"])
    
    @router.get("/", response_model=List[ProjectResponse])
    async def get_projects(
        request: Request,
        status: Optional[str] = None
    ):
        """Get all projects for the current user."""
        user = await get_current_user(request, db)
        
        # Build filter query
        filter_query = {"user_id": user["id"]}
        if status:
            filter_query["status"] = status
        
        # Get projects from database
        projects_cursor = db.projects.find(filter_query)
        projects = await projects_cursor.to_list(1000)
        
        # Add task counts for each project
        project_responses = []
        for project in projects:
            task_count = await db.tasks.count_documents({
                "project_id": project["id"], 
                "user_id": user["id"]
            })
            
            project_response = ProjectResponse(**project)
            project_response.tasks_count = task_count
            project_responses.append(project_response)
        
        return project_responses
    
    @router.post("/", response_model=ProjectResponse)
    async def create_project(request: Request, project_data: ProjectCreateRequest):
        """Create a new project."""
        user = await get_current_user(request, db)
        
        # Parse due_date if provided
        due_date = None
        if project_data.due_date:
            try:
                due_date = datetime.fromisoformat(project_data.due_date.replace('Z', '+00:00'))
            except ValueError:
                try:
                    due_date = datetime.strptime(project_data.due_date, '%Y-%m-%d')
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid date format. Use YYYY-MM-DD or ISO format."
                    )
        
        # Create project object
        project = Project(
            name=project_data.name,
            description=project_data.description,
            priority=project_data.priority,
            due_date=due_date,
            user_id=user["id"],
            team_members=project_data.team_members
        )
        
        # Save to database
        await db.projects.insert_one(project.dict())
        
        project_response = ProjectResponse(**project.dict())
        project_response.tasks_count = 0
        return project_response
    
    @router.get("/{project_id}", response_model=ProjectResponse)
    async def get_project(request: Request, project_id: str):
        """Get a specific project."""
        user = await get_current_user(request, db)
        
        project = await db.projects.find_one({"id": project_id, "user_id": user["id"]})
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Add task count
        task_count = await db.tasks.count_documents({
            "project_id": project_id, 
            "user_id": user["id"]
        })
        
        project_response = ProjectResponse(**project)
        project_response.tasks_count = task_count
        return project_response
    
    @router.put("/{project_id}", response_model=ProjectResponse)
    async def update_project(request: Request, project_id: str, project_update: ProjectUpdateRequest):
        """Update a project."""
        user = await get_current_user(request, db)
        
        # Check if project exists and belongs to user
        existing_project = await db.projects.find_one({"id": project_id, "user_id": user["id"]})
        if not existing_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Build update data
        update_data = {}
        for field, value in project_update.dict(exclude_unset=True).items():
            if field == "due_date" and value:
                try:
                    update_data[field] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except ValueError:
                    try:
                        update_data[field] = datetime.strptime(value, '%Y-%m-%d')
                    except ValueError:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid date format. Use YYYY-MM-DD or ISO format."
                        )
            else:
                update_data[field] = value
        
        if update_data:
            update_data["updated_at"] = datetime.now(timezone.utc)
            await db.projects.update_one(
                {"id": project_id, "user_id": user["id"]},
                {"$set": update_data}
            )
        
        # Return updated project
        updated_project = await db.projects.find_one({"id": project_id, "user_id": user["id"]})
        task_count = await db.tasks.count_documents({
            "project_id": project_id, 
            "user_id": user["id"]
        })
        
        project_response = ProjectResponse(**updated_project)
        project_response.tasks_count = task_count
        return project_response
    
    @router.delete("/{project_id}")
    async def delete_project(request: Request, project_id: str):
        """Delete a project and all its tasks."""
        user = await get_current_user(request, db)
        
        # Check if project exists
        project = await db.projects.find_one({"id": project_id, "user_id": user["id"]})
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Delete all tasks associated with this project
        await db.tasks.delete_many({"project_id": project_id, "user_id": user["id"]})
        
        # Delete the project
        await db.projects.delete_one({"id": project_id, "user_id": user["id"]})
        
        return {"message": "Project and associated tasks deleted successfully"}
    
    return router