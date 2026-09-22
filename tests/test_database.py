"""Unit tests for database models and repository CRUD."""

from datetime import datetime
from src.database.session import SessionLocal, init_db
from src.database.repositories import MeetingRepository, ActionItemRepository


def test_database_crud():
    init_db()
    db = SessionLocal()
    try:
        meeting_repo = MeetingRepository(db)
        action_repo = ActionItemRepository(db)

        # Create meeting
        m = meeting_repo.create({
            "title": "Test DB Meeting",
            "meeting_date": datetime.utcnow(),
            "transcript_text": "Priya: Hello\nArun: Hi",
        })
        assert m.meeting_id is not None

        # Add action item
        items = action_repo.create_batch([{
            "meeting_id": m.meeting_id,
            "task": "Test Task",
            "owner": "Priya",
            "evidence": "Priya will test this",
            "confidence": 0.95,
        }])
        assert len(items) == 1
        assert items[0].owner == "Priya"

        # Update action item
        updated = action_repo.update(items[0].task_id, {"status": "completed"})
        assert updated.status == "completed"

        # Cleanup
        meeting_repo.delete(m.meeting_id)
    finally:
        db.close()
