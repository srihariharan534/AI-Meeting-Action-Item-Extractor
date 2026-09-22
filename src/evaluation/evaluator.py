"""Evaluation runner for benchmarking AI providers."""

import time
from typing import Dict, Any, List
from src.extraction import get_ai_provider
from src.preprocessing.segmenter import segment_transcript
from src.evaluation.metrics import evaluate_action_item_extractions
from src.evaluation.dataset_loader import load_evaluation_dataset
from src.logging_config import logger


def run_benchmark_evaluation(provider_name: str = "mock") -> Dict[str, Any]:
    """Execute evaluation benchmark across annotated test dataset."""
    dataset = load_evaluation_dataset()
    if not dataset:
        raise FileNotFoundError("Evaluation benchmark dataset not found in data/annotations/benchmark_eval.json")

    ai_provider = get_ai_provider(provider_name)
    all_predictions = []
    all_ground_truth = []

    start_time = time.time()

    for item in dataset:
        transcript = item["transcript"]
        gold_actions = item.get("action_items", [])
        all_ground_truth.extend(gold_actions)

        # Run pipeline
        segments = segment_transcript(transcript)
        extracted = ai_provider.extract_action_items_and_decisions(
            segments,
            {"title": item.get("title", "Eval Meeting"), "meeting_date": item.get("meeting_date", "2026-09-18")}
        )
        all_predictions.extend(extracted.get("action_items", []))

    total_time = round(time.time() - start_time, 2)
    metrics = evaluate_action_item_extractions(all_predictions, all_ground_truth)
    metrics["processing_time"] = total_time
    metrics["total_meetings_evaluated"] = len(dataset)
    metrics["total_gold_items"] = len(all_ground_truth)
    metrics["total_extracted_items"] = len(all_predictions)

    logger.info(f"Evaluation finished in {total_time}s: F1={metrics['f1_score']}")
    return metrics
