"""Pydantic schemas for Analytics and Trends."""

from typing import Dict, List, Optional
from pydantic import BaseModel


class AnalyticsOverview(BaseModel):
    total_meetings: int
    total_action_items: int
    total_decisions: int
    completed_tasks: int
    pending_tasks: int
    in_progress_tasks: int
    blocked_tasks: int
    overdue_tasks: int
    unassigned_tasks: int
    review_required_tasks: int
    high_priority_tasks: int
    average_confidence: float


class OwnerAnalytics(BaseModel):
    owner: str
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    overdue_tasks: int


class StatusAnalytics(BaseModel):
    status_counts: Dict[str, int]
    priority_counts: Dict[str, int]
    action_type_counts: Dict[str, int]


class TrendPoint(BaseModel):
    date: str
    created_count: int
    completed_count: int


class AnalyticsTrends(BaseModel):
    trends: List[TrendPoint]


class DuplicateCandidate(BaseModel):
    task_id_1: str
    task_1: str
    meeting_id_1: str
    task_id_2: str
    task_2: str
    meeting_id_2: str
    similarity_score: float
    suggested_relationship: str
