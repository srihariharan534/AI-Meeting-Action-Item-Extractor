"""Analytics and duplicate detection API routes."""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.dependencies import get_db
from api.schemas.analytics import (
    AnalyticsOverview,
    OwnerAnalytics,
    StatusAnalytics,
    AnalyticsTrends,
    DuplicateCandidate,
)
from api.schemas.common import APIResponse
from src.services.analytics_service import AnalyticsService
from src.database.models import ActionItem
from src.deduplication.duplicate_detector import detect_duplicates_and_conflicts

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview", response_model=APIResponse[AnalyticsOverview])
def get_analytics_overview(db: Session = Depends(get_db)):
    """Summary overview KPIs based directly on stored database records."""
    service = AnalyticsService(db)
    data = service.get_overview()
    return APIResponse(success=True, data=data)


@router.get("/owners", response_model=APIResponse[List[OwnerAnalytics]])
def get_owner_breakdown(db: Session = Depends(get_db)):
    """Owner workload breakdown (total, pending, completed, overdue)."""
    service = AnalyticsService(db)
    data = service.get_owner_analytics()
    return APIResponse(success=True, data=data)


@router.get("/status", response_model=APIResponse[StatusAnalytics])
def get_status_distribution(db: Session = Depends(get_db)):
    """Task distribution by status, priority, and action type."""
    service = AnalyticsService(db)
    data = service.get_status_and_priority_distributions()
    return APIResponse(success=True, data=data)


@router.get("/trends", response_model=APIResponse[AnalyticsTrends])
def get_trends(db: Session = Depends(get_db)):
    """Timeline trend of created vs completed tasks."""
    service = AnalyticsService(db)
    data = service.get_trends()
    return APIResponse(success=True, data={"trends": data})


@router.get("/duplicates", response_model=APIResponse[List[DuplicateCandidate]])
def get_duplicate_candidates(db: Session = Depends(get_db)):
    """Detect potential cross-meeting duplicate or conflicting action items."""
    all_items = db.query(ActionItem).all()
    task_dicts = [
        {
            "task_id": item.task_id,
            "task": item.task,
            "owner": item.owner,
            "deadline": item.deadline,
            "meeting_id": item.meeting_id,
        }
        for item in all_items
    ]
    duplicates = detect_duplicates_and_conflicts(task_dicts, task_dicts)
    # Deduplicate symmetric pairs
    seen = set()
    unique_candidates = []
    for d in duplicates:
        pair_key = tuple(sorted([d["task_id_1"], d["task_id_2"]]))
        if pair_key not in seen:
            seen.add(pair_key)
            unique_candidates.append(d)

    return APIResponse(success=True, data=unique_candidates)
