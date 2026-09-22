"""Pydantic models for Meetings and Segments."""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from api.schemas.action_item import ActionItemResponse, DecisionResponse


class TranscriptSegmentResponse(BaseModel):
    segment_id: str
    meeting_id: str
    speaker: str
    timestamp_start: Optional[str] = None
    timestamp_end: Optional[str] = None
    original_text: str
    cleaned_text: str
    sequence_number: int

    class Config:
        from_attributes = True


class MeetingCreate(BaseModel):
    """Payload to create an ingested meeting."""
    title: str = Field(..., min_length=1, max_length=255)
    meeting_date: Optional[datetime] = None
    meeting_type: str = Field(default="General meeting")
    organizer: Optional[str] = None
    participants: List[str] = Field(default_factory=list)
    project_name: Optional[str] = None
    department: Optional[str] = None
    source_filename: Optional[str] = None
    transcript_text: str = Field(..., min_length=1)


class MeetingUpdate(BaseModel):
    """Payload to update meeting metadata."""
    title: Optional[str] = None
    meeting_date: Optional[datetime] = None
    meeting_type: Optional[str] = None
    organizer: Optional[str] = None
    participants: Optional[List[str]] = None
    project_name: Optional[str] = None
    department: Optional[str] = None


class MeetingResponse(BaseModel):
    meeting_id: str
    title: str
    meeting_date: datetime
    meeting_type: str
    organizer: Optional[str] = None
    participants: List[str] = Field(default_factory=list)
    project_name: Optional[str] = None
    department: Optional[str] = None
    source_filename: Optional[str] = None
    transcript_text: str
    processing_status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MeetingDetailResponse(MeetingResponse):
    """Includes segments, action items, and decisions."""
    segments: List[TranscriptSegmentResponse] = Field(default_factory=list)
    action_items: List[ActionItemResponse] = Field(default_factory=list)
    decisions: List[DecisionResponse] = Field(default_factory=list)


class MeetingProcessingResponse(BaseModel):
    """Summary of processing run."""
    meeting_id: str
    segments_count: int
    action_items_count: int
    decisions_count: int
    review_required_count: int
    processing_time_seconds: float
    provider_used: str
    message: str
