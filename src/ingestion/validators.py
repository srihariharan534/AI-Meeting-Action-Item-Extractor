"""Input validation utilities for transcripts and metadata."""

from typing import Tuple, Optional
from datetime import datetime
from src.config import settings


def validate_transcript_text(text: Optional[str]) -> Tuple[bool, str]:
    """Validate transcript text presence, length, and sanity."""
    if not text or not text.strip():
        return False, "Transcript text cannot be empty."

    cleaned = text.strip()
    if len(cleaned) < 10:
        return False, "Transcript is too short to extract action items (minimum 10 characters)."

    # Maximum file size / character threshold (10MB ~ 10 million characters)
    max_chars = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(cleaned) > max_chars:
        return False, f"Transcript exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB."

    return True, ""


def validate_meeting_metadata(
    title: Optional[str],
    meeting_date: Optional[datetime] = None,
) -> Tuple[bool, str]:
    """Validate meeting title and date metadata."""
    if not title or not title.strip():
        return False, "Meeting title is required."

    if len(title.strip()) > 255:
        return False, "Meeting title cannot exceed 255 characters."

    return True, ""


def validate_file_extension(filename: str) -> Tuple[bool, str]:
    """Validate file type extension against supported formats."""
    allowed = {".txt", ".pdf", ".docx"}
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in allowed:
        return False, f"Unsupported file format '{ext}'. Supported formats: .txt, .pdf, .docx"
    return True, ""
