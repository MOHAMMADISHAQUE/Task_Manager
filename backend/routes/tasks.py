from fastapi import APIRouter, HTTPException, status, Request, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
from typing import List, Optional
from models.tasks import (
    Task, Project, TaskCreateRequest, TaskUpdateRequest, 
    ProjectCreateRequest, ProjectUpdateRequest, TaskResponse, ProjectResponse
)
from auth.dependencies import get_current_user
import logging

logger = logging.getLogger(__name__)

def create_tasks_router(db: AsyncIOMotorDatabase) -> APIRouter:
    """Create tasks router with database dependency injected."""
    
    router = APIRouter(prefix="/tasks", tags=["tasks"])
    
    @router.get("/", response_model=List[TaskResponse])
    async def get_tasks(
        request: Request,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        project_id: Optional[str] = None
    ):
        """Get all tasks for the current user."""
        user = await get_current_user(request, db)
        
        # Build filter query
        filter_query = {"user_id": user["id"]}
        if status:
            filter_query["status"] = status
        if priority:
            filter_query["priority"] = priority
        if project_id:
            filter_query["project_id"] = project_id
        
        # Get tasks from database
        tasks_cursor = db.tasks.find(filter_query)
        tasks = await tasks_cursor.to_list(1000)
        
        # Convert to response format
        return [TaskResponse(**task) for task in tasks]
    
    @router.post("/", response_model=TaskResponse)
    async def create_task(request: Request, task_data: TaskCreateRequest):
        """Create a new task."""
        user = await get_current_user(request, db)
        
        # Parse due_date if provided
        due_date = None
        if task_data.due_date:
            try:
                due_date = datetime.fromisoformat(task_data.due_date.replace('Z', '+00:00'))
            except ValueError:
                try:
                    due_date = datetime.strptime(task_data.due_date, '%Y-%m-%d')
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid date format. Use YYYY-MM-DD or ISO format."
                    )
        
        # Create task object
        task = Task(
            title=task_data.title,
            description=task_data.description,
            priority=task_data.priority,
            due_date=due_date,
            user_id=user["id"],
            project_id=task_data.project_id,
            tags=task_data.tags
        )
        
        # Save to database
        await db.tasks.insert_one(task.dict())
        
        return TaskResponse(**task.dict())
    
    @router.get("/{task_id}", response_model=TaskResponse)
    async def get_task(request: Request, task_id: str):
        """Get a specific task."""
        user = await get_current_user(request, db)
        
        task = await db.tasks.find_one({"id": task_id, "user_id": user["id"]})
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        return TaskResponse(**task)
    
    @router.put("/{task_id}", response_model=TaskResponse)
    async def update_task(request: Request, task_id: str, task_update: TaskUpdateRequest):
        """Update a task."""
        user = await get_current_user(request, db)
        
        # Check if task exists and belongs to user
        existing_task = await db.tasks.find_one({"id": task_id, "user_id": user["id"]})
        if not existing_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Build update data
        update_data = {}
        for field, value in task_update.dict(exclude_unset=True).items():
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
            await db.tasks.update_one(
                {"id": task_id, "user_id": user["id"]},
                {"$set": update_data}
            )
        
        # Return updated task
        updated_task = await db.tasks.find_one({"id": task_id, "user_id": user["id"]})
        return TaskResponse(**updated_task)
    
    @router.delete("/{task_id}")
    async def delete_task(request: Request, task_id: str):
        """Delete a task."""
        user = await get_current_user(request, db)
        
        result = await db.tasks.delete_one({"id": task_id, "user_id": user["id"]})
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        return {"message": "Task deleted successfully"}
    
    @router.get("/stats/summary")
    async def get_task_stats(request: Request):
        """Get task statistics for the current user."""
        user = await get_current_user(request, db)
        
        # Get all tasks for user
        tasks_cursor = db.tasks.find({"user_id": user["id"]})
        tasks = await tasks_cursor.to_list(1000)
        
        # Calculate stats
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t["status"] == "completed"])
        pending_tasks = len([t for t in tasks if t["status"] == "pending"])
        in_progress_tasks = len([t for t in tasks if t["status"] == "in-progress"])
        
        # Calculate overdue tasks
        now = datetime.now(timezone.utc)
        overdue_tasks = 0
        for task in tasks:
            if (task["status"] != "completed" and 
                task.get("due_date") and 
                task["due_date"] < now):
                overdue_tasks += 1
        
        completion_rate = round((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "in_progress_tasks": in_progress_tasks,
            "overdue_tasks": overdue_tasks,
            "completion_rate": completion_rate
        }
    
    return router