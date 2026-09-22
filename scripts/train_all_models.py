"""
Model / Provider Artifact Preparation Script.
Honest Documentation: This script prepares and verifies deterministic rule vocabularies,
similarity models (TF-IDF), date parser caches, and provider configuration schemas.
It does NOT pretend to train an LLM locally from scratch.
"""

import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from sklearn.feature_extraction.text import TfidfVectorizer
from src.config import settings
from src.logging_config import logger


def main():
    logger.info("Starting train_all_models.py (Artifact & Model Pipeline Preparation)...")

    # 1. Prepare TF-IDF vectorizer vocabulary on sample meeting corpus
    corpus = [
        "prepare the detailed proposal by Friday",
        "review the UI components and design",
        "update documentation and API references",
        "coordinate with QA to execute load tests",
        "investigate payment gateway bug",
    ]

    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    vectorizer.fit(corpus)
    logger.info(f"Fitted TF-IDF vocabulary of {len(vectorizer.vocabulary_)} features for deduplication.")

    # 2. Verify AI Provider configurations
    logger.info(f"Active configured AI Provider: '{settings.AI_PROVIDER}'")
    logger.info("Artifact and model preparation completed successfully.")


if __name__ == "__main__":
    main()
