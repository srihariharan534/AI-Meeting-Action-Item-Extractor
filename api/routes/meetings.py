"""Meetings API routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from api.dependencies import get_db
from api.schemas.meeting import (
    MeetingCreate,
    MeetingResponse,
    MeetingDetailResponse,
    MeetingProcessingResponse,
)
from api.schemas.action_item import ActionItemResponse, DecisionResponse
from api.schemas.common import APIResponse
from src.services.meeting_service import MeetingService
from src.services.extraction_service import ExtractionService

router = APIRouter(prefix="/meetings", tags=["Meetings"])


@router.post("", response_model=APIResponse[MeetingResponse], status_code=201)
def create_meeting(payload: MeetingCreate, db: Session = Depends(get_db)):
    """Ingest a new meeting transcript with metadata."""
    service = MeetingService(db)
    try:
        meeting = service.create_meeting(
            title=payload.title,
            transcript_text=payload.transcript_text,
            meeting_date=payload.meeting_date,
            meeting_type=payload.meeting_type,
            organizer=payload.organizer,
            participants=payload.participants,
            project_name=payload.project_name,
            department=payload.department,
            source_filename=payload.source_filename,
        )
        return APIResponse(
            success=True,
            message="Meeting created and segmented successfully",
            data=meeting,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=APIResponse[List[MeetingResponse]])
def list_meetings(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List all ingested meetings ordered by newest first."""
    service = MeetingService(db)
    meetings = service.list_meetings(skip=skip, limit=limit)
    return APIResponse(success=True, data=meetings)


@router.get("/{meeting_id}", response_model=APIResponse[MeetingDetailResponse])
def get_meeting_details(meeting_id: str, db: Session = Depends(get_db)):
    """Retrieve full meeting details including transcript segments, action items, and decisions."""
    service = MeetingService(db)
    meeting = service.get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return APIResponse(success=True, data=meeting)


@router.delete("/{meeting_id}", response_model=APIResponse[bool])
def delete_meeting(meeting_id: str, db: Session = Depends(get_db)):
    """Delete a meeting and all associated action items, segments, and decisions."""
    service = MeetingService(db)
    deleted = service.delete_meeting(meeting_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return APIResponse(success=True, message="Meeting deleted successfully", data=True)


@router.post("/{meeting_id}/process", response_model=APIResponse[MeetingProcessingResponse])
def process_meeting_action_items(
    meeting_id: str,
    provider: Optional[str] = Query(None, description="Optional AI Provider override: mock | rule | openai"),
    db: Session = Depends(get_db),
):
    """Execute AI extraction, evidence grounding, date intelligence, and validation on meeting."""
    service = ExtractionService(db)
    try:
        result = service.process_meeting(meeting_id, provider_name=provider or "")
        return APIResponse(
            success=True,
            message="Meeting action items processed successfully",
            data=result,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failure: {str(e)}")


@router.get("/{meeting_id}/action-items", response_model=APIResponse[List[ActionItemResponse]])
def get_meeting_action_items(meeting_id: str, db: Session = Depends(get_db)):
    """Get all action items associated with a specific meeting."""
    meeting_svc = MeetingService(db)
    meeting = meeting_svc.get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return APIResponse(success=True, data=meeting.action_items)


@router.get("/{meeting_id}/decisions", response_model=APIResponse[List[DecisionResponse]])
def get_meeting_decisions(meeting_id: str, db: Session = Depends(get_db)):
    """Get all decisions extracted from a specific meeting."""
    meeting_svc = MeetingService(db)
    meeting = meeting_svc.get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return APIResponse(success=True, data=meeting.decisions)
