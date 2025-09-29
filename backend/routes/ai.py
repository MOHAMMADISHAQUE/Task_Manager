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

import logging

# Set up logger first
logger = logging.getLogger(__name__)

try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    AI_AVAILABLE = True
    logger.info("emergentintegrations.llm.chat imported successfully")
    try:
        from emergentintegrations.web.search import WebSearch
        WEB_SEARCH_AVAILABLE = True
        logger.info("emergentintegrations.web.search imported successfully")
    except ImportError:
        WEB_SEARCH_AVAILABLE = False
        logger.warning("emergentintegrations.web.search not available, continuing without web search")
except ImportError:
    AI_AVAILABLE = False
    WEB_SEARCH_AVAILABLE = False
    logger.error("emergentintegrations not available, using fallback responses")

from auth.dependencies import get_current_user
from models.tasks import Task

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
            logger.error("AI_AVAILABLE is False - emergentintegrations not imported")
            return None
            
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            logger.error("EMERGENT_LLM_KEY not found in environment")
            return None
            
        try:
            chat = LlmChat(
                api_key=api_key,
                session_id="smarttask-ai",
                system_message="You are an intelligent task management assistant with access to web resources."
            ).with_model("openai", "gpt-5")
            logger.info("GPT-5 chat initialized successfully")
            return chat
        except Exception as e:
            logger.error(f"Failed to initialize GPT-5 chat: {e}")
            return None
    
    def get_web_search():
        """Initialize web search for finding external resources"""
        if not WEB_SEARCH_AVAILABLE:
            logger.warning("Web search not available")
            return None
            
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            logger.warning("EMERGENT_LLM_KEY not found for web search")
            return None
            
        try:
            return WebSearch(api_key=api_key)
        except Exception as e:
            logger.error(f"Failed to initialize web search: {e}")
            return None
    
    async def find_external_resources(task_domains: set, task_titles: list) -> dict:
        """Find external resources for tasks using web search"""
        resources = {}
        
        # Return predefined resources if web search isn't available
        predefined_resources = {
            'marketing': {'title': 'Canva Design Templates', 'url': 'https://canva.com/templates', 'description': 'Professional design templates for marketing'},
            'development': {'title': 'GitHub Code Repository', 'url': 'https://github.com', 'description': 'Version control and collaboration for developers'},
            'design': {'title': 'Figma Design Tool', 'url': 'https://figma.com', 'description': 'Collaborative design and prototyping tool'},
            'finance': {'title': 'Excel Financial Templates', 'url': 'https://templates.office.com/excel', 'description': 'Financial planning and analysis templates'},
            'education': {'title': 'Khan Academy Learning', 'url': 'https://khanacademy.org', 'description': 'Free online courses and tutorials'},
            'business': {'title': 'Notion Productivity Workspace', 'url': 'https://notion.so', 'description': 'All-in-one workspace for notes and planning'},
        }
        
        try:
            web_search = get_web_search()
            if web_search:
                logger.info("Using web search for external resources")
                # Try web search for more specific resources
                for domain in list(task_domains)[:2]:  # Limit to 2 domains
                    try:
                        search_query = f"best {domain} tools 2024"
                        search_results = await web_search.search(search_query, max_results=2)
                        
                        if search_results and 'results' in search_results:
                            for result in search_results['results'][:1]:
                                resources[domain] = {
                                    'title': result.get('title', ''),
                                    'url': result.get('url', ''),
                                    'description': result.get('description', '')[:100]
                                }
                                break
                    except Exception as e:
                        logger.warning(f"Web search failed for {domain}: {e}")
                        # Fall back to predefined resource
                        if domain in predefined_resources:
                            resources[domain] = predefined_resources[domain]
            else:
                logger.info("Using predefined resources (web search not available)")
                # Use predefined resources when web search is not available
                for domain in task_domains:
                    if domain in predefined_resources:
                        resources[domain] = predefined_resources[domain]
                        
        except Exception as e:
            logger.error(f"Resource finding error: {e}")
            # Ultimate fallback to predefined resources
            for domain in task_domains:
                if domain in predefined_resources:
                    resources[domain] = predefined_resources[domain]
            
        return resources
    
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
            
            # Extract domains and important tasks for resource searching
            important_tasks = []
            for task in tasks[:5]:  # Top 5 tasks for resource search
                if task.get('priority') in ['high', 'medium'] and task.get('status') != 'completed':
                    important_tasks.append(task.get('title', ''))
            
            # Find external resources
            external_resources = await find_external_resources(task_domains, important_tasks)
            
            # Enhanced prompt with web resources
            resource_context = ""
            if external_resources:
                resource_context = "AVAILABLE EXTERNAL RESOURCES:\n"
                for key, resource in external_resources.items():
                    resource_context += f"- {resource['title']}: {resource['url']}\n"
            
            # Create intelligent analysis prompt
            prompt = f"""
            You are an AI productivity assistant analyzing specific task and project content. Provide 4 highly intelligent, personalized suggestions.

            USER'S CURRENT WORK:
            {chr(10).join(detailed_context)}

            URGENT ITEMS:
            {chr(10).join(urgent_items) if urgent_items else "No urgent items"}

            DOMAINS DETECTED: {', '.join(task_domains) if task_domains else 'General productivity'}

            {resource_context}

            REQUIREMENTS FOR SUGGESTIONS:
            1. Analyze ACTUAL task/project content, not just counts or generic advice
            2. Address urgent items first with specific, actionable steps
            3. Provide domain-specific suggestions based on the task content
            4. Include relevant external resources, tools, or websites when helpful
            5. Reference specific task names from their list when giving advice
            6. Each suggestion must be immediately actionable

            SUGGESTION QUALITY EXAMPLES:
            ✅ GOOD: "🚨 For overdue 'Marketing Campaign' task - create content calendar with Buffer.com"
            ✅ GOOD: "📊 'Python Learning' project needs structure - start with Python.org's beginner tutorial"  
            ✅ GOOD: "⚡ Break 'Website Design' into: research → wireframe → mockup → code phases"
            ❌ AVOID: "Try organizing tasks by priority level" (too generic)
            ❌ AVOID: "Set realistic due dates" (doesn't reference their actual work)

            FORMAT: Return ONLY a JSON array of exactly 4 suggestion strings.
            Each suggestion should be 80-130 characters, start with emoji, be specific to their tasks.
            """
            
            user_message = UserMessage(text=prompt)
            
            # Set a timeout for the AI response to prevent long waits
            import asyncio
            try:
                response = await asyncio.wait_for(
                    chat.send_message(user_message), 
                    timeout=30.0  # 30 second timeout
                )
            except asyncio.TimeoutError:
                logger.warning("AI response timed out after 30 seconds, using intelligent fallback")
                response = None
            
            if response:
                try:
                    # Parse AI response with timeout
                    suggestions = json.loads(response.strip())
                    if isinstance(suggestions, list) and len(suggestions) >= 3:
                        logger.info(f"AI generated intelligent suggestions: {suggestions}")
                        return TaskSuggestionResponse(suggestions=suggestions[:4])
                    else:
                        logger.warning(f"AI returned invalid format: {suggestions}")
                        raise ValueError("Invalid AI response format")
                except (json.JSONDecodeError, ValueError) as e:
                    logger.error(f"AI returned malformed response: {response[:200]} | Error: {e}")
                    # Fall through to intelligent fallback
            
            # If AI fails, create intelligent fallback based on actual content
            intelligent_suggestions = []
            
            logger.info(f"Creating intelligent fallback suggestions for {len(tasks)} tasks, {len(projects)} projects")
            
            # Address urgent items first with specific advice
            if urgent_items:
                overdue_count = len([item for item in urgent_items if "OVERDUE" in item])
                today_count = len([item for item in urgent_items if "TODAY" in item])
                
                if overdue_count > 0:
                    overdue_task = urgent_items[0].replace("OVERDUE: ", "")
                    intelligent_suggestions.append(f"🚨 Priority: Complete overdue '{overdue_task[:40]}...' - break into 25min sessions")
                
                if today_count > 0:
                    today_task = [item for item in urgent_items if "TODAY" in item][0].replace("TODAY: ", "")
                    intelligent_suggestions.append(f"⏰ Focus: '{today_task[:40]}...' is due today - schedule dedicated time")
            
            # Domain-specific suggestions with external resources
            if 'marketing' in task_domains:
                intelligent_suggestions.append("📈 Marketing tasks detected - try Canva.com for design templates and Buffer.com for scheduling")
            elif 'development' in task_domains or 'coding' in task_domains:
                intelligent_suggestions.append("💻 Development work found - use GitHub.com for version control and Stack Overflow for help")
            elif 'design' in task_domains:
                intelligent_suggestions.append("🎨 Design tasks detected - check Figma.com for collaboration and Dribbble.com for inspiration")
            elif 'finance' in task_domains or 'budget' in task_domains:
                intelligent_suggestions.append("💰 Financial tasks found - use Excel templates from Office.com or QuickBooks.com")
            elif 'education' in task_domains or 'learning' in task_domains:
                intelligent_suggestions.append("📚 Learning goals detected - try Khan Academy, Coursera, or YouTube tutorials")
            elif 'business' in task_domains:
                intelligent_suggestions.append("🏢 Business tasks found - organize with Notion.so or track progress in Trello.com")
            
            # Analyze task patterns for specific suggestions
            long_tasks = [t for t in tasks if len(t.get('title', '')) > 30 or len(t.get('description', '')) > 50]
            if long_tasks:
                sample_task = long_tasks[0].get('title', 'complex task')
                intelligent_suggestions.append(f"📝 Break down '{sample_task[:30]}...' into smaller, manageable subtasks")
            
            # Project-specific advice based on actual data
            projects_without_tasks = [p for p in projects if not any(t.get('project_id') == p.get('id') for t in tasks)]
            if projects_without_tasks and len(projects_without_tasks) <= 3:
                project_names = ', '.join([p.get('name', 'Unnamed')[:20] for p in projects_without_tasks[:2]])
                intelligent_suggestions.append(f"📂 Add specific tasks to '{project_names}' project{'s' if len(projects_without_tasks) > 1 else ''}")
            
            # Progress-based encouragement with specific numbers
            completed_count = len([t for t in tasks if t.get('status') == 'completed'])
            pending_count = len([t for t in tasks if t.get('status') != 'completed'])
            
            if completed_count > 0 and len(tasks) > 0:
                completion_rate = (completed_count / len(tasks)) * 100
                if completion_rate >= 60:
                    intelligent_suggestions.append(f"🎉 Excellent progress! {completion_rate:.0f}% completion rate - maintain this momentum")
                elif completed_count >= 3:
                    intelligent_suggestions.append(f"💪 You've completed {completed_count} tasks - build on that success with the next one")
            
            # Productivity suggestions based on actual task load
            if pending_count > 8:
                intelligent_suggestions.append("⚡ High task load detected - try the Eisenhower Matrix: focus on urgent + important first")
            elif len(tasks) > 0 and not projects:
                intelligent_suggestions.append("📊 Consider organizing your tasks into projects for better structure and tracking")
            
            # Ensure we have exactly 4 suggestions with helpful external resources
            if len(intelligent_suggestions) < 4:
                additional_suggestions = [
                    "🎯 Use Pomodoro Technique (25min focus blocks) - try Forest app to stay focused",
                    "📅 Time-block your calendar with specific task slots - Google Calendar works great",
                    "🔄 Weekly review every Sunday - plan upcoming tasks and celebrate wins",
                    "📝 Capture all ideas in a note-taking app - try Notion.so or Obsidian for organization",
                    "⚡ Apply the 2-minute rule - do quick tasks immediately to clear your list",
                    "🚀 Batch similar tasks together for maximum efficiency and flow state"
                ]
                
                # Add unique suggestions that aren't already included
                for suggestion in additional_suggestions:
                    if len(intelligent_suggestions) < 4:
                        # Check if similar suggestion already exists
                        suggestion_key_words = suggestion.lower().split()[:3]
                        is_duplicate = any(
                            any(word in existing.lower() for word in suggestion_key_words)
                            for existing in intelligent_suggestions
                        )
                        if not is_duplicate:
                            intelligent_suggestions.append(suggestion)
            
            logger.info(f"Generated {len(intelligent_suggestions)} intelligent fallback suggestions")
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