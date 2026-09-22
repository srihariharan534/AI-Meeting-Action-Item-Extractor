"""Extraction orchestration service integrating AI provider, date intelligence, and validation."""

import time
from typing import Dict, Any
from sqlalchemy.orm import Session
from src.database.repositories import (
    MeetingRepository,
    SegmentRepository,
    ActionItemRepository,
    DecisionRepository,
)
from src.extraction import get_ai_provider
from src.validation.date_validator import normalize_deadline
from src.validation.confidence import calculate_extraction_confidence
from src.validation.rules import run_validation_rules
from src.logging_config import logger


class ExtractionService:
    def __init__(self, db: Session):
        self.db = db
        self.meeting_repo = MeetingRepository(db)
        self.segment_repo = SegmentRepository(db)
        self.action_item_repo = ActionItemRepository(db)
        self.decision_repo = DecisionRepository(db)

    def process_meeting(self, meeting_id: str, provider_name: str = "") -> Dict[str, Any]:
        """Execute end-to-end extraction, evidence grounding, date normalization, and validation."""
        start_time = time.time()
        meeting = self.meeting_repo.get_by_id(meeting_id)
        if not meeting:
            raise ValueError(f"Meeting not found: {meeting_id}")

        self.meeting_repo.update_status(meeting_id, "processing")
        segments = self.segment_repo.get_by_meeting(meeting_id)
        seg_dicts = [
            {
                "segment_id": s.segment_id,
                "speaker": s.speaker,
                "cleaned_text": s.cleaned_text,
                "sequence_number": s.sequence_number,
            }
            for s in segments
        ]

        ai_provider = get_ai_provider(provider_name)
        meeting_meta = {
            "title": meeting.title,
            "meeting_date": meeting.meeting_date.strftime("%Y-%m-%d") if meeting.meeting_date else "2026-09-18",
            "meeting_type": meeting.meeting_type,
        }

        # AI Extraction
        raw_extraction = ai_provider.extract_action_items_and_decisions(seg_dicts, meeting_meta)
        raw_actions = raw_extraction.get("action_items", [])
        raw_decisions = raw_extraction.get("decisions", [])

        processed_actions = []
        review_count = 0

        # Segment lookup for evidence grounding validation
        seg_id_set = {s.segment_id for s in segments}

        for item in raw_actions:
            task = item.get("task", "").strip()
            owner = item.get("owner")
            owner_conf = item.get("owner_confidence", 1.0)
            raw_deadline = item.get("deadline_text_original")
            evidence = item.get("evidence", "").strip()
            seg_ids = [sid for sid in item.get("evidence_segment_ids", []) if sid in seg_id_set]

            # 1. Deadline Intelligence & Normalization
            norm_date, d_type, d_ambig = normalize_deadline(raw_deadline, meeting.meeting_date)

            # 2. Validation Rules Pre-check
            temp_task_dict = {
                "task": task,
                "owner": owner,
                "deadline": norm_date,
                "deadline_text_original": raw_deadline,
                "deadline_type": d_type,
                "evidence": evidence,
                "confidence": item.get("confidence", 0.90),
            }
            flags, issues, req_review = run_validation_rules(temp_task_dict, meeting.meeting_date)
            if d_ambig and d_ambig not in item.get("ambiguities", []):
                item.setdefault("ambiguities", []).append(d_ambig)

            # 3. Transparent Confidence Calculation
            overall_conf, conf_breakdown, conf_reasons = calculate_extraction_confidence(
                task=task,
                owner=owner or "",
                owner_conf=owner_conf,
                deadline_type=d_type,
                evidence=evidence,
                validation_flags=flags,
            )

            # Low confidence triggers review
            if overall_conf < 0.70 and not req_review:
                req_review = True
                if "low_confidence" not in flags:
                    flags.append("low_confidence")

            if req_review:
                review_count += 1

            status_val = "needs_review" if req_review else item.get("status", "pending")

            action_data = {
                "meeting_id": meeting_id,
                "task": task,
                "description": item.get("description") or task,
                "owner": owner,
                "owner_confidence": owner_conf,
                "deadline": norm_date,
                "deadline_text_original": raw_deadline,
                "deadline_type": d_type,
                "priority": item.get("priority", "medium").lower(),
                "status": status_val,
                "action_type": item.get("action_type", "other").lower(),
                "confidence": overall_conf,
                "evidence": evidence,
                "evidence_segment_ids": seg_ids if seg_ids else ([segments[0].segment_id] if segments else []),
                "ambiguities": item.get("ambiguities", []),
                "validation_flags": flags,
                "requires_review": req_review,
                "review_status": "pending",
                "review_comment": None,
            }
            processed_actions.append(action_data)

        # Process decisions
        processed_decisions = []
        for d in raw_decisions:
            dec_seg_ids = [sid for sid in d.get("evidence_segment_ids", []) if sid in seg_id_set]
            processed_decisions.append({
                "meeting_id": meeting_id,
                "decision": d.get("decision", ""),
                "decision_date": meeting.meeting_date,
                "decision_owner": d.get("decision_owner"),
                "evidence": d.get("evidence", ""),
                "evidence_segment_ids": dec_seg_ids,
                "confidence": d.get("confidence", 0.90),
                "requires_review": False,
            })

        # Persist to database
        saved_actions = self.action_item_repo.create_batch(processed_actions)
        saved_decisions = self.decision_repo.create_batch(processed_decisions)
        self.meeting_repo.update_status(meeting_id, "completed")

        elapsed = round(time.time() - start_time, 2)
        logger.info(
            f"Processed meeting {meeting_id}: {len(saved_actions)} action items, "
            f"{len(saved_decisions)} decisions in {elapsed}s"
        )

        return {
            "meeting_id": meeting_id,
            "segments_count": len(segments),
            "action_items_count": len(saved_actions),
            "decisions_count": len(saved_decisions),
            "review_required_count": review_count,
            "processing_time_seconds": elapsed,
            "provider_used": ai_provider.__class__.__name__,
            "message": "Extraction and validation completed successfully",
        }
