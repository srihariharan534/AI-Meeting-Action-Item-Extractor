"""Data preparation script: loads raw transcripts, cleans, segments, and prepares processed data."""

import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import json
from src.config import settings
from src.ingestion.txt_loader import load_txt
from src.preprocessing.segmenter import segment_transcript
from src.logging_config import logger


def main():
    logger.info("Starting prepare_data.py...")
    raw_sample = settings.DATA_PATH / "sample" / "sample_meeting.txt"
    if not raw_sample.exists():
        logger.error(f"Sample meeting not found at {raw_sample}")
        return

    text = load_txt(raw_sample)
    segments = segment_transcript(text, meeting_id="sample_001")

    processed_dir = settings.DATA_PATH / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    out_file = processed_dir / "sample_segmented.json"

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(segments, f, indent=2)

    logger.info(f"Data preparation complete! Segmented {len(segments)} segments saved to {out_file}")


if __name__ == "__main__":
    main()
