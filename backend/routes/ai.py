from fastapi import APIRouter, HTTPException, status, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone, timedelta
import os
import logging
import json
import re
from typing import List, Dict, Any
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables
load_dotenv()

try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    logging.warning("emergentintegrations not available, using mock responses")

from auth.dependencies import get_current_user
from models.tasks import Task

logger = logging.getLogger(__name__)

class NaturalTaskRequest(BaseModel):
    text: str

class TaskSuggestionResponse(BaseModel):
    suggestions: List[str]

class TaskSummaryResponse(BaseModel):
    summary: str
    stats: Dict[str, Any]

def create_ai_router(db: AsyncIOMotorDatabase) -> APIRouter:
    """Create AI router with database dependency injected."""
    
    router = APIRouter(prefix="/ai", tags=["ai-features"])
    
    def get_llm_chat():
        """Initialize LLM chat with GPT-5"""
        if not AI_AVAILABLE:
            return None
            
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            return None
            
        return LlmChat(
            api_key=api_key,
            session_id="smarttask-ai",
            system_message="You are a helpful task management assistant."
        ).with_model("openai", "gpt-5")
    
    def extract_date_from_text(text: str) -> datetime | None:
        """Extract due date from natural language text"""
        try:
            # Simple patterns for common date expressions
            text_lower = text.lower()
            now = datetime.now(timezone.utc)
            
            if "tomorrow" in text_lower:
                return now + timedelta(days=1)
            elif "next week" in text_lower:
                return now + timedelta(days=7)
            elif "next friday" in text_lower:
                days_until_friday = (4 - now.weekday() + 7) % 7
                if days_until_friday == 0:
                    days_until_friday = 7
                return now + timedelta(days=days_until_friday)
            elif "next monday" in text_lower:
                days_until_monday = (0 - now.weekday() + 7) % 7
                if days_until_monday == 0:
                    days_until_monday = 7
                return now + timedelta(days=days_until_monday)
            
            return None
        except Exception:
            return None
    
    def get_mock_task_data(text: str) -> Dict[str, Any]:
        """Generate mock task data when AI is unavailable"""
        # Extract basic info from text
        title = text.strip()
        if len(title) > 50:
            title = title[:50] + "..."
        
        # Determine priority from keywords
        priority = "medium"
        text_lower = text.lower()
        if any(word in text_lower for word in ["urgent", "asap", "important", "critical"]):
            priority = "high"
        elif any(word in text_lower for word in ["low", "when possible", "eventually"]):
            priority = "low"
        
        # Extract due date
        due_date = extract_date_from_text(text)
        
        return {
            "title": title,
            "description": text,
            "due_date": due_date.isoformat() if due_date else None,
            "priority": priority
        }
    
    @router.post("/parse-task")
    async def parse_natural_language_task(request: NaturalTaskRequest, req: Request):
        """Convert natural language text into structured task data"""
        
        # Get current user
        user = await get_current_user(req, db)
        
        try:
            chat = get_llm_chat()
            
            if chat:
                # AI-powered parsing
                prompt = f"""
                Parse the following natural language text into a structured task. Extract:
                - title: A concise task title (max 60 chars)
                - description: The full original text
                - due_date: ISO format date if mentioned, null if not
                - priority: "low", "medium", or "high" based on urgency words
                
                Text: "{request.text}"
                
                Respond ONLY with valid JSON in this exact format:
                {{
                    "title": "string",
                    "description": "string", 
                    "due_date": "2024-12-25T10:00:00Z" or null,
                    "priority": "low|medium|high"
                }}
                """
                
                user_message = UserMessage(text=prompt)
                response = await chat.send_message(user_message)
                
                # Parse AI response
                try:
                    task_data = json.loads(response.strip())
                    logger.info(f"AI parsed task successfully: {task_data}")
                except json.JSONDecodeError:
                    # Fallback to mock if AI response is malformed
                    task_data = get_mock_task_data(request.text)
                    logger.warning(f"AI response malformed, using mock data: {task_data}")
            else:
                # Use mock data when AI unavailable
                task_data = get_mock_task_data(request.text)
                logger.info(f"AI unavailable, using mock data: {task_data}")
            
            # Validate and create task
            task = Task(
                title=task_data["title"],
                description=task_data["description"],
                due_date=task_data.get("due_date"),
                priority=task_data.get("priority", "medium"),
                status="todo",
                user_id=user["id"]
            )
            
            # Save to database
            await db.tasks.insert_one(task.dict())
            
            return {
                "success": True,
                "task": task.dict(),
                "ai_used": chat is not None
            }
            
        except Exception as e:
            logger.error(f"Task parsing error: {str(e)}")
            # Emergency fallback
            task_data = get_mock_task_data(request.text)
            task = Task(
                title=task_data["title"],
                description=task_data["description"],
                priority=task_data.get("priority", "medium"),
                status="todo",
                user_id=user["id"]
            )
            
            await db.tasks.insert_one(task.dict())
            
            return {
                "success": True,
                "task": task.dict(),
                "ai_used": False,
                "fallback": True
            }
    
    @router.get("/suggestions", response_model=TaskSuggestionResponse)
    async def get_task_suggestions(req: Request):
        """Generate truly intelligent AI-powered suggestions based on user's actual tasks and projects content"""
        
        # Get current user
        user = await get_current_user(req, db)
        
        # Get user's tasks and projects with full details
        tasks = await db.tasks.find({"user_id": user["id"]}).to_list(length=None)
        projects = await db.projects.find({"user_id": user["id"]}).to_list(length=None)
        
        if not tasks and not projects:
            return TaskSuggestionResponse(suggestions=[
                "🚀 Welcome! Start by creating your first task - describe what you want to accomplish",
                "💡 Try: 'Plan marketing campaign for Q4' or 'Learn Python programming'",
                "📊 Create a project to group related tasks together",
                "🎯 I'll analyze your tasks and provide intelligent, personalized suggestions"
            ])
        
        try:
            chat = get_llm_chat()
            
            if not chat:
                logger.error("GPT-5 chat not available - check EMERGENT_LLM_KEY")
                return TaskSuggestionResponse(suggestions=[
                    "🤖 AI suggestions temporarily unavailable - check system configuration",
                    "📝 Meanwhile, try organizing tasks by priority: high, medium, low",
                    "⏰ Set specific deadlines for time-sensitive tasks",
                    "🎯 Break large tasks into smaller, actionable steps"
                ])
            
            # Prepare detailed context with actual task/project content
            detailed_context = []
            urgent_items = []
            task_domains = set()
            
            # Analyze tasks with content
            for task in tasks:
                status_emoji = "✅" if task.get("status") == "completed" else "🔄"
                priority = task.get('priority', 'medium')
                due_date_str = ""
                
                # Check urgency
                if task.get('due_date') and task.get('status') != 'completed':
                    try:
                        due_date = task['due_date']
                        if isinstance(due_date, str):
                            due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                        elif isinstance(due_date, datetime):
                            if due_date.tzinfo is None:
                                due_date = due_date.replace(tzinfo=timezone.utc)
                        
                        now = datetime.now(timezone.utc)
                        if due_date < now:
                            urgent_items.append(f"OVERDUE: {task['title']}")
                            due_date_str = " (OVERDUE)"
                        elif due_date.date() == now.date():
                            urgent_items.append(f"TODAY: {task['title']}")
                            due_date_str = " (DUE TODAY)"
                        else:
                            days_left = (due_date - now).days
                            if days_left <= 3:
                                due_date_str = f" (due in {days_left} days)"
                    except (ValueError, TypeError):
                        pass
                
                # Extract domain/category from task content
                task_content = f"{task.get('title', '')} {task.get('description', '')}".lower()
                for domain in ['marketing', 'development', 'design', 'finance', 'health', 'education', 'business', 'personal', 'research', 'writing']:
                    if domain in task_content:
                        task_domains.add(domain)
                
                detailed_context.append(
                    f"{status_emoji} [{priority.upper()}] {task['title']}{due_date_str}\n"
                    f"   Description: {task.get('description', 'No description')[:100]}"
                )
            
            # Analyze projects with content
            for project in projects:
                project_tasks = [t for t in tasks if t.get('project_id') == project.get('id')]
                completed_tasks = len([t for t in project_tasks if t.get('status') == 'completed'])
                total_project_tasks = len(project_tasks)
                
                progress = f"{completed_tasks}/{total_project_tasks} tasks" if total_project_tasks > 0 else "No tasks"
                
                detailed_context.append(
                    f"📂 PROJECT: {project.get('name', 'Untitled')}\n"
                    f"   Description: {project.get('description', 'No description')[:100]}\n"
                    f"   Progress: {progress}"
                )
            
            # Create intelligent analysis prompt
            prompt = f"""
            You are an AI productivity assistant with access to web resources. Analyze this user's specific tasks and projects to provide 4 highly intelligent, personalized suggestions.

            USER'S CURRENT WORK:
            {chr(10).join(detailed_context)}

            URGENT ITEMS:
            {chr(10).join(urgent_items) if urgent_items else "No urgent items"}

            DOMAINS DETECTED: {', '.join(task_domains) if task_domains else 'General productivity'}

            REQUIREMENTS:
            1. Analyze the ACTUAL CONTENT of tasks/projects, not just counts
            2. Address urgent items with specific advice
            3. Provide domain-specific suggestions based on task content
            4. Include helpful external resources (websites, tools, documents) when relevant
            5. Each suggestion must be actionable and specific to their situation

            FORMAT REQUIREMENTS:
            - Each suggestion starts with relevant emoji
            - 80-120 characters per suggestion
            - Include external resource links when applicable
            - Be specific about their actual tasks, not generic advice

            EXAMPLE GOOD SUGGESTIONS:
            "🚨 Focus on overdue 'Marketing Campaign' - use Canva templates: canva.com/templates"
            "📊 For 'Python Learning' project - start with Python.org official tutorial"
            "⚡ Break 'Website Design' into: wireframe → mockup → code → test phases"
            
            Return ONLY a JSON array of exactly 4 suggestion strings.
            """
            
            user_message = UserMessage(text=prompt)
            response = await chat.send_message(user_message)
            
            try:
                # Parse AI response
                suggestions = json.loads(response.strip())
                if isinstance(suggestions, list) and len(suggestions) >= 3:
                    logger.info(f"AI generated intelligent suggestions: {suggestions}")
                    return TaskSuggestionResponse(suggestions=suggestions[:4])
                else:
                    logger.warning(f"AI returned invalid format: {suggestions}")
            except json.JSONDecodeError as e:
                logger.error(f"AI returned malformed JSON: {response[:200]} | Error: {e}")
            
            # If AI fails, create intelligent fallback based on actual content
            intelligent_suggestions = []
            
            # Address urgent items first with specific advice
            if urgent_items:
                overdue_count = len([item for item in urgent_items if "OVERDUE" in item])
                today_count = len([item for item in urgent_items if "TODAY" in item])
                
                if overdue_count > 0:
                    overdue_task = urgent_items[0].replace("OVERDUE: ", "")
                    intelligent_suggestions.append(f"🚨 Tackle overdue '{overdue_task[:30]}...' - break into 25min focused sessions")
                
                if today_count > 0:
                    today_task = [item for item in urgent_items if "TODAY" in item][0].replace("TODAY: ", "")
                    intelligent_suggestions.append(f"⏰ Priority: '{today_task[:30]}...' - schedule specific time blocks today")
            
            # Domain-specific suggestions
            if 'marketing' in task_domains:
                intelligent_suggestions.append("📈 Marketing tasks detected - use Hootsuite.com for social media scheduling")
            elif 'development' in task_domains:
                intelligent_suggestions.append("💻 Coding projects found - try GitHub.com for version control and collaboration")
            elif 'design' in task_domains:
                intelligent_suggestions.append("🎨 Design work detected - check Figma.com for collaborative design tools")
            elif 'education' in task_domains or 'research' in task_domains:
                intelligent_suggestions.append("📚 Learning tasks found - use Khan Academy or Coursera for structured courses")
            
            # Project-specific advice
            projects_without_tasks = [p for p in projects if not any(t.get('project_id') == p.get('id') for t in tasks)]
            if projects_without_tasks:
                project_name = projects_without_tasks[0].get('name', 'your project')
                intelligent_suggestions.append(f"📂 Add specific tasks to '{project_name[:25]}...' project for better organization")
            
            # High-level productivity based on their patterns
            high_priority_tasks = [t for t in tasks if t.get('priority') == 'high' and t.get('status') != 'completed']
            if len(high_priority_tasks) > 3:
                intelligent_suggestions.append("⚡ Too many high-priority items - use Eisenhower Matrix: urgent vs important")
            elif len(tasks) > 10 and not projects:
                intelligent_suggestions.append("📊 Consider grouping your tasks into projects - try GTD methodology")
            else:
                completed_count = len([t for t in tasks if t.get('status') == 'completed'])
                if completed_count > 0:
                    intelligent_suggestions.append(f"🎉 Great momentum with {completed_count} completed tasks - maintain your rhythm!")
            
            # Ensure we have 4 suggestions
            while len(intelligent_suggestions) < 4:
                fallback_suggestions = [
                    "🎯 Use Pomodoro Technique (25min focus) - try Forest app for focus tracking",
                    "📅 Time-block your calendar - Google Calendar has built-in time insights",
                    "🔄 Review and adjust priorities weekly - Sunday planning sessions work well",
                    "📝 Capture ideas in a note-taking app - Notion or Obsidian for knowledge management"
                ]
                for suggestion in fallback_suggestions:
                    if suggestion not in intelligent_suggestions and len(intelligent_suggestions) < 4:
                        intelligent_suggestions.append(suggestion)
            
            return TaskSuggestionResponse(suggestions=intelligent_suggestions[:4])
            
        except Exception as e:
            logger.error(f"Intelligent suggestions error: {str(e)}")
            # Emergency fallback with task awareness
            task_count = len(tasks)
            project_count = len(projects)
            
            emergency_suggestions = []
            if task_count > 0:
                emergency_suggestions.append(f"📋 Focus on your {task_count} tasks - identify the most impactful one first")
                emergency_suggestions.append("🎯 Try timeboxing: allocate specific hours to specific tasks")
            
            if project_count > 0:
                emergency_suggestions.append(f"📂 Review your {project_count} projects - ensure each has clear next actions")
            
            emergency_suggestions.extend([
                "⚡ Use the 2-minute rule: do small tasks immediately",
                "📅 Block time in calendar for deep work - Calendly.com for scheduling",
                "🔄 Weekly review: assess progress and adjust priorities",
                "💡 Document lessons learned - use Notion.so for knowledge management"
            ])
            
            return TaskSuggestionResponse(suggestions=emergency_suggestions[:4])
    
    @router.get("/summary", response_model=TaskSummaryResponse)
    async def get_task_summary(req: Request):
        """Generate an AI-powered summary of user's tasks and projects"""
        
        # Get current user
        user = await get_current_user(req, db)
        
        # Get user's tasks and projects
        tasks = await db.tasks.find({"user_id": user["id"]}).to_list(length=None)
        projects = await db.projects.find({"user_id": user["id"]}).to_list(length=None)
        
        # Calculate comprehensive stats
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.get('status') == 'completed'])
        pending_tasks = total_tasks - completed_tasks
        
        overdue_tasks = 0
        today_tasks = 0
        for t in tasks:
            if t.get('due_date') and t.get('status') != 'completed':
                try:
                    due_date = t['due_date']
                    if isinstance(due_date, str):
                        due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                    elif isinstance(due_date, datetime):
                        if due_date.tzinfo is None:
                            due_date = due_date.replace(tzinfo=timezone.utc)
                    
                    now = datetime.now(timezone.utc)
                    if due_date < now:
                        overdue_tasks += 1
                    elif due_date.date() == now.date():
                        today_tasks += 1
                except (ValueError, TypeError):
                    continue
        
        high_priority_tasks = len([t for t in tasks if t.get('priority') == 'high' and t.get('status') != 'completed'])
        
        # Project-related stats
        total_projects = len(projects)
        active_projects = len([p for p in projects if p.get('status') != 'completed'])
        projects_with_tasks = 0
        for project in projects:
            project_tasks = [t for t in tasks if t.get('project_id') == project['id']]
            if project_tasks:
                projects_with_tasks += 1
        
        stats = {
            "total": total_tasks,
            "completed": completed_tasks,
            "pending": pending_tasks,
            "overdue": overdue_tasks,
            "today": today_tasks,
            "high_priority": high_priority_tasks,
            "projects_total": total_projects,
            "projects_active": active_projects,
            "projects_with_tasks": projects_with_tasks
        }
        
        if total_tasks == 0 and total_projects == 0:
            return TaskSummaryResponse(
                summary="🎯 Ready to start! Create your first task or project to begin organizing your work.",
                stats=stats
            )
        
        try:
            chat = get_llm_chat()
            
            if chat:
                # Create comprehensive context for AI
                context_parts = []
                
                # Task context
                if total_tasks > 0:
                    completion_rate = (completed_tasks / total_tasks) * 100
                    context_parts.append(f"Tasks: {total_tasks} total, {completed_tasks} completed ({completion_rate:.0f}% completion rate)")
                    
                    if overdue_tasks > 0:
                        context_parts.append(f"{overdue_tasks} tasks are overdue")
                    if today_tasks > 0:
                        context_parts.append(f"{today_tasks} tasks due today")
                    if high_priority_tasks > 0:
                        context_parts.append(f"{high_priority_tasks} high priority tasks pending")
                
                # Project context
                if total_projects > 0:
                    context_parts.append(f"Projects: {total_projects} total, {active_projects} active")
                    if projects_with_tasks < total_projects:
                        empty_projects = total_projects - projects_with_tasks
                        context_parts.append(f"{empty_projects} projects have no tasks assigned")
                
                prompt = f"""
                Create a personalized, motivational summary based on this user's current situation:
                
                {chr(10).join(context_parts)}
                
                Write 2-3 sentences that:
                - Acknowledge their progress and current state
                - Highlight any urgent items (overdue, today's tasks)
                - Provide encouragement and next steps
                - Include relevant emojis
                - Keep it under 150 characters total
                
                Be specific to their actual situation, not generic.
                """
                
                user_message = UserMessage(text=prompt)
                response = await chat.send_message(user_message)
                
                summary = response.strip()
                if len(summary) > 200:
                    summary = summary[:150] + "..."
                
                return TaskSummaryResponse(summary=summary, stats=stats)
            
            # Enhanced intelligent fallback summary
            summary_parts = []
            
            # Progress acknowledgment
            if completed_tasks > 0:
                completion_rate = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
                if completion_rate >= 75:
                    summary_parts.append(f"🎉 Outstanding! {completion_rate:.0f}% completion rate")
                elif completion_rate >= 50:
                    summary_parts.append(f"💪 Great progress! {completion_rate:.0f}% tasks completed")
                else:
                    summary_parts.append(f"🚀 Building momentum with {completed_tasks} tasks done")
            
            # Urgent items first
            if overdue_tasks > 0:
                summary_parts.append(f"🚨 {overdue_tasks} overdue task{'s' if overdue_tasks != 1 else ''} need attention")
            elif today_tasks > 0:
                summary_parts.append(f"⏰ {today_tasks} task{'s' if today_tasks != 1 else ''} due today")
            elif high_priority_tasks > 0:
                summary_parts.append(f"⚡ {high_priority_tasks} high priority task{'s' if high_priority_tasks != 1 else ''} to focus on")
            
            # Project status
            if total_projects > 0:
                if projects_with_tasks < total_projects:
                    empty_projects = total_projects - projects_with_tasks
                    summary_parts.append(f"📂 {empty_projects} project{'s' if empty_projects != 1 else ''} ready for tasks")
                elif active_projects > 0:
                    summary_parts.append(f"📊 {active_projects} active project{'s' if active_projects != 1 else ''} in progress")
            
            # Encouragement
            if not summary_parts:
                if total_tasks > 0:
                    summary_parts.append("🎯 Ready to tackle your tasks!")
                else:
                    summary_parts.append("🚀 Time to create your first task!")
            
            # Combine with appropriate connectors
            if len(summary_parts) == 1:
                summary = summary_parts[0]
            elif len(summary_parts) == 2:
                summary = f"{summary_parts[0]}. {summary_parts[1]}."
            else:
                summary = f"{summary_parts[0]}. {summary_parts[1]}. Keep it up! 💪"
            
            return TaskSummaryResponse(summary=summary, stats=stats)
            
        except Exception as e:
            logger.error(f"Enhanced summary error: {str(e)}")
            # Ultimate fallback
            if total_tasks > 0:
                summary = f"📊 {pending_tasks} pending tasks out of {total_tasks} total"
                if total_projects > 0:
                    summary += f" across {total_projects} projects"
                summary += ". Keep going! 💪"
            else:
                summary = "🎯 Ready to start your productivity journey!"
                
            return TaskSummaryResponse(summary=summary, stats=stats)
    
    return router