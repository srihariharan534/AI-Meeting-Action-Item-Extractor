"""Service layer for Meeting ingestion and lifecycle."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from src.database.repositories import MeetingRepository, SegmentRepository
from src.database.models import Meeting
from src.ingestion.validators import validate_transcript_text, validate_meeting_metadata
from src.preprocessing.segmenter import segment_transcript
from src.logging_config import logger


class MeetingService:
    def __init__(self, db: Session):
        self.db = db
        self.meeting_repo = MeetingRepository(db)
        self.segment_repo = SegmentRepository(db)

    def create_meeting(
        self,
        title: str,
        transcript_text: str,
        meeting_date: Optional[datetime] = None,
        meeting_type: str = "General meeting",
        organizer: Optional[str] = None,
        participants: Optional[List[str]] = None,
        project_name: Optional[str] = None,
        department: Optional[str] = None,
        source_filename: Optional[str] = None,
    ) -> Meeting:
        # Validate inputs
        valid_meta, meta_err = validate_meeting_metadata(title, meeting_date)
        if not valid_meta:
            raise ValueError(meta_err)

        valid_trans, trans_err = validate_transcript_text(transcript_text)
        if not valid_trans:
            raise ValueError(trans_err)

        date_val = meeting_date or datetime.utcnow()
        parts = participants or []

        meeting_data = {
            "title": title.strip(),
            "meeting_date": date_val,
            "meeting_type": meeting_type,
            "organizer": organizer,
            "participants": parts,
            "project_name": project_name,
            "department": department,
            "source_filename": source_filename,
            "transcript_text": transcript_text,
            "processing_status": "pending",
        }

        meeting = self.meeting_repo.create(meeting_data)
        logger.info(f"Created meeting '{meeting.title}' (ID: {meeting.meeting_id})")

        # Automatically segment and persist segments
        segments = segment_transcript(transcript_text, meeting_id=meeting.meeting_id)
        if segments:
            self.segment_repo.create_batch(segments)
            logger.info(f"Persisted {len(segments)} segments for meeting {meeting.meeting_id}")

        return meeting

    def get_meeting(self, meeting_id: str) -> Optional[Meeting]:
        return self.meeting_repo.get_by_id(meeting_id)

    def list_meetings(self, skip: int = 0, limit: int = 100) -> List[Meeting]:
        return self.meeting_repo.list_all(skip, limit)

    def delete_meeting(self, meeting_id: str) -> bool:
        return self.meeting_repo.delete(meeting_id)
