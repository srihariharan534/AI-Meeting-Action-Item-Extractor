"""Transparent confidence calculation for action-item extractions."""

from typing import Dict, Any, List, Tuple


def calculate_extraction_confidence(
    task: str,
    owner: str,
    owner_conf: float,
    deadline_type: str,
    evidence: str,
    validation_flags: List[str],
) -> Tuple[float, Dict[str, float], List[str]]:
    """
    Compute decomposed confidence metrics:
    - Task detection confidence
    - Owner confidence
    - Deadline confidence
    - Evidence grounding confidence
    - Overall weighted confidence
    """
    reasons = []

    # 1. Task confidence (clarity and actionability)
    task_conf = 0.95
    if len(task.split()) < 3:
        task_conf = 0.70
        reasons.append("Task description is very short.")

    # 2. Owner confidence
    if not owner or owner.lower() in ["unassigned", "none", "unknown", "someone"]:
        owner_score = 0.40
        reasons.append("No responsible owner identified (Unassigned).")
    else:
        owner_score = max(0.50, min(1.0, owner_conf))

    # 3. Deadline confidence
    if deadline_type == "exact_date":
        deadline_score = 0.95
    elif deadline_type == "relative_date":
        deadline_score = 0.85
    elif deadline_type == "ambiguous":
        deadline_score = 0.40
        reasons.append("Deadline is ambiguous or imprecise.")
    else:  # missing
        deadline_score = 0.60
        reasons.append("No deadline mentioned.")

    # 4. Evidence grounding confidence
    evidence_score = 0.95 if evidence and len(evidence.strip()) > 10 else 0.30
    if evidence_score < 0.5:
        reasons.append("Weak or missing transcript evidence citation.")

    # Validation flag penalties
    penalty = len(validation_flags) * 0.05

    # Overall weighted score
    overall = (
        (task_conf * 0.30) +
        (owner_score * 0.30) +
        (deadline_score * 0.20) +
        (evidence_score * 0.20)
    ) - penalty

    overall_clamped = max(0.20, min(0.99, round(overall, 2)))

    confidence_breakdown = {
        "overall": overall_clamped,
        "task": round(task_conf, 2),
        "owner": round(owner_score, 2),
        "deadline": round(deadline_score, 2),
        "evidence": round(evidence_score, 2),
    }

    return overall_clamped, confidence_breakdown, reasons
