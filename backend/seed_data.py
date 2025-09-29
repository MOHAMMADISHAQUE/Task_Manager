from datetime import datetime, timedelta
import uuid
import random
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Sample data pools for personalization
PROJECT_TEMPLATES = [
    # Tech/Development Projects
    {
        "name": "Website Redesign", 
        "description": "Complete overhaul of company website with modern design and improved UX",
        "category": "tech"
    },
    {
        "name": "Mobile App Development", 
        "description": "Cross-platform mobile application for task management and productivity",
        "category": "tech"
    },
    {
        "name": "API Documentation", 
        "description": "Comprehensive documentation for all API endpoints and developer resources",
        "category": "tech"
    },
    {
        "name": "E-commerce Integration", 
        "description": "Integrate payment processing and inventory management systems",
        "category": "tech"
    },
    # Business/Marketing Projects
    {
        "name": "Marketing Campaign Q4", 
        "description": "Launch comprehensive marketing campaign for Q4 product releases",
        "category": "business"
    },
    {
        "name": "Brand Identity Refresh", 
        "description": "Update brand guidelines, logos, and marketing materials",
        "category": "business"
    },
    {
        "name": "Customer Onboarding", 
        "description": "Improve customer onboarding process and reduce churn rate",
        "category": "business"
    },
    # Personal Projects
    {
        "name": "Home Office Setup", 
        "description": "Design and organize productive home office workspace",
        "category": "personal"
    },
    {
        "name": "Fitness Challenge", 
        "description": "30-day fitness and wellness improvement program",
        "category": "personal"
    },
    {
        "name": "Skill Development", 
        "description": "Learn new professional skills and earn certifications",
        "category": "personal"
    }
]

TASK_TEMPLATES = [
    # Tech Tasks
    {"title": "Design new landing page", "description": "Create a modern, responsive landing page with improved conversion rates", "category": "tech", "priority": "high"},
    {"title": "Implement user authentication", "description": "Set up secure user authentication system with JWT tokens", "category": "tech", "priority": "high"},
    {"title": "Database optimization", "description": "Optimize database queries and improve performance", "category": "tech", "priority": "medium"},
    {"title": "Code review and testing", "description": "Comprehensive code review and unit testing", "category": "tech", "priority": "high"},
    {"title": "API rate limiting", "description": "Implement rate limiting for API endpoints", "category": "tech", "priority": "high"},
    {"title": "Security audit", "description": "Complete security audit using best practices", "category": "tech", "priority": "high"},
    
    # Business Tasks
    {"title": "Social media content calendar", "description": "Develop content calendar for social media posts", "category": "business", "priority": "medium"},
    {"title": "Client presentation preparation", "description": "Prepare presentation materials for client meeting", "category": "business", "priority": "high"},
    {"title": "Market research analysis", "description": "Analyze competitor strategies and market trends", "category": "business", "priority": "medium"},
    {"title": "Budget planning review", "description": "Review and optimize quarterly budget allocation", "category": "business", "priority": "medium"},
    
    # Personal Tasks
    {"title": "Organize workspace", "description": "Declutter and organize home office for better productivity", "category": "personal", "priority": "low"},
    {"title": "Exercise routine", "description": "Establish consistent daily exercise routine", "category": "personal", "priority": "medium"},
    {"title": "Read industry articles", "description": "Stay updated with latest industry trends and news", "category": "personal", "priority": "low"},
    {"title": "Network with colleagues", "description": "Schedule coffee chats with industry contacts", "category": "personal", "priority": "low"},
]

