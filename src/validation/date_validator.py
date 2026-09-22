"""Deadline parsing, normalization, and ambiguity validation."""

import re
from datetime import datetime, timedelta
from typing import Tuple, Optional
from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta, MO, TU, WE, TH, FR, SA, SU

WEEKDAY_MAP = {
    "monday": MO,
    "tuesday": TU,
    "wednesday": WE,
    "thursday": TH,
    "friday": FR,
    "saturday": SA,
    "sunday": SU,
}


def normalize_deadline(
    deadline_text: Optional[str],
    reference_date: Optional[datetime] = None,
) -> Tuple[Optional[datetime], str, Optional[str]]:
    """
    Safely resolve raw deadline text relative to meeting reference_date.
    Returns: (normalized_datetime, deadline_type, ambiguity_warning)
    
    deadline_type in: exact_date | relative_date | inferred_date | ambiguous | missing
    """
    if not deadline_text or not deadline_text.strip():
        return None, "missing", None

    text = deadline_text.strip().lower()
    ref = reference_date or datetime.utcnow()

    # 1. Flag ambiguous temporal phrases that cannot be safely pinned
    if text in ["soon", "later", "asap", "when possible", "sometime", "eventually"]:
        return None, "ambiguous", f"Ambiguous deadline expression: '{deadline_text}'"

    # 2. Relative keywords
    if "today" in text:
        return ref.replace(hour=18, minute=0, second=0, microsecond=0), "relative_date", None

    if "tomorrow" in text:
        target = ref + timedelta(days=1)
        return target.replace(hour=18, minute=0, second=0, microsecond=0), "relative_date", None

    if "end of this week" in text or "end of the week" in text:
        # Friday of current week
        target = ref + relativedelta(weekday=FR)
        return target.replace(hour=18, minute=0, second=0, microsecond=0), "relative_date", None

    if "next week" in text:
        target = ref + timedelta(weeks=1)
        return target.replace(hour=18, minute=0, second=0, microsecond=0), "relative_date", None

    if "month-end" in text or "end of this month" in text or "end of the month" in text:
        # Last day of current month
        next_month = ref.replace(day=28) + timedelta(days=4)
        last_day = next_month - timedelta(days=next_month.day)
        return last_day.replace(hour=18, minute=0, second=0, microsecond=0), "relative_date", None

    # 3. Within X days / weeks
    within_match = re.search(r"within\s+(\d+)\s+(day|week|month)s?", text)
    if within_match:
        num = int(within_match.group(1))
        unit = within_match.group(2)
        if unit == "day":
            target = ref + timedelta(days=num)
        elif unit == "week":
            target = ref + timedelta(weeks=num)
        else:
            target = ref + relativedelta(months=num)
        return target.replace(hour=18, minute=0, second=0, microsecond=0), "relative_date", None

    # 4. By / Before [Day of week], e.g. "by Friday", "by next Monday"
    weekday_match = re.search(r"(?:by|before|on)?\s*(next\s+)?(monday|tuesday|wednesday|thursday|friday|saturday|sunday)", text)
    if weekday_match:
        is_next = bool(weekday_match.group(1))
        day_str = weekday_match.group(2).lower()
        target_day = WEEKDAY_MAP[day_str]

        if is_next:
            # Advance to next week's occurrence
            target = ref + relativedelta(weeks=1, weekday=target_day)
        else:
            # First upcoming occurrence (or today if same weekday and before deadline time)
            target = ref + relativedelta(weekday=target_day)
            if target.date() <= ref.date():
                target = ref + relativedelta(weeks=1, weekday=target_day)

        return target.replace(hour=18, minute=0, second=0, microsecond=0), "relative_date", None

    # 5. Try parsing as exact date
    try:
        clean_date_str = re.sub(r"^(?:by|before|on|due)\s+", "", text).strip()
        parsed = date_parser.parse(clean_date_str, default=ref)
        # Verify year and month were actually specified
        return parsed.replace(hour=18, minute=0, second=0, microsecond=0), "exact_date", None
    except Exception:
        pass

    return None, "ambiguous", f"Could not safely resolve date phrase: '{deadline_text}'"
