"""Repository layer for database operations on Meetings and Action Items."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from src.database.models import (
    Meeting,
    TranscriptSegment,
    ActionItem,
    Decision,
    TaskRelationship,
    ReviewHistory,
    EvaluationResults,
)


class MeetingRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, meeting_data: Dict[str, Any]) -> Meeting:
        meeting = Meeting(**meeting_data)
        self.db.add(meeting)
        self.db.commit()
        self.db.refresh(meeting)
        return meeting

    def get_by_id(self, meeting_id: str) -> Optional[Meeting]:
        return self.db.query(Meeting).filter(Meeting.meeting_id == meeting_id).first()

    def list_all(self, skip: int = 0, limit: int = 100) -> List[Meeting]:
        return (
            self.db.query(Meeting)
            .order_by(desc(Meeting.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def delete(self, meeting_id: str) -> bool:
        meeting = self.get_by_id(meeting_id)
        if meeting:
            self.db.delete(meeting)
            self.db.commit()
            return True
        return False

    def update_status(self, meeting_id: str, status: str) -> Optional[Meeting]:
        meeting = self.get_by_id(meeting_id)
        if meeting:
            meeting.processing_status = status
            meeting.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(meeting)
        return meeting


class SegmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_batch(self, segments: List[Dict[str, Any]]) -> List[TranscriptSegment]:
        objs = [TranscriptSegment(**s) for s in segments]
        self.db.add_all(objs)
        self.db.commit()
        return objs

    def get_by_meeting(self, meeting_id: str) -> List[TranscriptSegment]:
        return (
            self.db.query(TranscriptSegment)
            .filter(TranscriptSegment.meeting_id == meeting_id)
            .order_by(TranscriptSegment.sequence_number)
            .all()
        )


class ActionItemRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_batch(self, action_items: List[Dict[str, Any]]) -> List[ActionItem]:
        objs = [ActionItem(**item) for item in action_items]
        self.db.add_all(objs)
        self.db.commit()
        return objs

    def get_by_id(self, task_id: str) -> Optional[ActionItem]:
        return self.db.query(ActionItem).filter(ActionItem.task_id == task_id).first()

    def get_by_meeting(self, meeting_id: str) -> List[ActionItem]:
        return self.db.query(ActionItem).filter(ActionItem.meeting_id == meeting_id).all()

    def list_all(
        self,
        status: Optional[str] = None,
        owner: Optional[str] = None,
        requires_review: Optional[bool] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 200,
    ) -> List[ActionItem]:
        q = self.db.query(ActionItem)
        if status:
            q = q.filter(ActionItem.status == status)
        if owner:
            q = q.filter(ActionItem.owner == owner)
        if requires_review is not None:
            q = q.filter(ActionItem.requires_review == requires_review)
        if search:
            search_fmt = f"%{search}%"
            q = q.filter(
                or_(
                    ActionItem.task.ilike(search_fmt),
                    ActionItem.description.ilike(search_fmt),
                    ActionItem.evidence.ilike(search_fmt),
                    ActionItem.owner.ilike(search_fmt),
                )
            )
        return q.order_by(desc(ActionItem.created_at)).offset(skip).limit(limit).all()

    def update(self, task_id: str, updates: Dict[str, Any]) -> Optional[ActionItem]:
        item = self.get_by_id(task_id)
        if not item:
            return None
        for k, v in updates.items():
            if hasattr(item, k) and v is not None:
                setattr(item, k, v)
        item.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, task_id: str) -> bool:
        item = self.get_by_id(task_id)
        if item:
            self.db.delete(item)
            self.db.commit()
            return True
        return False


class DecisionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_batch(self, decisions: List[Dict[str, Any]]) -> List[Decision]:
        objs = [Decision(**d) for d in decisions]
        self.db.add_all(objs)
        self.db.commit()
        return objs

    def get_by_meeting(self, meeting_id: str) -> List[Decision]:
        return self.db.query(Decision).filter(Decision.meeting_id == meeting_id).all()

    def list_all(self) -> List[Decision]:
        return self.db.query(Decision).order_by(desc(Decision.created_at)).all()


class ReviewHistoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def record_review(
        self,
        task_id: str,
        previous_values: Dict[str, Any],
        updated_values: Dict[str, Any],
        action: str,
        reviewer_note: Optional[str] = None,
    ) -> ReviewHistory:
        entry = ReviewHistory(
            task_id=task_id,
            previous_values=previous_values,
            updated_values=updated_values,
            action=action,
            reviewer_note=reviewer_note,
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry
