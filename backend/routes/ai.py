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
        """Generate AI-powered task suggestions based on user's current tasks"""
        
        # Get current user
        user = await get_current_user(req, db)
        
        # Get user's tasks
        tasks = await db.tasks.find({"user_id": user["id"]}).to_list(length=None)
        
        if not tasks:
            return TaskSuggestionResponse(suggestions=[
                "🚀 Start by creating your first task!",
                "💡 Try using natural language: 'Remind me to call mom tomorrow'",
                "📅 Set due dates to stay organized"
            ])
        
        try:
            chat = get_llm_chat()
            
            if chat:
                # Prepare task data for AI
                task_summaries = []
                for task in tasks[:10]:  # Limit to recent tasks
                    status_emoji = "✅" if task["status"] == "completed" else "📋"
                    priority_text = f"({task.get('priority', 'medium')} priority)"
                    due_text = f"due {task.get('due_date', 'no date')}" if task.get('due_date') else "no due date"
                    task_summaries.append(f"{status_emoji} {task['title']} - {priority_text} - {due_text}")
                
                prompt = f"""
                Analyze these tasks and provide 3-4 helpful, actionable suggestions for better task management:
                
                Tasks:
                {chr(10).join(task_summaries)}
                
                Provide suggestions about:
                - Task prioritization
                - Breaking down complex tasks
                - Time management
                - Task organization
                
                Respond with exactly 3-4 suggestions, each starting with an emoji and being concise (under 80 chars each).
                Format as a JSON array of strings.
                """
                
                user_message = UserMessage(text=prompt)
                response = await chat.send_message(user_message)
                
                try:
                    suggestions = json.loads(response.strip())
                    if isinstance(suggestions, list):
                        return TaskSuggestionResponse(suggestions=suggestions)
                except json.JSONDecodeError:
                    pass
            
            # Mock suggestions based on task analysis
            suggestions = []
            
            # Analyze tasks for patterns
            overdue_count = len([t for t in tasks if t.get('due_date') and 
                               datetime.fromisoformat(t['due_date'].replace('Z', '+00:00')) < datetime.now(timezone.utc) and
                               t.get('status') != 'completed'])
            
            high_priority_count = len([t for t in tasks if t.get('priority') == 'high' and t.get('status') != 'completed'])
            completed_count = len([t for t in tasks if t.get('status') == 'completed'])
            
            if overdue_count > 0:
                suggestions.append(f"🚨 You have {overdue_count} overdue task{'s' if overdue_count != 1 else ''}. Consider prioritizing them!")
            
            if high_priority_count > 2:
                suggestions.append("⚡ Too many high priority tasks. Consider reducing some to medium priority.")
            
            if completed_count > 0:
                suggestions.append(f"🎉 Great progress! You've completed {completed_count} task{'s' if completed_count != 1 else ''}.")
            
            if len(suggestions) < 3:
                suggestions.extend([
                    "📝 Consider breaking large tasks into smaller, manageable chunks",
                    "⏰ Set specific due dates to stay on track",
                    "🎯 Focus on completing one task at a time for better productivity"
                ])
            
            return TaskSuggestionResponse(suggestions=suggestions[:4])
            
        except Exception as e:
            logger.error(f"Suggestions error: {str(e)}")
            return TaskSuggestionResponse(suggestions=[
                "💡 Try organizing tasks by priority level",
                "📅 Set realistic due dates for better planning",
                "🎯 Break complex tasks into smaller steps"
            ])
    
    @router.get("/summary", response_model=TaskSummaryResponse)
    async def get_task_summary(req: Request):
        """Generate an AI-powered summary of user's tasks"""
        
        # Get current user
        user = await get_current_user(req, db)
        
        # Get user's tasks
        tasks = await db.tasks.find({"user_id": user["id"]}).to_list(length=None)
        
        # Calculate stats
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.get('status') == 'completed'])
        pending_tasks = total_tasks - completed_tasks
        
        overdue_tasks = len([t for t in tasks if t.get('due_date') and 
                           datetime.fromisoformat(t['due_date'].replace('Z', '+00:00')) < datetime.now(timezone.utc) and
                           t.get('status') != 'completed'])
        
        high_priority_tasks = len([t for t in tasks if t.get('priority') == 'high' and t.get('status') != 'completed'])
        
        stats = {
            "total": total_tasks,
            "completed": completed_tasks,
            "pending": pending_tasks,
            "overdue": overdue_tasks,
            "high_priority": high_priority_tasks
        }
        
        if total_tasks == 0:
            return TaskSummaryResponse(
                summary="🎯 You're all set to start! Create your first task to begin organizing your work.",
                stats=stats
            )
        
        try:
            chat = get_llm_chat()
            
            if chat:
                prompt = f"""
                Create a concise, encouraging summary of these task statistics:
                
                - Total tasks: {total_tasks}
                - Completed: {completed_tasks}
                - Pending: {pending_tasks}
                - Overdue: {overdue_tasks}
                - High priority pending: {high_priority_tasks}
                
                Write a 2-3 sentence summary that's motivational and actionable. Include relevant emojis.
                Focus on progress made and next steps. Keep it under 150 characters.
                """
                
                user_message = UserMessage(text=prompt)
                response = await chat.send_message(user_message)
                
                summary = response.strip()
                if len(summary) > 200:  # Fallback if too long
                    summary = summary[:150] + "..."
                
                return TaskSummaryResponse(summary=summary, stats=stats)
            
            # Mock summary generation
            if completed_tasks > 0:
                completion_rate = (completed_tasks / total_tasks) * 100
                summary = f"🎉 Great progress! You've completed {completion_rate:.0f}% of your tasks"
            else:
                summary = "🚀 Ready to tackle your tasks!"
            
            if overdue_tasks > 0:
                summary += f" 🚨 {overdue_tasks} task{'s' if overdue_tasks != 1 else ''} need immediate attention."
            elif high_priority_tasks > 0:
                summary += f" ⚡ Focus on {high_priority_tasks} high priority task{'s' if high_priority_tasks != 1 else ''} next."
            else:
                summary += " Keep up the momentum! 💪"
            
            return TaskSummaryResponse(summary=summary, stats=stats)
            
        except Exception as e:
            logger.error(f"Summary error: {str(e)}")
            return TaskSummaryResponse(
                summary=f"📊 You have {pending_tasks} pending tasks out of {total_tasks} total. Keep going! 💪",
                stats=stats
            )
    
    return router