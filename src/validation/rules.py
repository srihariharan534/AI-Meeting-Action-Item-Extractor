"""Deterministic validation rule engine for action items."""

from datetime import datetime
from typing import List, Dict, Any, Tuple
from api.schemas.common import ValidationIssue
from src.config import settings


def run_validation_rules(
    task_data: Dict[str, Any],
    meeting_date: datetime,
) -> Tuple[List[str], List[ValidationIssue], bool]:
    """
    Execute deterministic validation checks on an extracted action item.
    Returns: (validation_flags, detailed_issues, requires_review_boolean)
    """
    flags: List[str] = []
    issues: List[ValidationIssue] = []
    requires_review = False

    task = task_data.get("task", "").strip()
    owner = task_data.get("owner")
    deadline = task_data.get("deadline")
    deadline_text = task_data.get("deadline_text_original")
    deadline_type = task_data.get("deadline_type")
    evidence = task_data.get("evidence", "").strip()
    confidence = task_data.get("confidence", 1.0)

    # Rule 1: Missing Task Title
    if not task:
        flags.append("missing_task_title")
        issues.append(ValidationIssue(
            rule_name="missing_task_title",
            severity="critical",
            message="Task title is completely empty.",
            affected_field="task"
        ))
        requires_review = True

    # Rule 2: Missing Owner
    if not owner or owner.lower() in ["unassigned", "none", "unknown", "someone"]:
        flags.append("missing_owner")
        issues.append(ValidationIssue(
            rule_name="missing_owner",
            severity="warning",
            message="No responsible owner was assigned to this task.",
            affected_field="owner"
        ))
        requires_review = True

    # Rule 3: Missing Deadline
    if not deadline and (not deadline_text or deadline_type == "missing"):
        flags.append("missing_deadline")
        issues.append(ValidationIssue(
            rule_name="missing_deadline",
            severity="info",
            message="No target completion deadline was stated in the meeting.",
            affected_field="deadline"
        ))

    # Rule 4: Ambiguous Deadline
    if deadline_type == "ambiguous":
        flags.append("ambiguous_deadline")
        issues.append(ValidationIssue(
            rule_name="ambiguous_deadline",
            severity="warning",
            message=f"Deadline phrasing '{deadline_text}' is ambiguous.",
            affected_field="deadline_text_original"
        ))
        requires_review = True

    # Rule 5: Past Deadline
    if deadline and meeting_date and deadline.date() < meeting_date.date():
        flags.append("past_deadline")
        issues.append(ValidationIssue(
            rule_name="past_deadline",
            severity="warning",
            message=f"Normalized deadline ({deadline.strftime('%Y-%m-%d')}) precedes meeting date ({meeting_date.strftime('%Y-%m-%d')}).",
            affected_field="deadline"
        ))
        requires_review = True

    # Rule 6: Missing Evidence Grounding
    if not evidence or len(evidence) < 5:
        flags.append("missing_evidence")
        issues.append(ValidationIssue(
            rule_name="missing_evidence",
            severity="error",
            message="Task lacks direct evidence quotation from the transcript.",
            affected_field="evidence"
        ))
        requires_review = True

    # Rule 7: Low Confidence Threshold
    if confidence < settings.CONFIDENCE_THRESHOLD_REVIEW:
        flags.append("low_confidence")
        issues.append(ValidationIssue(
            rule_name="low_confidence",
            severity="warning",
            message=f"Extraction confidence ({confidence:.2f}) is below threshold ({settings.CONFIDENCE_THRESHOLD_REVIEW:.2f}).",
            affected_field="confidence"
        ))
        requires_review = True

    return flags, issues, requires_review
