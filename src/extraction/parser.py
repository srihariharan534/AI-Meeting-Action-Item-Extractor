"""JSON and schema parsing with fallback recovery for LLM extraction outputs."""

import json
import re
from typing import Dict, Any, List
from src.logging_config import logger


def clean_json_response(raw_text: str) -> str:
    """Strip markdown code blocks or wrapping strings from LLM text."""
    text = raw_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    return text.strip()


def parse_extraction_json(raw_text: str) -> Dict[str, Any]:
    """Parse JSON with regex fallbacks if malformed."""
    cleaned = clean_json_response(raw_text)

    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError as e:
        logger.warning(f"Standard JSON decoding failed: {e}. Attempting regex block extraction...")

    # Regex extraction of top-level JSON object
    match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception as e2:
            logger.error(f"Regex JSON recovery failed: {e2}")

    return {"action_items": [], "decisions": []}
