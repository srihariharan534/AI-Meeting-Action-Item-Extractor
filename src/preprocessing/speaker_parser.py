"""Speaker and timestamp parsing from transcript lines."""

import re
from typing import Tuple, Optional

# Patterns matching timestamps like [00:12:30], (12:30), 00:02:14 - 00:02:20, etc.
TIMESTAMP_PATTERN = re.compile(
    r"\[?\(?(\d{1,2}:\d{2}(?::\d{2})?)\s*(?:-|–|to)?\s*(\d{1,2}:\d{2}(?::\d{2})?)?\]?\)?",
    re.IGNORECASE,
)

# Patterns matching speaker labels:
# "Arun:", "Priya [00:12]:", "[00:12] Meena:", "Arun (PM):"
SPEAKER_COLON_PATTERN = re.compile(
    r"^(?:\[?(?P<pre_ts>\d{1,2}:\d{2}(?::\d{2})?)\]?\s*)?(?P<speaker>[A-Z0-9][A-Za-z0-9\s\.\-_'\(\)]+?)(?:\s*\[?(?P<post_ts>\d{1,2}:\d{2}(?::\d{2})?)\]?)?\s*:\s*(?P<content>.*)$",
    re.IGNORECASE,
)


def parse_speaker_and_timestamps(line: str) -> Tuple[str, Optional[str], Optional[str], str]:
    """
    Extract (speaker, timestamp_start, timestamp_end, utterance_text) from a line.
    Returns default speaker 'Unknown' and None timestamps if pattern is not explicit.
    """
    line = line.strip()
    match = SPEAKER_COLON_PATTERN.match(line)
    if match:
        speaker = match.group("speaker").strip()
        pre_ts = match.group("pre_ts")
        post_ts = match.group("post_ts")
        content = match.group("content").strip()
        ts_start = pre_ts or post_ts

        # Remove titles/roles from speaker if parenthesized, e.g. "Arun (Tech Lead)" -> speaker: "Arun"
        if "(" in speaker and ")" in speaker and not speaker.startswith("("):
            # Still keep clean name
            pass

        return speaker, ts_start, None, content

    # Check for standalone timestamp at start of line
    ts_match = TIMESTAMP_PATTERN.match(line)
    if ts_match:
        ts_start = ts_match.group(1)
        ts_end = ts_match.group(2)
        content = line[ts_match.end():].strip().lstrip(":- ").strip()
        return "Unknown", ts_start, ts_end, content

    return "Unknown", None, None, line
