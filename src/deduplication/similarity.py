"""String and token similarity utilities for text comparison."""

import re
from typing import Set


def tokenize_text(text: str) -> Set[str]:
    """Clean and tokenize text into words for robust lexical similarity."""
    cleaned = re.sub(r"[^\w\s]", "", text.lower()).strip()
    return {w for w in cleaned.split() if w}


def compute_text_similarity(text1: str, text2: str) -> float:
    """
    Calculate word overlap similarity (Jaccard / Token Overlap)
    supplemented by exact match check.
    """
    if not text1.strip() or not text2.strip():
        return 0.0

    t1_clean = re.sub(r"[^\w\s]", "", text1.lower()).strip()
    t2_clean = re.sub(r"[^\w\s]", "", text2.lower()).strip()

    if t1_clean == t2_clean:
        return 1.0

    tokens1 = tokenize_text(text1)
    tokens2 = tokenize_text(text2)

    if not tokens1 or not tokens2:
        return 0.0

    intersection = tokens1 & tokens2
    union = tokens1 | tokens2

    # Jaccard + Overlap coefficient blend for phrase matching
    jaccard = len(intersection) / len(union)
    overlap = len(intersection) / min(len(tokens1), len(tokens2))

    sim = (jaccard * 0.4) + (overlap * 0.6)
    return round(float(sim), 4)
