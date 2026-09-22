"""Unit tests for ingestion layer."""

import pytest
from pathlib import Path
from src.ingestion.validators import (
    validate_transcript_text,
    validate_meeting_metadata,
    validate_file_extension,
)
from src.ingestion.txt_loader import load_txt
from src.ingestion.loaders import load_transcript_file


def test_validate_transcript_text():
    # Empty
    valid, msg = validate_transcript_text("")
    assert not valid
    assert "cannot be empty" in msg

    # Too short
    valid, msg = validate_transcript_text("Hi there")
    assert not valid
    assert "too short" in msg

    # Valid
    valid, msg = validate_transcript_text("Arun: I will complete the report by Friday.")
    assert valid
    assert msg == ""


def test_validate_meeting_metadata():
    valid, msg = validate_meeting_metadata("")
    assert not valid
    assert "required" in msg

    valid, msg = validate_meeting_metadata("Sprint Review")
    assert valid


def test_validate_file_extension():
    assert validate_file_extension("meeting.txt")[0]
    assert validate_file_extension("notes.pdf")[0]
    assert validate_file_extension("doc.docx")[0]
    assert not validate_file_extension("script.py")[0]
    assert not validate_file_extension("image.png")[0]


def test_load_txt_bytes():
    raw_bytes = b"Priya: Hello team\nArun: Hi Priya"
    loaded = load_txt(raw_bytes)
    assert "Priya: Hello team" in loaded
