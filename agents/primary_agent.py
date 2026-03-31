import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta
from database import get_db
from models import Task, Event, Note
from tools.calendar_tool import CalendarTool
from tools.task_tool import TaskTool
from tools.notes_tool import NotesTool
from tools.search_tool import SearchTool

class PrimaryAgent:
    def __init__(self):
        self.max_rounds = 6
        self.tools = {
            "calendar": CalendarTool(),
            "task": TaskTool(),
            "notes": NotesTool(),
            "search": SearchTool()
        }
        self.active_agents = []

    async def process_request(self, user_input: str, websocket=None) -> str:
        self.active_agents = ["Primary"]
        if websocket:
            await websocket.send_json({"type": "status", "active_agents": self.active_agents})

        # Determine workflow based on input
        workflow = self._classify_workflow(user_input)
        
        if workflow == "plan_week":
            return await self._plan_my_week(websocket)
        elif workflow == "proposal_deadline":
            return await self._proposal_deadline(user_input, websocket)
        elif workflow == "schedule_sync":
            return await self._schedule_team_sync(user_input, websocket)
        elif workflow == "whats_on_plate":
            return await self._whats_on_my_plate(websocket)
        else:
            return "I'm sorry, I don't understand that request. Please try one of the predefined workflows."

    def _classify_workflow(self, user_input: str) -> str:
        input_lower = user_input.lower()
        if "plan my week" in input_lower or "weekly brief" in input_lower:
            return "plan_week"
        elif "proposal deadline" in input_lower:
            return "proposal_deadline"
        elif "schedule team sync" in input_lower or "team meeting" in input_lower:
            return "schedule_sync"
        elif "what's on my plate" in input_lower or "daily brief" in input_lower:
            return "whats_on_plate"
        return "unknown"

    async def _plan_my_week(self, websocket=None) -> str:
        self.active_agents = ["Primary", "Search", "Task", "Calendar", "Notes"]
        if websocket:
            await websocket.send_json({"type": "status", "active_agents": self.active_agents})

        db = get_db()
        
        # Get current week
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        # Gather data
        tasks = db.query(Task).filter(Task.due_date.between(week_start, week_end)).all()
        events = db.query(Event).filter(Event.start_time.between(week_start, week_end)).all()
        notes = db.query(Note).filter(Note.created_at.between(week_start, week_end)).all()
        
        # Process with tools
        search_results = await self.tools["search"].execute("search_weekly_data", tasks=tasks, events=events, notes=notes)
        if websocket:
            await websocket.send_json({"type": "tool_call", "tool": "Search", "action": "search_weekly_data", "result": search_results})
        
        prioritized_tasks = await self.tools["task"].execute("prioritize_tasks", tasks=tasks)
        if websocket:
            await websocket.send_json({"type": "tool_call", "tool": "Task", "action": "prioritize_tasks", "result": [t.title for t in prioritized_tasks[:5]]})
        
        response = f"## Weekly Brief ({week_start.strftime('%B %d')} - {week_end.strftime('%B %d')})\n\n"
        response += "### Top Priorities:\n"
        for task in prioritized_tasks[:5]:
            response += f"- {task.title} (Priority: {task.priority}, Due: {task.due_date.strftime('%m/%d')})\n"
        
        response += "\n### Upcoming Events:\n"
        for event in events:
            response += f"- {event.title} at {event.start_time.strftime('%m/%d %H:%M')}\n"
        
        response += "\n### Relevant Notes:\n"
        for note in notes[:3]:
            response += f"- {note.title}\n"
        
        self.active_agents = ["Primary"]
        if websocket:
            await websocket.send_json({"type": "status", "active_agents": self.active_agents})
        
        return response

    async def _proposal_deadline(self, user_input: str, websocket=None) -> str:
        self.active_agents = ["Primary", "Task", "Calendar", "Notes"]
        if websocket:
            await websocket.send_json({"type": "status", "active_agents": self.active_agents})

        # Extract deadline from input (simplified)
        deadline_str = "2024-12-31"  # Default, should parse from input
        deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
        
        db = get_db()
        
        # Create main task
        task = await self.tools["task"].execute("create_task", title="Complete Proposal", description="Prepare and submit the proposal by deadline", priority="high", due_date=deadline)
        if websocket:
            await websocket.send_json({"type": "tool_call", "tool": "Task", "action": "create_task", "result": {"title": task.title, "id": task.id}})
        
        # Block focus time
        focus_start = deadline - timedelta(days=2)
        event = await self.tools["calendar"].execute("create_event", title="Proposal Focus Time", description="Dedicated time to work on proposal", start_time=focus_start, end_time=focus_start + timedelta(hours=4))
        if websocket:
            await websocket.send_json({"type": "tool_call", "tool": "Calendar", "action": "create_event", "result": {"title": event.title, "id": event.id}})
        
        # Create checklist note
        checklist = """Proposal Preparation Checklist:
- Research and gather requirements
- Draft initial proposal
- Review and revise
- Get feedback
- Final edits
- Submit"""
        
        note = await self.tools["notes"].execute("create_note", title="Proposal Checklist", content=checklist, tags="proposal,deadline")
        if websocket:
            await websocket.send_json({"type": "tool_call", "tool": "Notes", "action": "create_note", "result": {"title": note.title, "id": note.id}})
        
        db.commit()
        
        response = "✅ Proposal deadline workflow completed!\n\n"
        response += f"📋 Created task: {task.title}\n"
        response += f"🗓️ Blocked focus time: {event.start_time.strftime('%m/%d %H:%M')}\n"
        response += "📝 Saved preparation checklist\n"
        
        self.active_agents = ["Primary"]
        if websocket:
            await websocket.send_json({"type": "status", "active_agents": self.active_agents})
        
        return response

    async def _schedule_team_sync(self, user_input: str, websocket=None) -> str:
        self.active_agents = ["Primary", "Calendar", "Task", "Notes"]
        if websocket:
            await websocket.send_json({"type": "status", "active_agents": self.active_agents})

        # Parse meeting details (simplified)
        meeting_title = "Team Sync"
        meeting_time = datetime.now() + timedelta(days=1, hours=10)  # Tomorrow 10 AM
        
        db = get_db()
        
        # Book meeting
        event = await self.tools["calendar"].execute("create_event", title=meeting_title, description="Weekly team synchronization meeting", start_time=meeting_time, end_time=meeting_time + timedelta(hours=1))
        if websocket:
            await websocket.send_json({"type": "tool_call", "tool": "Calendar", "action": "create_event", "result": {"title": event.title, "id": event.id}})
        
        # Create agenda task
        task = await self.tools["task"].execute("create_task", title="Prepare Team Sync Agenda", description="Prepare agenda items for the team sync meeting", priority="medium", due_date=meeting_time - timedelta(hours=2))
        if websocket:
            await websocket.send_json({"type": "tool_call", "tool": "Task", "action": "create_task", "result": {"title": task.title, "id": task.id}})
        
        # Save agenda note
        agenda = """Team Sync Agenda:
- Project updates
- Blockers and issues
- Next steps
- Q&A"""
        
        note = await self.tools["notes"].execute("create_note", title="Team Sync Agenda", content=agenda, tags="meeting,agenda")
        if websocket:
            await websocket.send_json({"type": "tool_call", "tool": "Notes", "action": "create_note", "result": {"title": note.title, "id": note.id}})
        
        db.commit()
        
        response = "✅ Team sync scheduled!\n\n"
        response += f"🗓️ Meeting: {event.title} at {event.start_time.strftime('%m/%d %H:%M')}\n"
        response += f"📋 Task: {task.title}\n"
        response += "📝 Agenda saved\n"
        
        self.active_agents = ["Primary"]
        if websocket:
            await websocket.send_json({"type": "status", "active_agents": self.active_agents})
        
        return response

    async def _whats_on_my_plate(self, websocket=None) -> str:
        self.active_agents = ["Primary", "Search", "Task", "Calendar"]
        if websocket:
            await websocket.send_json({"type": "status", "active_agents": self.active_agents})

        db = get_db()
        today = datetime.now()
        
        # Get overdue tasks
        overdue_tasks = db.query(Task).filter(Task.due_date < today, Task.status != "completed").all()
        if websocket:
            await websocket.send_json({"type": "tool_call", "tool": "Task", "action": "get_overdue_tasks", "result": len(overdue_tasks)})
        
        # Get today's events
        today_events = db.query(Event).filter(
            Event.start_time >= today.replace(hour=0, minute=0, second=0),
            Event.start_time < today.replace(hour=23, minute=59, second=59)
        ).all()
        if websocket:
            await websocket.send_json({"type": "tool_call", "tool": "Calendar", "action": "get_today_events", "result": len(today_events)})
        
        # Get top priorities
        all_tasks = db.query(Task).filter(Task.status != "completed").order_by(Task.priority.desc()).limit(3).all()
        if websocket:
            await websocket.send_json({"type": "tool_call", "tool": "Task", "action": "get_top_priorities", "result": [t.title for t in all_tasks]})
        
        response = f"## Daily Brief ({today.strftime('%B %d, %Y')})\n\n"
        
        if overdue_tasks:
            response += "### Overdue Items:\n"
            for task in overdue_tasks:
                response += f"- {task.title} (Due: {task.due_date.strftime('%m/%d')})\n"
        
        response += "\n### Today's Events:\n"
        for event in today_events:
            response += f"- {event.title} at {event.start_time.strftime('%H:%M')}\n"
        
        response += "\n### Top 3 Priorities:\n"
        for i, task in enumerate(all_tasks, 1):
            response += f"{i}. {task.title} (Priority: {task.priority})\n"
        
        self.active_agents = ["Primary"]
        if websocket:
            await websocket.send_json({"type": "status", "active_agents": self.active_agents})
        
        return response