"""Unit tests for AI extraction providers and rule engine."""

from src.extraction.rule_based_extractor import RuleBasedExtractor
from src.extraction.mock_extractor import MockProvider


def test_rule_based_extractor_explicit_commitment():
    extractor = RuleBasedExtractor()
    segments = [
        {"segment_id": "seg_001", "speaker": "Arun", "cleaned_text": "I will prepare the proposal by Friday."}
    ]
    results = extractor.extract_action_items_and_decisions(segments, {})
    actions = results["action_items"]
    assert len(actions) == 1
    assert actions[0]["owner"] == "Arun"
    assert "proposal" in actions[0]["task"].lower()
    assert actions[0]["evidence_segment_ids"] == ["seg_001"]


def test_non_action_filtering():
    extractor = RuleBasedExtractor()
    segments = [
        {"segment_id": "seg_001", "speaker": "Meena", "cleaned_text": "Does anyone know the status of the project?"},
        {"segment_id": "seg_002", "speaker": "Rohan", "cleaned_text": "The bug was already resolved yesterday."},
    ]
    results = extractor.extract_action_items_and_decisions(segments, {})
    assert len(results["action_items"]) == 0