def generate_personalized_sample_data(user_id: str, user_name: str = None):
    """Generate personalized sample tasks and projects for a user."""
    
    # Randomly select project templates (3-5 projects)
    num_projects = random.randint(3, 5)
    selected_project_templates = random.sample(PROJECT_TEMPLATES, min(num_projects, len(PROJECT_TEMPLATES)))
    
    projects = []
    for i, template in enumerate(selected_project_templates):
        # Randomize project details
        progress = random.randint(0, 100) if template["category"] != "personal" else random.randint(0, 80)
        
        # Random status based on progress
        if progress >= 100:
            status = "completed"
        elif progress >= 70:
            status = "active"
        elif progress >= 30:
            status = "active"
        else:
            status = "planning" if random.random() > 0.5 else "active"
        
        # Random priority
        priority = random.choice(["high", "medium", "low"])
        if template["category"] == "tech":
            priority = random.choice(["high", "medium"])  # Tech projects tend to be higher priority
        
        # Random due date (1-60 days from now)
        days_ahead = random.randint(7, 60)
        if status == "completed":
            days_ahead = random.randint(-10, -1)  # Completed projects have past due dates
        
        project = {
            "id": str(uuid.uuid4()),
            "name": template["name"],
            "description": template["description"],
            "status": status,
            "priority": priority,
            "progress": progress,
            "due_date": datetime.utcnow() + timedelta(days=days_ahead),
            "user_id": user_id,
            "team_members": generate_random_team_members(user_name),
            "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            "updated_at": datetime.utcnow() - timedelta(hours=random.randint(1, 72))
        }
        projects.append(project)
    
    # Generate tasks (8-15 tasks)
    num_tasks = random.randint(8, 15)
    
    # Select task templates
    selected_task_templates = random.choices(TASK_TEMPLATES, k=num_tasks)
    
    tasks = []
    for i, template in enumerate(selected_task_templates):
        # Random status
        status = random.choice(["pending", "in-progress", "completed"])
        
        # Assign to project (70% chance) or keep as standalone
        project_id = None
        if random.random() < 0.7 and projects:
            # Try to match category
            matching_projects = [p for p in projects if template["category"] in p["name"].lower() or template["category"] in p["description"].lower()]
            if matching_projects:
                project_id = random.choice(matching_projects)["id"]
            else:
                project_id = random.choice(projects)["id"]
        
        # Random due date
        if status == "completed":
            days_ahead = random.randint(-10, -1)
        else:
            days_ahead = random.randint(1, 30)
        
        # Generate realistic tags
        tags = generate_task_tags(template["category"], template["title"])
        
        task = {
            "id": str(uuid.uuid4()),
            "title": template["title"],
            "description": template["description"],
            "status": status,
            "priority": template["priority"],
            "due_date": datetime.utcnow() + timedelta(days=days_ahead),
            "user_id": user_id,
            "project_id": project_id,
            "tags": tags,
            "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 20)),
            "updated_at": datetime.utcnow() - timedelta(hours=random.randint(1, 48))
        }
        tasks.append(task)
    
    return projects, tasks

def generate_random_team_members(user_name: str = None):
    """Generate random team member names."""
    names = [
        "Alex Johnson", "Sarah Chen", "Mike Rodriguez", "Emily Davis", 
        "David Wilson", "Lisa Thompson", "Tom Anderson", "Maria Garcia",
        "James Brown", "Anna Lee", "Chris Taylor", "Jessica Wang"
    ]
    
    # Include user name if provided
    if user_name and user_name not in names:
        names.append(user_name)
    
    # Return 1-3 random team members
    return random.sample(names, random.randint(1, min(3, len(names))))

def generate_task_tags(category: str, title: str):
    """Generate relevant tags for tasks."""
    tag_pools = {
        "tech": ["frontend", "backend", "api", "database", "security", "testing", "deployment", "optimization"],
        "business": ["marketing", "strategy", "analysis", "planning", "client", "sales", "budget"],
        "personal": ["productivity", "learning", "organization", "health", "networking", "skills"]
    }
    
    base_tags = tag_pools.get(category, ["general"])
    
    # Add specific tags based on title keywords
    title_lower = title.lower()
    specific_tags = []
    
    if "design" in title_lower:
        specific_tags.append("design")
    if "auth" in title_lower or "login" in title_lower:
        specific_tags.append("authentication")
    if "database" in title_lower or "db" in title_lower:
        specific_tags.append("database")
    if "api" in title_lower:
        specific_tags.append("api")
    if "security" in title_lower:
        specific_tags.append("security")
    if "mobile" in title_lower:
        specific_tags.append("mobile")
    if "social" in title_lower:
        specific_tags.append("social media")
    
    # Combine and return 2-4 tags
    all_tags = list(set(base_tags + specific_tags))
    return random.sample(all_tags, min(random.randint(2, 4), len(all_tags)))

