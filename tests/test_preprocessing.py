"""Unit tests for preprocessing, segmentation, and speaker parsing."""

from src.preprocessing.cleaner import clean_text
from src.preprocessing.speaker_parser import parse_speaker_and_timestamps
from src.preprocessing.segmenter import segment_transcript, split_into_sentences


def test_clean_text():
    dirty = "Line 1   with   spaces\r\n\r\n\r\n\r\nLine 2"
    cleaned = clean_text(dirty)
    assert "\r" not in cleaned
    assert "Line 1 with spaces" in cleaned


def test_parse_speaker_and_timestamps():
    speaker, ts_start, _, content = parse_speaker_and_timestamps("Arun [09:15]: We need to finish by 5pm.")
    assert speaker == "Arun"
    assert ts_start == "09:15"
    assert content == "We need to finish by 5pm."


def test_segment_transcript():
    transcript = "Priya: Let's begin. Arun will review the report.\nArun: I will do it by Friday."
    segments = segment_transcript(transcript, meeting_id="m1")
    assert len(segments) >= 2
    assert segments[0]["speaker"] == "Priya"
    assert segments[0]["segment_id"] == "seg_001"
    assert segments[1]["segment_id"] == "seg_002"
