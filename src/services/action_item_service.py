"""Service for Action Items CRUD and Human-in-the-Loop review workflow."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from src.database.repositories import ActionItemRepository, ReviewHistoryRepository
from src.database.models import ActionItem
from src.logging_config import logger


class ActionItemService:
    def __init__(self, db: Session):
        self.db = db
        self.action_repo = ActionItemRepository(db)
        self.review_repo = ReviewHistoryRepository(db)

    def get_action_item(self, task_id: str) -> Optional[ActionItem]:
        return self.action_repo.get_by_id(task_id)

    def list_action_items(
        self,
        status: Optional[str] = None,
        owner: Optional[str] = None,
        requires_review: Optional[bool] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 200,
    ) -> List[ActionItem]:
        return self.action_repo.list_all(
            status=status,
            owner=owner,
            requires_review=requires_review,
            search=search,
            skip=skip,
            limit=limit,
        )

    def update_action_item(self, task_id: str, updates: Dict[str, Any]) -> Optional[ActionItem]:
        return self.action_repo.update(task_id, updates)

    def delete_action_item(self, task_id: str) -> bool:
        return self.action_repo.delete(task_id)

    def execute_review_action(
        self,
        task_id: str,
        action: str,  # approve | edit | reject | complete
        reviewer_note: Optional[str] = None,
        updated_fields: Optional[Dict[str, Any]] = None,
    ) -> Optional[ActionItem]:
        """Perform a human review action and record an immutable audit history entry."""
        item = self.action_repo.get_by_id(task_id)
        if not item:
            return None

        # Capture previous state
        prev_vals = {
            "task": item.task,
            "owner": item.owner,
            "deadline": item.deadline.isoformat() if item.deadline else None,
            "priority": item.priority,
            "status": item.status,
            "review_status": item.review_status,
            "requires_review": item.requires_review,
        }

        updates: Dict[str, Any] = {}
        if updated_fields:
            updates.update(updated_fields)

        if action == "approve":
            updates["review_status"] = "approved"
            updates["requires_review"] = False
            if item.status == "needs_review":
                updates["status"] = "pending"
        elif action == "edit":
            updates["review_status"] = "edited"
            updates["requires_review"] = False
            if item.status == "needs_review":
                updates["status"] = "pending"
        elif action == "reject":
            updates["review_status"] = "rejected"
            updates["status"] = "rejected"
            updates["requires_review"] = False
        elif action == "complete":
            updates["status"] = "completed"
            updates["requires_review"] = False

        if reviewer_note:
            updates["review_comment"] = reviewer_note

        updated_item = self.action_repo.update(task_id, updates)

        # Audit entry
        self.review_repo.record_review(
            task_id=task_id,
            previous_values=prev_vals,
            updated_values=updates,
            action=action,
            reviewer_note=reviewer_note,
        )

        logger.info(f"ActionItem {task_id} review executed: action='{action}' by human reviewer.")
        return updated_item
