"""AI Extraction layer exports and factory."""

from src.extraction.base import LLMProvider
from src.extraction.mock_extractor import MockProvider
from src.extraction.rule_based_extractor import RuleBasedExtractor
from src.extraction.llm_extractor import OpenAIProvider
from src.config import settings
from src.logging_config import logger


def get_ai_provider(provider_name: str = "") -> LLMProvider:
    """Factory to instantiate the configured AI Provider."""
    name = (provider_name or settings.AI_PROVIDER).lower()

    if name == "openai":
        return OpenAIProvider()
    elif name == "rule":
        return RuleBasedExtractor()
    elif name in ["mock", "local"]:
        return MockProvider()

    logger.warning(f"Unknown provider '{name}'. Falling back to MockProvider.")
    return MockProvider()


__all__ = [
    "LLMProvider",
    "MockProvider",
    "RuleBasedExtractor",
    "OpenAIProvider",
    "get_ai_provider",
]
