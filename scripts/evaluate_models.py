"""
Model Evaluation Script: executes benchmarking across the annotated test set
and records empirical metrics into the database and a JSON report.
"""

import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import json
from src.evaluation.evaluator import run_benchmark_evaluation
from src.database.session import SessionLocal
from src.database.models import EvaluationResults
from src.config import settings
from src.logging_config import logger


def main():
    logger.info("Starting evaluate_models.py...")
    metrics = run_benchmark_evaluation(provider_name=settings.AI_PROVIDER)

    db = SessionLocal()
    try:
        eval_record = EvaluationResults(
            model_name=settings.AI_PROVIDER,
            dataset_name="benchmark_eval.json",
            precision=metrics["precision"],
            recall=metrics["recall"],
            f1_score=metrics["f1_score"],
            owner_accuracy=metrics["owner_accuracy"],
            deadline_accuracy=metrics["deadline_accuracy"],
            evidence_grounding_score=metrics["evidence_grounding_score"],
            processing_time=metrics["processing_time"],
            metrics_metadata=metrics,
        )
        db.add(eval_record)
        db.commit()
        logger.info("Evaluation metrics successfully committed to database.")
    finally:
        db.close()

    # Save to reports directory
    reports_dir = settings.REPORTS_PATH
    reports_dir.mkdir(parents=True, exist_ok=True)
    out_file = reports_dir / "latest_evaluation_metrics.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    logger.info(f"Evaluation metrics saved to {out_file}")
    print("\n=== EVALUATION RESULTS SUMMARY ===")
    print(f"Model / Provider:       {settings.AI_PROVIDER}")
    print(f"Action-Item Precision:  {metrics['precision'] * 100:.1f}%")
    print(f"Action-Item Recall:     {metrics['recall'] * 100:.1f}%")
    print(f"Action-Item F1 Score:   {metrics['f1_score'] * 100:.1f}%")
    print(f"Owner Accuracy:         {metrics['owner_accuracy'] * 100:.1f}%")
    print(f"Deadline Accuracy:      {metrics['deadline_accuracy'] * 100:.1f}%")
    print(f"Grounding Evidence:     {metrics['evidence_grounding_score'] * 100:.1f}%")
    print(f"Latency:                {metrics['processing_time']}s")
    print("==================================\n")


if __name__ == "__main__":
    main()
