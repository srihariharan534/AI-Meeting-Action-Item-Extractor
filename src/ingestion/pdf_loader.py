"""PDF document ingestion loader."""

import io
from typing import Union
from pathlib import Path
from pypdf import PdfReader


def load_pdf(file_input: Union[str, Path, bytes]) -> str:
    """Extract raw text from PDF document."""
    if isinstance(file_input, (str, Path)):
        path = Path(file_input)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {path}")
        reader = PdfReader(str(path))
    elif isinstance(file_input, bytes):
        reader = PdfReader(io.BytesIO(file_input))
    else:
        raise TypeError("Invalid file_input type for load_pdf; must be str, Path, or bytes.")

    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)

    return "\n\n".join(text_parts)
