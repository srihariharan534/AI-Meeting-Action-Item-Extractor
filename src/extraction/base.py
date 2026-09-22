"""Base interface for LLM extraction providers."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from api.schemas.action_item import ActionItemBase, DecisionBase


class LLMProvider(ABC):
    """Abstract interface for AI action-item and decision extractors."""

    @abstractmethod
    def extract_action_items_and_decisions(
        self,
        segments: List[Dict[str, Any]],
        meeting_metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Extract structured action items and decisions from transcript segments.
        Returns a dict with keys: 'action_items' and 'decisions'.
        """
        pass
