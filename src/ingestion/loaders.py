"""Unified ingestion loader dispatcher for transcripts."""

from typing import Union
from pathlib import Path
from src.ingestion.txt_loader import load_txt
from src.ingestion.pdf_loader import load_pdf
from src.ingestion.docx_loader import load_docx
from src.ingestion.validators import validate_file_extension


def load_transcript_file(
    file_input: Union[str, Path, bytes],
    filename: str,
) -> str:
    """Load and parse transcript text based on filename extension."""
    valid_ext, err = validate_file_extension(filename)
    if not valid_ext:
        raise ValueError(err)

    ext = "." + filename.rsplit(".", 1)[-1].lower()

    if ext == ".txt":
        return load_txt(file_input)
    elif ext == ".pdf":
        return load_pdf(file_input)
    elif ext == ".docx":
        return load_docx(file_input)

    raise ValueError(f"Unsupported file format: {ext}")
