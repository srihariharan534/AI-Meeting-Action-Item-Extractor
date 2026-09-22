"""Benchmark dataset loader and serializer."""

import json
from pathlib import Path
from typing import List, Dict, Any
from src.config import settings


def load_evaluation_dataset(dataset_path: Path = None) -> List[Dict[str, Any]]:
    """Load gold annotated benchmark dataset from JSON."""
    path = dataset_path or (settings.DATA_PATH / "annotations" / "benchmark_eval.json")
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
