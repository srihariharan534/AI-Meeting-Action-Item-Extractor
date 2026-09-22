"""Quantitative evaluation metrics for action-item detection, fields, and grounding."""

from typing import List, Dict, Any, Tuple
from src.deduplication.similarity import compute_text_similarity


def evaluate_action_item_extractions(
    predictions: List[Dict[str, Any]],
    ground_truth: List[Dict[str, Any]],
    similarity_match_threshold: float = 0.50,
) -> Dict[str, float]:
    """
    Empirically evaluate extracted action items against gold annotations:
    - Precision, Recall, F1
    - Owner accuracy
    - Deadline accuracy
    - Evidence grounding score
    """
    if not ground_truth and not predictions:
        return {
            "precision": 1.0,
            "recall": 1.0,
            "f1_score": 1.0,
            "owner_accuracy": 1.0,
            "deadline_accuracy": 1.0,
            "evidence_grounding_score": 1.0,
        }

    if not ground_truth and predictions:
        return {
            "precision": 0.0,
            "recall": 1.0,
            "f1_score": 0.0,
            "owner_accuracy": 0.0,
            "deadline_accuracy": 0.0,
            "evidence_grounding_score": 0.0,
        }

    if ground_truth and not predictions:
        return {
            "precision": 0.0,
            "recall": 0.0,
            "f1_score": 0.0,
            "owner_accuracy": 0.0,
            "deadline_accuracy": 0.0,
            "evidence_grounding_score": 0.0,
        }

    matched_pred_indices = set()
    matched_gt_indices = set()

    owner_matches = 0
    deadline_matches = 0
    grounded_count = 0

    # Match each prediction to most similar ground truth
    for p_idx, pred in enumerate(predictions):
        p_task = pred.get("task", "")
        p_evidence = pred.get("evidence", "")

        best_sim = 0.0
        best_gt_idx = -1

        for g_idx, gt in enumerate(ground_truth):
            if g_idx in matched_gt_indices:
                continue
            g_task = gt.get("task", "")
            sim = compute_text_similarity(p_task, g_task)
            if sim > best_sim:
                best_sim = sim
                best_gt_idx = g_idx

        if best_sim >= similarity_match_threshold and best_gt_idx >= 0:
            matched_pred_indices.add(p_idx)
            matched_gt_indices.add(best_gt_idx)

            gt_item = ground_truth[best_gt_idx]

            # Owner accuracy
            p_owner = (pred.get("owner") or "").lower()
            g_owner = (gt_item.get("owner") or "").lower()
            if p_owner == g_owner or (not p_owner and not g_owner):
                owner_matches += 1

            # Deadline accuracy
            p_dead = (pred.get("deadline_text_original") or "").lower()
            g_dead = (gt_item.get("deadline_text_original") or "").lower()
            if p_dead == g_dead or (not p_dead and not g_dead):
                deadline_matches += 1

        # Evidence grounding check: does evidence contain substantial non-empty citation?
        if p_evidence and len(p_evidence.strip()) > 10:
            grounded_count += 1

    tp = len(matched_pred_indices)
    fp = len(predictions) - tp
    fn = len(ground_truth) - len(matched_gt_indices)

    precision = round(tp / (tp + fp), 3) if (tp + fp) > 0 else 0.0
    recall = round(tp / (tp + fn), 3) if (tp + fn) > 0 else 0.0
    f1 = round(2 * precision * recall / (precision + recall), 3) if (precision + recall) > 0 else 0.0

    owner_acc = round(owner_matches / tp, 3) if tp > 0 else 0.0
    deadline_acc = round(deadline_matches / tp, 3) if tp > 0 else 0.0
    grounding_score = round(grounded_count / len(predictions), 3) if predictions else 0.0

    return {
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "owner_accuracy": owner_acc,
        "deadline_accuracy": deadline_acc,
        "evidence_grounding_score": grounding_score,
    }
