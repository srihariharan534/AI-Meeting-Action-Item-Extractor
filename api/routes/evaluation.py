"""Model evaluation API routes."""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.dependencies import get_db
from api.schemas.common import APIResponse
from src.database.models import EvaluationResults

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])


@router.get("/results", response_model=APIResponse[List[Dict[str, Any]]])
def get_evaluation_results(db: Session = Depends(get_db)):
    """Retrieve historical evaluation benchmark results."""
    records = (
        db.query(EvaluationResults)
        .order_by(EvaluationResults.created_at.desc())
        .all()
    )
    data = [
        {
            "evaluation_id": r.evaluation_id,
            "model_name": r.model_name,
            "dataset_name": r.dataset_name,
            "precision": r.precision,
            "recall": r.recall,
            "f1_score": r.f1_score,
            "owner_accuracy": r.owner_accuracy,
            "deadline_accuracy": r.deadline_accuracy,
            "evidence_grounding_score": r.evidence_grounding_score,
            "duplicate_f1": r.duplicate_f1,
            "processing_time": r.processing_time,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in records
    ]
    return APIResponse(success=True, data=data)
