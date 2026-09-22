"""Dependency and relationship detection among action items."""

import re
from typing import List, Dict, Any

DEPENDENCY_KEYWORDS = [
    (r"\bafter (.*?) (?:is done|is finished|is complete|finishes)\b", "depends_on"),
    (r"\bonce (.*?) (?:is done|finishes|completes)\b", "depends_on"),
    (r"\bdepends on\b", "depends_on"),
    (r"\bblocks\b", "blocks"),
    (r"\bblocked by\b", "blocked_by"),
]


def detect_task_dependencies(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Detect logical sequential dependencies between tasks extracted from the same meeting.
    E.g. "Review proposal after draft is prepared" -> Review depends_on Prepare.
    """
    relationships: List[Dict[str, Any]] = []

    for i, t1 in enumerate(tasks):
        desc1 = (t1.get("description", "") + " " + t1.get("evidence", "")).lower()
        t1_id = t1.get("task_id", f"t_{i}")

        for j, t2 in enumerate(tasks):
            if i == j:
                continue
            t2_id = t2.get("task_id", f"t_{j}")
            t2_task_lower = t2.get("task", "").lower()

            # Check if t1 explicitly references t2
            for pattern, rel_type in DEPENDENCY_KEYWORDS:
                if re.search(pattern, desc1):
                    # Check if keywords in t2 are mentioned
                    significant_words = [w for w in t2_task_lower.split() if len(w) > 3]
                    matches = sum(1 for w in significant_words if w in desc1)
                    if matches >= 1:
                        relationships.append({
                            "source_task_id": t1_id,
                            "target_task_id": t2_id,
                            "relationship_type": rel_type,
                            "confidence": 0.80,
                            "evidence": t1.get("evidence", ""),
                            "requires_review": True,
                        })

    return relationships
