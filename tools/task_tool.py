from typing import List, Any
from datetime import datetime
from models import Task
from database import get_db
from .base_tool import BaseTool

class TaskTool(BaseTool):
    async def execute(self, action: str, **kwargs) -> Any:
        if action == "create_task":
            return await self._create_task(**kwargs)
        elif action == "get_tasks":
            return await self._get_tasks(**kwargs)
        elif action == "update_task":
            return await self._update_task(**kwargs)
        elif action == "delete_task":
            return await self._delete_task(**kwargs)
        elif action == "prioritize_tasks":
            return await self._prioritize_tasks(**kwargs)
        return None

    async def _create_task(self, title: str, description: str = "", priority: str = "medium", due_date: datetime = None) -> Task:
        db = get_db()
        try:
            task = Task(
                title=title,
                description=description,
                priority=priority,
                status="pending",
                due_date=due_date
            )
            db.add(task)
            db.commit()
            db.refresh(task)
            return task
        finally:
            db.close()

    async def _get_tasks(self, status: str = None, priority: str = None) -> List[Task]:
        db = get_db()
        try:
            query = db.query(Task)
            if status:
                query = query.filter(Task.status == status)
            if priority:
                query = query.filter(Task.priority == priority)
            return query.all()
        finally:
            db.close()

    async def _update_task(self, task_id: int, **updates) -> Task:
        db = get_db()
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if task:
                for key, value in updates.items():
                    setattr(task, key, value)
                task.updated_at = datetime.utcnow()
                db.commit()
                db.refresh(task)
            return task
        finally:
            db.close()

    async def _delete_task(self, task_id: int) -> bool:
        db = get_db()
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if task:
                db.delete(task)
                db.commit()
                return True
            return False
        finally:
            db.close()

    async def _prioritize_tasks(self, tasks=None) -> List[Task]:
        if tasks is None:
            db = get_db()
            try:
                tasks = db.query(Task).filter(Task.status != "completed").all()
            finally:
                db.close()
        
        # Simple prioritization: high > medium > low, then by due date
        priority_order = {"high": 3, "medium": 2, "low": 1}
        sorted_tasks = sorted(tasks, key=lambda t: (priority_order.get(t.priority, 0), t.due_date or datetime.max), reverse=True)
        return sorted_tasks