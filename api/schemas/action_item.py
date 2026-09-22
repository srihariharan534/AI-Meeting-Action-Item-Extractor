"""Pydantic models for Action Items and Decisions."""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ActionItemBase(BaseModel):
    """Base fields for an action item."""
    task: str = Field(..., description="Short, clear task title")
    description: Optional[str] = Field(None, description="Detailed task description")
    owner: Optional[str] = Field(None, description="Responsible person or team, null if unassigned")
    owner_confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    deadline: Optional[datetime] = Field(None, description="Normalized ISO date")
    deadline_text_original: Optional[str] = Field(None, description="Original raw transcript phrasing")
    deadline_type: str = Field(default="missing", description="exact_date | relative_date | inferred_date | ambiguous | missing")
    priority: str = Field(default="medium", description="low | medium | high | critical | unknown")
    status: str = Field(default="pending", description="pending | in_progress | completed | blocked | rejected | needs_review")
    action_type: str = Field(default="other", description="create | review | fix | send | prepare | analyze | approve | schedule | contact | research | update | test | deploy | follow_up | other")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    evidence: str = Field(..., description="Verbatim supporting sentence from transcript")
    evidence_segment_ids: List[str] = Field(default_factory=list, description="IDs of supporting transcript segments")
    ambiguities: List[str] = Field(default_factory=list)
    validation_flags: List[str] = Field(default_factory=list)
    requires_review: bool = False
    review_status: str = Field(default="pending", description="pending | approved | edited | rejected")
    review_comment: Optional[str] = None


class ActionItemCreate(ActionItemBase):
    """Payload to create an action item."""
    meeting_id: str


class ActionItemUpdate(BaseModel):
    """Payload to update an action item."""
    task: Optional[str] = None
    description: Optional[str] = None
    owner: Optional[str] = None
    deadline: Optional[datetime] = None
    deadline_text_original: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    review_status: Optional[str] = None
    review_comment: Optional[str] = None
    requires_review: Optional[bool] = None


class ActionItemReviewAction(BaseModel):
    """Review action submission."""
    action: str = Field(..., description="approve | edit | reject | complete")
    reviewer_note: Optional[str] = None
    updated_fields: Optional[ActionItemUpdate] = None


class ActionItemResponse(ActionItemBase):
    """Output representation for an action item."""
    task_id: str
    meeting_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DecisionBase(BaseModel):
    """Base fields for an extracted meeting decision."""
    decision: str = Field(..., description="The decision text")
    decision_date: Optional[datetime] = None
    decision_owner: Optional[str] = None
    evidence: str = Field(..., description="Evidence sentence from transcript")
    evidence_segment_ids: List[str] = Field(default_factory=list)
    confidence: float = 1.0
    requires_review: bool = False


class DecisionResponse(DecisionBase):
    """Output representation for a meeting decision."""
    decision_id: str
    meeting_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class TaskRelationshipBase(BaseModel):
    """Base model for task dependency and relationships."""
    source_task_id: str
    target_task_id: str
    relationship_type: str = Field(..., description="depends_on | blocks | related_to | blocked_by | duplicate_of")
    confidence: float = 1.0
    evidence: Optional[str] = None
    requires_review: bool = False


class TaskRelationshipResponse(TaskRelationshipBase):
    relationship_id: str
    created_at: datetime

    class Config:
        from_attributes = True
