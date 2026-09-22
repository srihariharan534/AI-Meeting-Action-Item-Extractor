"""Action Items API routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from api.dependencies import get_db
from api.schemas.action_item import (
    ActionItemResponse,
    ActionItemUpdate,
    ActionItemReviewAction,
)
from api.schemas.common import APIResponse
from src.services.action_item_service import ActionItemService

router = APIRouter(prefix="/action-items", tags=["Action Items"])


@router.get("", response_model=APIResponse[List[ActionItemResponse]])
def list_action_items(
    status: Optional[str] = Query(None),
    owner: Optional[str] = Query(None),
    requires_review: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """List action items with optional status, owner, review flag, or search filter."""
    service = ActionItemService(db)
    items = service.list_action_items(
        status=status,
        owner=owner,
        requires_review=requires_review,
        search=search,
        skip=skip,
        limit=limit,
    )
    return APIResponse(success=True, data=items)


@router.get("/{task_id}", response_model=APIResponse[ActionItemResponse])
def get_action_item(task_id: str, db: Session = Depends(get_db)):
    """Retrieve single action item by task_id."""
    service = ActionItemService(db)
    item = service.get_action_item(task_id)
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    return APIResponse(success=True, data=item)


@router.patch("/{task_id}", response_model=APIResponse[ActionItemResponse])
def update_action_item(
    task_id: str,
    payload: ActionItemUpdate,
    db: Session = Depends(get_db),
):
    """Partially update action item fields."""
    service = ActionItemService(db)
    item = service.update_action_item(task_id, payload.model_dump(exclude_unset=True))
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    return APIResponse(success=True, message="Task updated", data=item)


@router.delete("/{task_id}", response_model=APIResponse[bool])
def delete_action_item(task_id: str, db: Session = Depends(get_db)):
    """Delete an action item."""
    service = ActionItemService(db)
    deleted = service.delete_action_item(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Action item not found")
    return APIResponse(success=True, message="Task deleted", data=True)


@router.post("/{task_id}/approve", response_model=APIResponse[ActionItemResponse])
def approve_action_item(task_id: str, note: Optional[str] = None, db: Session = Depends(get_db)):
    """Human-in-the-loop: Approve an action item and dismiss review flag."""
    service = ActionItemService(db)
    item = service.execute_review_action(task_id, action="approve", reviewer_note=note)
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    return APIResponse(success=True, message="Task approved", data=item)


@router.post("/{task_id}/reject", response_model=APIResponse[ActionItemResponse])
def reject_action_item(task_id: str, note: Optional[str] = None, db: Session = Depends(get_db)):
    """Human-in-the-loop: Reject a hallucinated or invalid action item."""
    service = ActionItemService(db)
    item = service.execute_review_action(task_id, action="reject", reviewer_note=note)
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    return APIResponse(success=True, message="Task rejected", data=item)


@router.post("/{task_id}/complete", response_model=APIResponse[ActionItemResponse])
def complete_action_item(task_id: str, db: Session = Depends(get_db)):
    """Mark action item status as completed."""
    service = ActionItemService(db)
    item = service.execute_review_action(task_id, action="complete")
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    return APIResponse(success=True, message="Task marked completed", data=item)


@router.post("/{task_id}/review", response_model=APIResponse[ActionItemResponse])
def review_action_item_submission(
    task_id: str,
    payload: ActionItemReviewAction,
    db: Session = Depends(get_db),
):
    """Execute review action (approve/edit/reject/complete) with field changes and audit logging."""
    service = ActionItemService(db)
    updated_dict = payload.updated_fields.model_dump(exclude_unset=True) if payload.updated_fields else None
    item = service.execute_review_action(
        task_id=task_id,
        action=payload.action,
        reviewer_note=payload.reviewer_note,
        updated_fields=updated_dict,
    )
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    return APIResponse(success=True, message=f"Task reviewed ({payload.action})", data=item)
