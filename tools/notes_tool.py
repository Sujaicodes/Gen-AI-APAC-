from typing import List, Any
from datetime import datetime
from models import Note
from database import get_db
from .base_tool import BaseTool

class NotesTool(BaseTool):
    async def execute(self, action: str, **kwargs) -> Any:
        if action == "create_note":
            return await self._create_note(**kwargs)
        elif action == "get_notes":
            return await self._get_notes(**kwargs)
        elif action == "update_note":
            return await self._update_note(**kwargs)
        elif action == "delete_note":
            return await self._delete_note(**kwargs)
        elif action == "search_notes":
            return await self._search_notes(**kwargs)
        return None

    async def _create_note(self, title: str, content: str, tags: str = "") -> Note:
        db = get_db()
        note = Note(
            title=title,
            content=content,
            tags=tags
        )
        db.add(note)
        db.commit()
        db.refresh(note)
        return note

    async def _get_notes(self, tag: str = None) -> List[Note]:
        db = get_db()
        query = db.query(Note)
        if tag:
            query = query.filter(Note.tags.contains(tag))
        return query.all()

    async def _update_note(self, note_id: int, **updates) -> Note:
        db = get_db()
        note = db.query(Note).filter(Note.id == note_id).first()
        if note:
            for key, value in updates.items():
                setattr(note, key, value)
            note.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(note)
        return note

    async def _delete_note(self, note_id: int) -> bool:
        db = get_db()
        note = db.query(Note).filter(Note.id == note_id).first()
        if note:
            db.delete(note)
            db.commit()
            return True
        return False

    async def _search_notes(self, query: str) -> List[Note]:
        db = get_db()
        notes = db.query(Note).filter(
            (Note.title.contains(query)) | (Note.content.contains(query)) | (Note.tags.contains(query))
        ).all()
        return notes