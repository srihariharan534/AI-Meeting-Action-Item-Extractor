"""End-to-end integration test of the extraction pipeline."""

from src.ingestion.txt_loader import load_txt
from src.preprocessing.segmenter import segment_transcript
from src.extraction.mock_extractor import MockProvider
from src.validation.date_validator import normalize_deadline
from src.validation.rules import run_validation_rules
from src.validation.confidence import calculate_extraction_confidence
from datetime import datetime


def test_pipeline_end_to_end():
    sample_text = (
        "Priya [09:00]: Arun, please prepare the sales pitch by Friday.\n"
        "Arun [09:01]: I will prepare the pitch by Friday.\n"
        "Meena [09:02]: Someone needs to review the security guidelines.\n"
        "Priya [09:03]: We decided to launch on October 1st."
    )

    # Preprocessing
    segments = segment_transcript(sample_text)
    assert len(segments) >= 4

    # Extraction
    extractor = MockProvider()
    results = extractor.extract_action_items_and_decisions(segments, {})
    actions = results["action_items"]
    decisions = results["decisions"]

    assert len(actions) >= 2
    assert len(decisions) >= 1

    # Validation & Confidence for each action
    ref_date = datetime(2026, 9, 18)
    for a in actions:
        norm_dt, d_type, ambig = normalize_deadline(a.get("deadline_text_original"), ref_date)
        a["deadline"] = norm_dt
        a["deadline_type"] = d_type
        flags, issues, req_review = run_validation_rules(a, ref_date)
        overall, breakdown, reasons = calculate_extraction_confidence(
            task=a["task"],
            owner=a["owner"] or "",
            owner_conf=a["owner_confidence"],
            deadline_type=d_type,
            evidence=a["evidence"],
            validation_flags=flags,
        )
        assert overall > 0.0
