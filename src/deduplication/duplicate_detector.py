"""Cross-meeting duplicate and conflict detector."""

from typing import List, Dict, Any
from src.deduplication.similarity import compute_text_similarity
from src.config import settings


def detect_duplicates_and_conflicts(
    new_tasks: List[Dict[str, Any]],
    existing_tasks: List[Dict[str, Any]],
    similarity_threshold: float = 0.50,
) -> List[Dict[str, Any]]:
    """
    Compare new extracted tasks with previously stored tasks to flag:
    - probable_duplicate (high lexical overlap)
    - conflicting_task (same task, conflicting owners or deadlines)
    - related_task (moderate overlap)
    """
    threshold = similarity_threshold if similarity_threshold is not None else settings.SIMILARITY_THRESHOLD_DUPLICATE
    matches: List[Dict[str, Any]] = []

    for new_t in new_tasks:
        n_task = new_t.get("task", "")
        n_owner = new_t.get("owner")
        n_deadline = new_t.get("deadline")
        n_id = new_t.get("task_id", "new")
        n_mid = new_t.get("meeting_id", "")

        for ex_t in existing_tasks:
            ex_task = ex_t.get("task", "")
            ex_owner = ex_t.get("owner")
            ex_deadline = ex_t.get("deadline")
            ex_id = ex_t.get("task_id", "")
            ex_mid = ex_t.get("meeting_id", "")

            # Don't compare a task to itself
            if n_id == ex_id:
                continue

            sim = compute_text_similarity(n_task, ex_task)
            if sim >= threshold:
                rel_type = "probable_duplicate"

                # Check for conflicts
                if n_owner and ex_owner and n_owner.lower() != ex_owner.lower():
                    rel_type = "conflicting_task"
                elif n_deadline and ex_deadline and n_deadline != ex_deadline:
                    rel_type = "conflicting_task"

                matches.append({
                    "task_id_1": n_id,
                    "task_1": n_task,
                    "meeting_id_1": n_mid,
                    "task_id_2": ex_id,
                    "task_2": ex_task,
                    "meeting_id_2": ex_mid,
                    "similarity_score": sim,
                    "suggested_relationship": rel_type,
                })

    return matches
