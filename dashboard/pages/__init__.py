import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from dashboard.pages import (
    overview,
    upload_meeting,
    meetings,
    meeting_details,
    action_items,
    review_queue,
    analytics,
    evaluation_results,
)

__all__ = [
    "overview",
    "upload_meeting",
    "meetings",
    "meeting_details",
    "action_items",
    "review_queue",
    "analytics",
    "evaluation_results",
]
