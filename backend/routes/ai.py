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
        """Generate AI-powered task suggestions based on user's current tasks and projects"""
        
        # Get current user
        user = await get_current_user(req, db)
        
        # Get user's tasks and projects
        tasks = await db.tasks.find({"user_id": user["id"]}).to_list(length=None)
        projects = await db.projects.find({"user_id": user["id"]}).to_list(length=None)
        
        if not tasks and not projects:
            return TaskSuggestionResponse(suggestions=[
                "🚀 Welcome! Start by creating your first task or project",
                "💡 Try using natural language: 'Remind me to call mom tomorrow'",
                "📊 Create a project to organize related tasks together",
                "📅 Set due dates to stay organized and on track"
            ])
        
        try:
            chat = get_llm_chat()
            
            if chat:
                # Prepare comprehensive data for AI
                context_data = []
                
                # Add project context
                for project in projects:
                    project_tasks = [t for t in tasks if t.get('project_id') == project['id']]
                    completed_tasks = len([t for t in project_tasks if t.get('status') == 'completed'])
                    total_tasks = len(project_tasks)
                    progress = f"{completed_tasks}/{total_tasks} tasks completed" if total_tasks > 0 else "no tasks yet"
                    
                    context_data.append(f"📂 Project '{project['name']}' ({progress}) - {project.get('description', '')}".strip())
                
                # Add task context - focus on recent and important ones
                task_summaries = []
                overdue_tasks = []
                today_tasks = []
                high_priority_tasks = []
                
                for task in tasks:
                    status_emoji = "✅" if task["status"] == "completed" else "📋"
                    priority_text = f"({task.get('priority', 'medium')} priority)"
                    
                    # Check if task is overdue
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
                                overdue_tasks.append(task['title'])
                            elif due_date.date() == now.date():
                                today_tasks.append(task['title'])
                        except (ValueError, TypeError):
                            pass
                    
                    if task.get('priority') == 'high' and task.get('status') != 'completed':
                        high_priority_tasks.append(task['title'])
                
                # Create intelligent context summary
                context_summary = []
                if len(projects) > 0:
                    context_summary.append(f"📊 {len(projects)} active projects")
                if len(overdue_tasks) > 0:
                    context_summary.append(f"🚨 {len(overdue_tasks)} overdue tasks: {', '.join(overdue_tasks[:3])}")
                if len(today_tasks) > 0:
                    context_summary.append(f"⏰ {len(today_tasks)} tasks due today: {', '.join(today_tasks[:3])}")
                if len(high_priority_tasks) > 0:
                    context_summary.append(f"⚡ {len(high_priority_tasks)} high priority tasks: {', '.join(high_priority_tasks[:3])}")
                
                completed_count = len([t for t in tasks if t.get('status') == 'completed'])
                total_tasks = len(tasks)
                if total_tasks > 0:
                    completion_rate = (completed_count / total_tasks) * 100
                    context_summary.append(f"📈 {completion_rate:.0f}% completion rate ({completed_count}/{total_tasks})")
                
                prompt = f"""
                Based on this user's current work situation, provide 3-4 personalized, actionable suggestions:
                
                PROJECTS: {len(projects)} projects
                {chr(10).join(context_data) if context_data else "No projects yet"}
                
                TASK SITUATION:
                {chr(10).join(context_summary) if context_summary else "No tasks yet"}
                
                Generate intelligent suggestions that:
                - Address urgent issues (overdue/today's tasks) first
                - Help with project organization if they have projects
                - Suggest productivity improvements based on their patterns
                - Encourage progress and next steps
                
                Each suggestion should be:
                - Specific to their actual situation
                - Actionable (they can do it now)
                - Under 80 characters
                - Start with a relevant emoji
                
                Respond with exactly 3-4 suggestions as a JSON array of strings.
                """
                
                user_message = UserMessage(text=prompt)
                response = await chat.send_message(user_message)
                
                try:
                    suggestions = json.loads(response.strip())
                    if isinstance(suggestions, list) and len(suggestions) >= 3:
                        return TaskSuggestionResponse(suggestions=suggestions[:4])
                except json.JSONDecodeError:
                    logger.warning("AI returned malformed JSON, falling back to intelligent analysis")
            
            # Enhanced intelligent fallback suggestions based on actual user data
            suggestions = []
            
            # Analyze current situation
            overdue_count = 0
            today_count = 0
            high_priority_count = 0
            completed_count = 0
            
            for task in tasks:
                if task.get('status') == 'completed':
                    completed_count += 1
                    continue
                
                if task.get('priority') == 'high':
                    high_priority_count += 1
                
                if task.get('due_date'):
                    try:
                        due_date = task['due_date']
                        if isinstance(due_date, str):
                            due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                        elif isinstance(due_date, datetime):
                            if due_date.tzinfo is None:
                                due_date = due_date.replace(tzinfo=timezone.utc)
                        
                        now = datetime.now(timezone.utc)
                        if due_date < now:
                            overdue_count += 1
                        elif due_date.date() == now.date():
                            today_count += 1
                    except (ValueError, TypeError):
                        continue
            
            # Prioritize suggestions based on user's actual situation
            if overdue_count > 0:
                suggestions.append(f"🚨 Focus on {overdue_count} overdue task{'s' if overdue_count != 1 else ''} - tackle the smallest one first!")
            
            if today_count > 0:
                suggestions.append(f"⏰ {today_count} task{'s' if today_count != 1 else ''} due today - prioritize your time wisely")
            
            if high_priority_count > 3:
                suggestions.append("⚡ Consider reducing some high priority tasks to avoid overwhelm")
            elif high_priority_count > 0:
                suggestions.append(f"🎯 Focus on completing {high_priority_count} high priority task{'s' if high_priority_count != 1 else ''} first")
            
            # Project-specific suggestions
            if len(projects) > 0:
                projects_with_no_tasks = len([p for p in projects if not any(t.get('project_id') == p['id'] for t in tasks)])
                if projects_with_no_tasks > 0:
                    suggestions.append(f"📂 Add tasks to {projects_with_no_tasks} empty project{'s' if projects_with_no_tasks != 1 else ''}")
                elif len(tasks) > 10 and not any(t.get('project_id') for t in tasks):
                    suggestions.append("📊 Organize your tasks into projects for better structure")
            
            # Progress-based suggestions
            if completed_count > 0:
                if len(tasks) > 0:
                    completion_rate = (completed_count / len(tasks)) * 100
                    if completion_rate >= 50:
                        suggestions.append(f"🎉 Great momentum! {completion_rate:.0f}% completion rate - keep it up!")
                    else:
                        suggestions.append(f"💪 You've completed {completed_count} task{'s' if completed_count != 1 else ''} - build on that progress!")
            
            # General productivity suggestions if we need more
            if len(suggestions) < 3:
                productivity_suggestions = [
                    "📝 Break large tasks into smaller, manageable chunks for quick wins",
                    "⏰ Set specific due dates for better time management",
                    "🎯 Use the 2-minute rule: do quick tasks immediately",
                    "📅 Review and plan your tasks each morning",
                    "🔄 Group similar tasks together for efficiency"
                ]
                
                # Add suggestions that aren't already covered
                for suggestion in productivity_suggestions:
                    if len(suggestions) < 4:
                        suggestions.append(suggestion)
            
            return TaskSuggestionResponse(suggestions=suggestions[:4])
            
        except Exception as e:
            logger.error(f"Enhanced suggestions error: {str(e)}")
            # Ultimate fallback with some personalization
            task_count = len(tasks)
            project_count = len(projects)
            
            if task_count == 0 and project_count == 0:
                return TaskSuggestionResponse(suggestions=[
                    "🚀 Start with creating your first task or project",
                    "💡 Use natural language: 'Buy groceries this weekend'",
                    "📊 Create projects to organize related tasks together"
                ])
            else:
                return TaskSuggestionResponse(suggestions=[
                    f"📋 You have {task_count} tasks - prioritize the most important ones",
                    f"📂 {project_count} projects need attention - check their progress",
                    "⚡ Focus on completing one task at a time for better results",
                    "📅 Set realistic due dates to stay on track"
                ])
    
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