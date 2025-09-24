from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = ""
    status: str = "pending"  # pending, in-progress, completed
    priority: str = "medium"  # low, medium, high
    due_date: Optional[datetime] = None
    user_id: str
    project_id: Optional[str] = None
    tags: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = ""
    status: str = "active"  # planning, active, completed, on-hold
    priority: str = "medium"  # low, medium, high
    progress: int = 0  # 0-100
    due_date: Optional[datetime] = None
    user_id: str
    team_members: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Request/Response Models
class TaskCreateRequest(BaseModel):
    title: str
    description: Optional[str] = ""
    priority: str = "medium"
    due_date: Optional[str] = None
    project_id: Optional[str] = None
    tags: List[str] = []

class TaskUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[str] = None
    project_id: Optional[str] = None
    tags: Optional[List[str]] = None

class ProjectCreateRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    priority: str = "medium"
    due_date: Optional[str] = None
    team_members: List[str] = []

class ProjectUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    progress: Optional[int] = None
    due_date: Optional[str] = None
    team_members: Optional[List[str]] = None

class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    status: str
    priority: str
    due_date: Optional[datetime]
    user_id: str
    project_id: Optional[str]
    tags: List[str]
    created_at: datetime
    updated_at: datetime

class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str
    status: str
    priority: str
    progress: int
    due_date: Optional[datetime]
    user_id: str
    team_members: List[str]
    tasks_count: int = 0
    created_at: datetime
    updated_at: datetime