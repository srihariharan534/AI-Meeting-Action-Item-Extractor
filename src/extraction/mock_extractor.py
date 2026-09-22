"""Mock AI extractor for offline testing, demos, and instant local execution."""

from typing import List, Dict, Any
from src.extraction.base import LLMProvider
from src.extraction.rule_based_extractor import RuleBasedExtractor
from src.logging_config import logger


class MockProvider(LLMProvider):
    """
    Mock AI Provider wraps RuleBasedExtractor to provide intelligent,
    deterministic extraction without needing external API keys or GPU weights.
    """

    def __init__(self):
        self._delegate = RuleBasedExtractor()

    def extract_action_items_and_decisions(
        self,
        segments: List[Dict[str, Any]],
        meeting_metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        logger.info("Using MockProvider (deterministic intelligent offline extractor)...")
        results = self._delegate.extract_action_items_and_decisions(segments, meeting_metadata)
        logger.info(
            f"MockProvider extracted {len(results['action_items'])} action items and {len(results['decisions'])} decisions."
        )
        return results
