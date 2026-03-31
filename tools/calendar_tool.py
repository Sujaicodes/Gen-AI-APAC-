from typing import List, Any
from datetime import datetime
from models import Event
from database import get_db
from .base_tool import BaseTool

class CalendarTool(BaseTool):
    async def execute(self, action: str, **kwargs) -> Any:
        if action == "create_event":
            return await self._create_event(**kwargs)
        elif action == "get_events":
            return await self._get_events(**kwargs)
        elif action == "update_event":
            return await self._update_event(**kwargs)
        elif action == "delete_event":
            return await self._delete_event(**kwargs)
        return None

    async def _create_event(self, title: str, start_time: datetime, end_time: datetime, description: str = "", location: str = "") -> Event:
        db = get_db()
        event = Event(
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            location=location
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    async def _get_events(self, start_date: datetime = None, end_date: datetime = None) -> List[Event]:
        db = get_db()
        query = db.query(Event)
        if start_date:
            query = query.filter(Event.start_time >= start_date)
        if end_date:
            query = query.filter(Event.start_time <= end_date)
        return query.all()

    async def _update_event(self, event_id: int, **updates) -> Event:
        db = get_db()
        event = db.query(Event).filter(Event.id == event_id).first()
        if event:
            for key, value in updates.items():
                setattr(event, key, value)
            db.commit()
            db.refresh(event)
        return event

    async def _delete_event(self, event_id: int) -> bool:
        db = get_db()
        event = db.query(Event).filter(Event.id == event_id).first()
        if event:
            db.delete(event)
            db.commit()
            return True
        return False