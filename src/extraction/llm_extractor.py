"""OpenAI provider implementation for cloud LLM structured extraction."""

from typing import List, Dict, Any
from src.extraction.base import LLMProvider
from src.extraction.prompts import EXTRACTION_SYSTEM_PROMPT, EXTRACTION_USER_PROMPT_TEMPLATE
from src.extraction.parser import parse_extraction_json
from src.config import settings
from src.logging_config import logger


class OpenAIProvider(LLMProvider):
    """Extraction provider using OpenAI API with structured JSON output."""

    def __init__(self, api_key: str = "", model: str = ""):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL

        if not self.api_key:
            logger.warning("OpenAI API key is missing. OpenAIProvider will fail if invoked without key.")

    def extract_action_items_and_decisions(
        self,
        segments: List[Dict[str, Any]],
        meeting_metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not configured in environment or settings.")

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("openai package is required to use OpenAIProvider.")

        # Format segments for prompt
        formatted_segments = []
        for s in segments:
            formatted_segments.append(
                f"[{s['segment_id']}] {s['speaker']}: {s['cleaned_text']}"
            )
        segments_str = "\n".join(formatted_segments)

        user_prompt = EXTRACTION_USER_PROMPT_TEMPLATE.format(
            title=meeting_metadata.get("title", "Meeting"),
            meeting_date=meeting_metadata.get("meeting_date", "2026-09-18"),
            meeting_type=meeting_metadata.get("meeting_type", "General meeting"),
            segments_formatted=segments_str,
        )

        logger.info(f"Invoking OpenAI model {self.model} for extraction...")
        response = client.chat.completions.create(
            model=self.model,
            temperature=0.0,
            messages=[
                {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content or "{}"
        return parse_extraction_json(content)
