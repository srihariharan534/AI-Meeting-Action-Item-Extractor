"""Unit tests for validation, date normalization, and confidence scoring."""

from datetime import datetime
from src.validation.date_validator import normalize_deadline
from src.validation.rules import run_validation_rules
from src.validation.confidence import calculate_extraction_confidence


def test_normalize_deadline_relative():
    meeting_date = datetime(2026, 9, 18)  # Friday
    # Tomorrow
    dt, dtype, ambig = normalize_deadline("tomorrow", reference_date=meeting_date)
    assert dtype == "relative_date"
    assert dt.day == 19

    # Soon -> ambiguous
    dt_soon, dtype_soon, ambig_soon = normalize_deadline("soon", reference_date=meeting_date)
    assert dtype_soon == "ambiguous"
    assert dt_soon is None


def test_validation_flags_missing_owner():
    task_data = {
        "task": "Update the documentation",
        "owner": None,
        "deadline": None,
        "deadline_text_original": None,
        "deadline_type": "missing",
        "evidence": "Someone needs to update the documentation.",
        "confidence": 0.85,
    }
    flags, issues, req_review = run_validation_rules(task_data, datetime(2026, 9, 18))
    assert "missing_owner" in flags
    assert req_review is True


def test_confidence_calculation():
    overall, breakdown, reasons = calculate_extraction_confidence(
        task="Prepare proposal",
        owner="Arun",
        owner_conf=0.95,
        deadline_type="relative_date",
        evidence="I will prepare the proposal by Friday.",
        validation_flags=[],
    )
    assert overall >= 0.80
    assert "overall" in breakdown
