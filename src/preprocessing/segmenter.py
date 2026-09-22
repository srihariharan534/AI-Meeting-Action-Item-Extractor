"""Transcript sentence and speaker turn segmentation."""

import re
import uuid
from typing import List, Dict, Any
from src.preprocessing.cleaner import clean_text
from src.preprocessing.speaker_parser import parse_speaker_and_timestamps

# Basic sentence boundary detector
SENTENCE_SPLIT_PATTERN = re.compile(r"(?<=[.?!])\s+(?=[A-Z0-9\"'])")


def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences while preserving meaningful boundaries."""
    sentences = [s.strip() for s in SENTENCE_SPLIT_PATTERN.split(text) if s.strip()]
    return sentences if sentences else [text.strip()]


def segment_transcript(transcript_text: str, meeting_id: str = "") -> List[Dict[str, Any]]:
    """
    Segment a raw meeting transcript into structured, ordered turns/sentences.
    Each segment gets a stable segment_id, sequence_number, speaker, and timestamps.
    """
    cleaned = clean_text(transcript_text)
    if not cleaned:
        return []

    lines = [line.strip() for line in cleaned.split("\n") if line.strip()]
    segments: List[Dict[str, Any]] = []
    seq = 1
    current_speaker = "Unknown"

    for line in lines:
        speaker, ts_start, ts_end, content = parse_speaker_and_timestamps(line)
        if speaker != "Unknown":
            current_speaker = speaker

        if not content:
            continue

        # Split long turn into individual sentences for fine-grained evidence citation
        sentences = split_into_sentences(content)
        for sentence in sentences:
            if not sentence:
                continue

            seg_id = f"seg_{seq:03d}"
            segments.append({
                "segment_id": seg_id,
                "meeting_id": meeting_id,
                "speaker": current_speaker,
                "timestamp_start": ts_start,
                "timestamp_end": ts_end,
                "original_text": sentence,
                "cleaned_text": sentence,
                "sequence_number": seq,
            })
            seq += 1

    return segments
