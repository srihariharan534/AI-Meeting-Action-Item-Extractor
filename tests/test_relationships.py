"""Unit tests for task dependency detection."""

from src.relationships.dependency_detector import detect_task_dependencies


def test_detect_task_dependencies():
    tasks = [
        {"task_id": "t1", "task": "Prepare proposal", "evidence": "I will prepare the proposal."},
        {"task_id": "t2", "task": "Review proposal", "evidence": "I will review the proposal after proposal is finished."},
    ]
    deps = detect_task_dependencies(tasks)
    assert len(deps) >= 1
    assert deps[0]["relationship_type"] == "depends_on"
