"""Unit tests for TF-IDF similarity and duplicate detector."""

from src.deduplication.similarity import compute_text_similarity
from src.deduplication.duplicate_detector import detect_duplicates_and_conflicts


def test_compute_text_similarity():
    sim = compute_text_similarity("Prepare marketing report", "Prepare detailed marketing report")
    assert sim > 0.60

    sim_diff = compute_text_similarity("Prepare marketing report", "Resolve backend database latency")
    assert sim_diff < 0.20


def test_detect_duplicates_and_conflicts():
    task1 = {"task_id": "t1", "task": "Prepare the marketing report", "owner": "Arun", "deadline": None, "meeting_id": "m1"}
    task2 = {"task_id": "t2", "task": "Prepare marketing report", "owner": "Meena", "deadline": None, "meeting_id": "m2"}

    matches = detect_duplicates_and_conflicts([task1], [task2])
    assert len(matches) == 1
    # Different owners -> conflicting_task
    assert matches[0]["suggested_relationship"] == "conflicting_task"
