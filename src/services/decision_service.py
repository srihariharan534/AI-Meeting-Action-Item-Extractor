"""Service for decision management."""

from typing import List, Optional
from sqlalchemy.orm import Session
from src.database.repositories import DecisionRepository
from src.database.models import Decision


class DecisionService:
    def __init__(self, db: Session):
        self.db = db
        self.decision_repo = DecisionRepository(db)

    def get_meeting_decisions(self, meeting_id: str) -> List[Decision]:
        return self.decision_repo.get_by_meeting(meeting_id)

    def list_all_decisions(self) -> List[Decision]:
        return self.decision_repo.list_all()
