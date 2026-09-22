"""Text cleaning and normalization for meeting transcripts."""

import re


def clean_text(text: str) -> str:
    """Clean unneeded carriage returns, irregular whitespace, and control characters."""
    if not text:
        return ""

    # Normalize carriage returns
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove non-printable control characters except \n and \t
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    # Normalize repetitive whitespace within lines
    lines = []
    for line in text.split("\n"):
        cleaned_line = re.sub(r"[ \t]+", " ", line).strip()
        lines.append(cleaned_line)

    # Collapse more than 2 consecutive blank lines
    result = re.sub(r"\n{3,}", "\n\n", "\n".join(lines))
    return result.strip()
