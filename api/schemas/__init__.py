"""Schema definitions for API payloads and responses."""

from api.schemas.common import APIResponse, ValidationIssue, HealthCheckResponse
from api.schemas.meeting import (
    MeetingCreate,
    MeetingUpdate,
    MeetingResponse,
    MeetingDetailResponse,
    MeetingProcessingResponse,
    TranscriptSegmentResponse,
)
from api.schemas.action_item import (
    ActionItemCreate,
    ActionItemUpdate,
    ActionItemResponse,
    ActionItemReviewAction,
    DecisionResponse,
    TaskRelationshipResponse,
)
from api.schemas.analytics import (
    AnalyticsOverview,
    OwnerAnalytics,
    StatusAnalytics,
    AnalyticsTrends,
    DuplicateCandidate,
)

__all__ = [
    "APIResponse",
    "ValidationIssue",
    "HealthCheckResponse",
    "MeetingCreate",
    "MeetingUpdate",
    "MeetingResponse",
    "MeetingDetailResponse",
    "MeetingProcessingResponse",
    "TranscriptSegmentResponse",
    "ActionItemCreate",
    "ActionItemUpdate",
    "ActionItemResponse",
    "ActionItemReviewAction",
    "DecisionResponse",
    "TaskRelationshipResponse",
    "AnalyticsOverview",
    "OwnerAnalytics",
    "StatusAnalytics",
    "AnalyticsTrends",
    "DuplicateCandidate",
]
