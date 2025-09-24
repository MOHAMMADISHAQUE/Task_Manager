from datetime import datetime, timedelta
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Sample data to make the app look appealing
def generate_sample_data(user_id: str):
    """Generate sample tasks and projects for a user."""
    
    # Sample projects
    projects = [
        {
            "id": str(uuid.uuid4()),
            "name": "Website Redesign",
            "description": "Complete overhaul of company website with modern design and improved UX",
            "status": "active",
            "priority": "high",
            "progress": 75,
            "due_date": datetime.utcnow() + timedelta(days=14),
            "user_id": user_id,
            "team_members": ["John Smith", "Sarah Johnson", "Mike Chen"],
            "created_at": datetime.utcnow() - timedelta(days=21),
            "updated_at": datetime.utcnow() - timedelta(days=2)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Mobile App Development",
            "description": "Cross-platform mobile application for task management and productivity",
            "status": "active",
            "priority": "medium",
            "progress": 45,
            "due_date": datetime.utcnow() + timedelta(days=45),
            "user_id": user_id,
            "team_members": ["Emily Davis", "David Wilson"],
            "created_at": datetime.utcnow() - timedelta(days=30),
            "updated_at": datetime.utcnow() - timedelta(days=1)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Marketing Campaign Q4",
            "description": "Launch comprehensive marketing campaign for Q4 product releases",
            "status": "planning",
            "priority": "medium",
            "progress": 15,
            "due_date": datetime.utcnow() + timedelta(days=60),
            "user_id": user_id,
            "team_members": ["Lisa Thompson", "Tom Anderson", "Alex Rodriguez"],
            "created_at": datetime.utcnow() - timedelta(days=7),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "API Documentation",
            "description": "Comprehensive documentation for all API endpoints and developer resources",
            "status": "completed",
            "priority": "low",
            "progress": 100,
            "due_date": datetime.utcnow() - timedelta(days=5),
            "user_id": user_id,
            "team_members": ["Mike Chen"],
            "created_at": datetime.utcnow() - timedelta(days=20),
            "updated_at": datetime.utcnow() - timedelta(days=3)
        }
    ]
    
    # Sample tasks
    tasks = [
        {
            "id": str(uuid.uuid4()),
            "title": "Design new landing page",
            "description": "Create a modern, responsive landing page with improved conversion rates",
            "status": "in-progress",
            "priority": "high",
            "due_date": datetime.utcnow() + timedelta(days=3),
            "user_id": user_id,
            "project_id": projects[0]["id"],
            "tags": ["design", "frontend", "landing"],
            "created_at": datetime.utcnow() - timedelta(days=5),
            "updated_at": datetime.utcnow() - timedelta(hours=2)
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Implement user authentication",
            "description": "Set up secure user authentication system with JWT tokens and session management",
            "status": "completed",
            "priority": "high",
            "due_date": datetime.utcnow() - timedelta(days=2),
            "user_id": user_id,
            "project_id": projects[0]["id"],
            "tags": ["backend", "security", "auth"],
            "created_at": datetime.utcnow() - timedelta(days=10),
            "updated_at": datetime.utcnow() - timedelta(days=1)
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Mobile UI wireframes",
            "description": "Create detailed wireframes for all mobile app screens and user flows",
            "status": "pending",
            "priority": "medium",
            "due_date": datetime.utcnow() + timedelta(days=7),
            "user_id": user_id,
            "project_id": projects[1]["id"],
            "tags": ["design", "mobile", "wireframes"],
            "created_at": datetime.utcnow() - timedelta(days=3),
            "updated_at": datetime.utcnow() - timedelta(days=3)
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Database optimization",
            "description": "Optimize database queries and improve performance for user data operations",
            "status": "in-progress",
            "priority": "medium",
            "due_date": datetime.utcnow() + timedelta(days=10),
            "user_id": user_id,
            "project_id": projects[0]["id"],
            "tags": ["backend", "database", "performance"],
            "created_at": datetime.utcnow() - timedelta(days=8),
            "updated_at": datetime.utcnow() - timedelta(hours=6)
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Social media content calendar",
            "description": "Develop content calendar for social media posts across all platforms",
            "status": "pending",
            "priority": "medium",
            "due_date": datetime.utcnow() + timedelta(days=12),
            "user_id": user_id,
            "project_id": projects[2]["id"],
            "tags": ["marketing", "social media", "content"],
            "created_at": datetime.utcnow() - timedelta(days=2),
            "updated_at": datetime.utcnow() - timedelta(days=2)
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Code review and testing",
            "description": "Comprehensive code review and unit testing for recent feature implementations",
            "status": "pending",
            "priority": "high",
            "due_date": datetime.utcnow() + timedelta(days=5),
            "user_id": user_id,
            "project_id": projects[0]["id"],
            "tags": ["testing", "code review", "quality assurance"],
            "created_at": datetime.utcnow() - timedelta(days=1),
            "updated_at": datetime.utcnow() - timedelta(days=1)
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Client presentation preparation",
            "description": "Prepare presentation materials for upcoming client meeting and product demo",
            "status": "in-progress",
            "priority": "high",
            "due_date": datetime.utcnow() + timedelta(days=2),
            "user_id": user_id,
            "project_id": None,
            "tags": ["presentation", "client", "demo"],
            "created_at": datetime.utcnow() - timedelta(hours=12),
            "updated_at": datetime.utcnow() - timedelta(hours=1)
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Team meeting notes review",
            "description": "Review and organize notes from weekly team meetings and action items",
            "status": "completed",
            "priority": "low",
            "due_date": datetime.utcnow() - timedelta(days=1),
            "user_id": user_id,
            "project_id": None,
            "tags": ["meetings", "notes", "organization"],
            "created_at": datetime.utcnow() - timedelta(days=4),
            "updated_at": datetime.utcnow() - timedelta(hours=8)
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Update project documentation",
            "description": "Update all project documentation with latest changes and requirements",
            "status": "pending",
            "priority": "low",
            "due_date": datetime.utcnow() + timedelta(days=15),
            "user_id": user_id,
            "project_id": projects[3]["id"],
            "tags": ["documentation", "updates", "maintenance"],
            "created_at": datetime.utcnow() - timedelta(hours=6),
            "updated_at": datetime.utcnow() - timedelta(hours=6)
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Security audit checklist",
            "description": "Complete comprehensive security audit using industry best practices checklist",
            "status": "pending",
            "priority": "high",
            "due_date": datetime.utcnow() + timedelta(days=8),
            "user_id": user_id,
            "project_id": None,
            "tags": ["security", "audit", "checklist"],
            "created_at": datetime.utcnow() - timedelta(hours=3),
            "updated_at": datetime.utcnow() - timedelta(hours=3)
        }
    ]
    
    return projects, tasks

async def seed_user_data(user_id: str):
    """Add sample data for a specific user."""
    # MongoDB connection
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        # Check if user already has data
        existing_tasks = await db.tasks.count_documents({"user_id": user_id})
        if existing_tasks > 0:
            print(f"User {user_id} already has {existing_tasks} tasks, skipping seed data")
            return
        
        # Generate sample data
        projects, tasks = generate_sample_data(user_id)
        
        # Insert projects
        if projects:
            await db.projects.insert_many(projects)
            print(f"Inserted {len(projects)} sample projects for user {user_id}")
        
        # Insert tasks
        if tasks:
            await db.tasks.insert_many(tasks)
            print(f"Inserted {len(tasks)} sample tasks for user {user_id}")
            
    except Exception as e:
        print(f"Error seeding data for user {user_id}: {e}")
    finally:
        client.close()

# Function to be called when a new user signs up
async def initialize_new_user(user_id: str):
    """Initialize a new user with sample data."""
    await seed_user_data(user_id)