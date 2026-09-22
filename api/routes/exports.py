"""Data export API routes."""

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from api.dependencies import get_db
from src.services.export_service import ExportService

router = APIRouter(prefix="/export", tags=["Exports"])


@router.get("/meetings/{meeting_id}/csv")
def export_csv(meeting_id: str, db: Session = Depends(get_db)):
    """Download meeting action items as CSV file."""
    service = ExportService(db)
    csv_str = service.export_action_items_csv(meeting_id)
    return Response(
        content=csv_str,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=meeting_{meeting_id}_actions.csv"},
    )


@router.get("/meetings/{meeting_id}/json")
def export_json(meeting_id: str, db: Session = Depends(get_db)):
    """Download meeting data as structured JSON file."""
    service = ExportService(db)
    json_str = service.export_meeting_json(meeting_id)
    return Response(
        content=json_str,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=meeting_{meeting_id}.json"},
    )


@router.get("/meetings/{meeting_id}/markdown")
def export_markdown(meeting_id: str, db: Session = Depends(get_db)):
    """Download meeting executive report as Markdown."""
    service = ExportService(db)
    md_str = service.export_meeting_markdown(meeting_id)
    return Response(
        content=md_str,
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename=meeting_{meeting_id}_summary.md"},
    )
