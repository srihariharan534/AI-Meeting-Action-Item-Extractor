"""Deduplication package exports."""

from src.deduplication.similarity import compute_text_similarity
from src.deduplication.duplicate_detector import detect_duplicates_and_conflicts

__all__ = [
    "compute_text_similarity",
    "detect_duplicates_and_conflicts",
]