# Keep the old function for backward compatibility
def generate_sample_data(user_id: str):
    
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
        },
        {
            "id": str(uuid.uuid4()),
            "name": "E-commerce Integration",
            "description": "Integrate payment processing and inventory management systems",
            "status": "active",
            "priority": "high",
            "progress": 60,
            "due_date": datetime.utcnow() + timedelta(days=30),
            "user_id": user_id,
            "team_members": ["Sarah Johnson", "John Smith"],
            "created_at": datetime.utcnow() - timedelta(days=15),
            "updated_at": datetime.utcnow() - timedelta(hours=4)
        }
    ]
    
    # Sample tasks - more comprehensive and appealing
    tasks = [
        {
            "id": str(uuid.uuid4()),
            "title": "Design new landing page",
            "description": "Create a modern, responsive landing page with improved conversion rates and A/B testing capabilities",
            "status": "in-progress",
            "priority": "high",
            "due_date": datetime.utcnow() + timedelta(days=3),
            "user_id": user_id,
            "project_id": projects[0]["id"],
            "tags": ["design", "frontend", "landing", "conversion"],
            "created_at": datetime.utcnow() - timedelta(days=5),
            "updated_at": datetime.utcnow() - timedelta(hours=2)
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Implement user authentication",
            "description": "Set up secure user authentication system with JWT tokens, session management, and password reset functionality",
            "status": "completed",
            "priority": "high",
            "due_date": datetime.utcnow() - timedelta(days=2),
            "user_id": user_id,
            "project_id": projects[0]["id"],
            "tags": ["backend", "security", "auth", "jwt"],
            "created_at": datetime.utcnow() - timedelta(days=10),
            "updated_at": datetime.utcnow() - timedelta(days=1)
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Mobile UI wireframes",
            "description": "Create detailed wireframes for all mobile app screens including user onboarding, dashboard, and settings",
            "status": "pending",
            "priority": "medium",
            "due_date": datetime.utcnow() + timedelta(days=7),
            "user_id": user_id,
            "project_id": projects[1]["id"],
            "tags": ["design", "mobile", "wireframes", "ux"],
            "created_at": datetime.utcnow() - timedelta(days=3),
            "updated_at": datetime.utcnow() - timedelta(days=3)
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Database optimization",
            "description": "Optimize database queries, add indexes, and improve performance for user data operations and analytics",
            "status": "in-progress",
            "priority": "medium",
            "due_date": datetime.utcnow() + timedelta(days=10),
            "user_id": user_id,
            "project_id": projects[0]["id"],
            "tags": ["backend", "database", "performance", "optimization"],
            "created_at": datetime.utcnow() - timedelta(days=8),
            "updated_at": datetime.utcnow() - timedelta(hours=6)
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Social media content calendar",
            "description": "Develop comprehensive content calendar for social media posts across LinkedIn, Twitter, and Instagram",
            "status": "pending",
            "priority": "medium",
            "due_date": datetime.utcnow() + timedelta(days=12),
            "user_id": user_id,
            "project_id": projects[2]["id"],
            "tags": ["marketing", "social media", "content", "strategy"],
            "created_at": datetime.utcnow() - timedelta(days=2),
            "updated_at": datetime.utcnow() - timedelta(days=2)
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Code review and testing",
            "description": "Comprehensive code review, unit testing, and integration testing for recent feature implementations",
            "status": "pending",
            "priority": "high",
            "due_date": datetime.utcnow() + timedelta(days=5),
            "user_id": user_id,
            "project_id": projects[0]["id"],
            "tags": ["testing", "code review", "quality assurance", "ci/cd"],
            "created_at": datetime.utcnow() - timedelta(days=1),
            "updated_at": datetime.utcnow() - timedelta(days=1)
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Client presentation preparation",
            "description": "Prepare presentation materials for upcoming client meeting including product demo and roadmap",
            "status": "in-progress",
            "priority": "high",
            "due_date": datetime.utcnow() + timedelta(days=2),
            "user_id": user_id,
            "project_id": None,
            "tags": ["presentation", "client", "demo", "roadmap"],
            "created_at": datetime.utcnow() - timedelta(hours=12),
            "updated_at": datetime.utcnow() - timedelta(hours=1)
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Team meeting notes review",
            "description": "Review and organize notes from weekly team meetings, create action items and follow-up tasks",
            "status": "completed",
            "priority": "low",
            "due_date": datetime.utcnow() - timedelta(days=1),
            "user_id": user_id,
            "project_id": None,
            "tags": ["meetings", "notes", "organization", "follow-up"],
            "created_at": datetime.utcnow() - timedelta(days=4),
            "updated_at": datetime.utcnow() - timedelta(hours=8)
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Update project documentation",
            "description": "Update all project documentation with latest changes, API specifications, and deployment guides",
            "status": "pending",
            "priority": "low",
            "due_date": datetime.utcnow() + timedelta(days=15),
            "user_id": user_id,
            "project_id": projects[3]["id"],
            "tags": ["documentation", "updates", "maintenance", "api"],
            "created_at": datetime.utcnow() - timedelta(hours=6),
            "updated_at": datetime.utcnow() - timedelta(hours=6)
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Security audit checklist",
            "description": "Complete comprehensive security audit using industry best practices and compliance checklist",
            "status": "pending",
            "priority": "high",
            "due_date": datetime.utcnow() + timedelta(days=8),
            "user_id": user_id,
            "project_id": None,
            "tags": ["security", "audit", "checklist", "compliance"],
            "created_at": datetime.utcnow() - timedelta(hours=3),
            "updated_at": datetime.utcnow() - timedelta(hours=3)
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Payment gateway integration",
            "description": "Implement Stripe payment processing with webhook handling and subscription management",
            "status": "in-progress",
            "priority": "high",
            "due_date": datetime.utcnow() + timedelta(days=14),
            "user_id": user_id,
            "project_id": projects[4]["id"],
            "tags": ["payments", "stripe", "webhooks", "subscriptions"],
            "created_at": datetime.utcnow() - timedelta(days=6),
            "updated_at": datetime.utcnow() - timedelta(hours=3)
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Inventory management system",
            "description": "Build automated inventory tracking with real-time stock updates and low stock alerts",
            "status": "pending",
            "priority": "medium",
            "due_date": datetime.utcnow() + timedelta(days=25),
            "user_id": user_id,
            "project_id": projects[4]["id"],
            "tags": ["inventory", "automation", "alerts", "tracking"],
            "created_at": datetime.utcnow() - timedelta(days=4),
            "updated_at": datetime.utcnow() - timedelta(days=4)
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Email campaign setup",
            "description": "Create automated email sequences for user onboarding, feature announcements, and retention",
            "status": "pending",
            "priority": "medium",
            "due_date": datetime.utcnow() + timedelta(days=18),
            "user_id": user_id,
            "project_id": projects[2]["id"],
            "tags": ["email", "automation", "onboarding", "retention"],
            "created_at": datetime.utcnow() - timedelta(days=2),
            "updated_at": datetime.utcnow() - timedelta(days=2)
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Performance monitoring setup",
            "description": "Implement application performance monitoring with alerts and error tracking using Sentry",
            "status": "completed",
            "priority": "medium",
            "due_date": datetime.utcnow() - timedelta(days=3),
            "user_id": user_id,
            "project_id": None,
            "tags": ["monitoring", "performance", "sentry", "alerts"],
            "created_at": datetime.utcnow() - timedelta(days=9),
            "updated_at": datetime.utcnow() - timedelta(days=2)
        },
        {
            "id": str(uuid.uuid4()),
            "title": "User analytics dashboard",
            "description": "Create comprehensive analytics dashboard showing user engagement, feature usage, and conversion metrics",
            "status": "in-progress",
            "priority": "medium",
            "due_date": datetime.utcnow() + timedelta(days=20),
            "user_id": user_id,
            "project_id": projects[1]["id"],
            "tags": ["analytics", "dashboard", "metrics", "engagement"],
            "created_at": datetime.utcnow() - timedelta(days=7),
            "updated_at": datetime.utcnow() - timedelta(hours=5)
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Dark mode implementation",
            "description": "Implement dark theme across the entire application with user preference persistence",
            "status": "pending",
            "priority": "low",
            "due_date": datetime.utcnow() + timedelta(days=30),
            "user_id": user_id,
            "project_id": projects[0]["id"],
            "tags": ["ui", "dark mode", "theme", "accessibility"],
            "created_at": datetime.utcnow() - timedelta(hours=18),
            "updated_at": datetime.utcnow() - timedelta(hours=18)
        },
        {
            "id": str(uuid.uuid4()),
            "title": "API rate limiting",
            "description": "Implement rate limiting and throttling for API endpoints to prevent abuse and ensure fair usage",
            "status": "pending",
            "priority": "high",
            "due_date": datetime.utcnow() + timedelta(days=6),
            "user_id": user_id,
            "project_id": None,
            "tags": ["api", "rate limiting", "security", "throttling"],
            "created_at": datetime.utcnow() - timedelta(hours=8),
            "updated_at": datetime.utcnow() - timedelta(hours=8)
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Backup and recovery system",
            "description": "Set up automated database backups with point-in-time recovery and disaster recovery procedures",
            "status": "pending",
            "priority": "high",
            "due_date": datetime.utcnow() + timedelta(days=11),
            "user_id": user_id,
            "project_id": None,
            "tags": ["backup", "recovery", "database", "disaster recovery"],
            "created_at": datetime.utcnow() - timedelta(hours=4),
            "updated_at": datetime.utcnow() - timedelta(hours=4)
        },
        {
            "id": str(uuid.uuid4()),
            "title": "User feedback collection",
            "description": "Implement in-app feedback system with rating, comments, and feature request functionality",
            "status": "completed",
            "priority": "low",
            "due_date": datetime.utcnow() - timedelta(days=8),
            "user_id": user_id,
            "project_id": projects[1]["id"],
            "tags": ["feedback", "user experience", "ratings", "features"],
            "created_at": datetime.utcnow() - timedelta(days=14),
            "updated_at": datetime.utcnow() - timedelta(days=6)
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Notification system",
            "description": "Build real-time notification system with push notifications, email alerts, and in-app messages",
            "status": "in-progress",
            "priority": "medium",
            "due_date": datetime.utcnow() + timedelta(days=16),
            "user_id": user_id,
            "project_id": projects[1]["id"],
            "tags": ["notifications", "real-time", "push", "alerts"],
            "created_at": datetime.utcnow() - timedelta(days=5),
            "updated_at": datetime.utcnow() - timedelta(hours=1)
        }
    ]
    
    return projects, tasks

async def seed_user_data(user_id: str, user_name: str = None, use_sample_data: bool = False):
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
        
        # Only add sample data if requested
        if use_sample_data:
            # Generate personalized sample data
            projects, tasks = generate_personalized_sample_data(user_id, user_name)
            
            # Insert projects
            if projects:
                await db.projects.insert_many(projects)
                print(f"Inserted {len(projects)} personalized sample projects for user {user_id}")
            
            # Insert tasks
            if tasks:
                await db.tasks.insert_many(tasks)
                print(f"Inserted {len(tasks)} personalized sample tasks for user {user_id}")
        else:
            print(f"User {user_id} chose to start with clean workspace")
            
    except Exception as e:
        print(f"Error seeding data for user {user_id}: {e}")
    finally:
        client.close()

# Function to be called when a new user signs up
async def initialize_new_user(user_id: str, user_name: str = None, use_sample_data: bool = False):
    """Initialize a new user with optional sample data."""
    await seed_user_data(user_id, user_name, use_sample_data)