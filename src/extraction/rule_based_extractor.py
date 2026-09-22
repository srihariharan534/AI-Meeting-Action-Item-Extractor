"""Rule-based pattern matching extractor for baseline performance and offline operation."""

import re
from typing import List, Dict, Any
from src.extraction.base import LLMProvider
from src.logging_config import logger

# Modals and commitment triggers
COMMITMENT_TRIGGERS = [
    r"\bI will\b",
    r"\bI'll\b",
    r"\bI can\b",
    r"\bI am going to\b",
    r"\bwe will\b",
    r"\bwe must\b",
    r"\bwe need to\b",
]

ASSIGNMENT_TRIGGERS = [
    r"\bplease\b",
    r"\bneeds to\b",
    r"\bmust\b",
    r"\bcan you\b",
    r"\bwill prepare\b",
    r"\bwill review\b",
    r"\bwill handle\b",
]

DECISION_TRIGGERS = [
    r"\bwe decided to\b",
    r"\bagreed that\b",
    r"\bthe decision is to\b",
    r"\bdecided to\b",
]

DEADLINE_PATTERNS = [
    r"\bby (?:next )?(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b",
    r"\bbefore (?:next )?(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b",
    r"\bby tomorrow\b",
    r"\bby today\b",
    r"\bby next week\b",
    r"\bby month-?end\b",
    r"\bby end of (?:this )?week\b",
    r"\bwithin \d+ (?:days|weeks)\b",
    r"\bby \d{4}-\d{2}-\d{2}\b",
    r"\bsoon\b",
]

ACTION_VERB_MAP = {
    "prepare": "prepare",
    "review": "review",
    "fix": "fix",
    "send": "send",
    "create": "create",
    "update": "update",
    "analyze": "analyze",
    "coordinate": "schedule",
    "execute": "test",
    "test": "test",
    "deploy": "deploy",
    "schedule": "schedule",
    "contact": "contact",
    "research": "research",
}


class RuleBasedExtractor(LLMProvider):
    """
    Deterministic rule-based extractor using regular expressions,
    verb identification, and speaker turn semantics.
    """

    def extract_action_items_and_decisions(
        self,
        segments: List[Dict[str, Any]],
        meeting_metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        action_items: List[Dict[str, Any]] = []
        decisions: List[Dict[str, Any]] = []

        for seg in segments:
            text = seg.get("cleaned_text", "")
            speaker = seg.get("speaker", "Unknown")
            seg_id = seg.get("segment_id", "")

            # 1. Decision extraction
            is_decision = False
            for d_trig in DECISION_TRIGGERS:
                if re.search(d_trig, text, re.IGNORECASE):
                    decisions.append({
                        "decision": text,
                        "evidence": text,
                        "evidence_segment_ids": [seg_id],
                        "confidence": 0.90,
                        "requires_review": False,
                    })
                    is_decision = True
                    break

            if is_decision:
                continue

            # 2. Skip past/completed or general questions without assignment
            if re.search(r"\balready (?:resolved|completed|done|fixed)\b", text, re.IGNORECASE):
                continue
            if text.endswith("?") and not any(re.search(p, text, re.IGNORECASE) for p in [r"\bcan you\b", r"\bcould you\b"]):
                continue

            # 3. Action Item Detection
            is_action = False
            owner = None
            owner_conf = 0.50
            matched_trigger = None

            # Check personal commitment: "I will prepare..." -> owner is speaker
            for comm in COMMITMENT_TRIGGERS:
                if re.search(comm, text, re.IGNORECASE):
                    is_action = True
                    owner = speaker if speaker != "Unknown" else None
                    owner_conf = 0.95 if owner else 0.40
                    matched_trigger = "commitment"
                    break

            # Check direct assignment: "Arun, please prepare..." or "Priya needs to..."
            if not is_action:
                # Name followed by comma or 'please'
                assign_match = re.search(r"^([A-Z][a-z]+)[,\s]+(?:please\s+)?([a-z].*)", text, re.IGNORECASE)
                if assign_match and any(re.search(trig, text, re.IGNORECASE) for trig in ASSIGNMENT_TRIGGERS):
                    is_action = True
                    owner = assign_match.group(1)
                    owner_conf = 0.90
                    matched_trigger = "assignment"
                elif any(re.search(trig, text, re.IGNORECASE) for trig in ASSIGNMENT_TRIGGERS):
                    # Check if someone mentioned
                    for name in ["Arun", "Priya", "Meena", "Rohan", "Suresh", "Kavita"]:
                        if name in text:
                            owner = name
                            owner_conf = 0.85
                            break
                    is_action = True
                    matched_trigger = "assignment"

            # Check general need: "We need someone to..."
            if not is_action and re.search(r"\b(?:someone needs? to|need someone to)\b", text, re.IGNORECASE):
                is_action = True
                owner = None
                owner_conf = 0.30
                matched_trigger = "unassigned_request"

            if is_action:
                # Extract deadline phrase
                deadline_phrase = None
                for d_pat in DEADLINE_PATTERNS:
                    d_match = re.search(d_pat, text, re.IGNORECASE)
                    if d_match:
                        deadline_phrase = d_match.group(0).strip()
                        break

                # Determine action type
                action_type = "other"
                lower_text = text.lower()
                for verb, act_type in ACTION_VERB_MAP.items():
                    if f" {verb} " in f" {lower_text} ":
                        action_type = act_type
                        break

                # Formulate task title
                task_title = text
                # Trim speaker or addressing prefix
                if owner and text.startswith(owner):
                    task_title = text[len(owner):].lstrip(",: -")

                # Clean up to imperative title
                for prefix in ["I will ", "I'll ", "please ", "Sure, I will ", "Sure, "]:
                    if task_title.lower().startswith(prefix.lower()):
                        task_title = task_title[len(prefix):]

                task_title = task_title.strip()
                if len(task_title) > 0:
                    task_title = task_title[0].upper() + task_title[1:]

                # Ambiguities & confidence
                ambiguities = []
                confidence = 0.85
                if not owner:
                    ambiguities.append("No explicit owner assigned")
                    confidence -= 0.15
                if deadline_phrase == "soon":
                    ambiguities.append("Ambiguous relative deadline ('soon')")
                    confidence -= 0.10

                action_items.append({
                    "task": task_title[:150],
                    "description": text,
                    "owner": owner,
                    "owner_confidence": owner_conf,
                    "deadline_text_original": deadline_phrase,
                    "deadline_type": "relative_date" if deadline_phrase and deadline_phrase != "soon" else ("ambiguous" if deadline_phrase == "soon" else "missing"),
                    "priority": "high" if "urgent" in lower_text or "proposal" in lower_text else "medium",
                    "status": "pending",
                    "action_type": action_type,
                    "confidence": max(0.40, round(confidence, 2)),
                    "evidence": text,
                    "evidence_segment_ids": [seg_id],
                    "ambiguities": ambiguities,
                })

        return {"action_items": action_items, "decisions": decisions}
