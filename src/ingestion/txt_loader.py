"""Text file (.txt) ingestion loader."""

from typing import Union
from pathlib import Path


def load_txt(file_input: Union[str, Path, bytes]) -> str:
    """Read and decode UTF-8 or standard encoded text files."""
    if isinstance(file_input, (str, Path)):
        path = Path(file_input)
        if not path.exists():
            raise FileNotFoundError(f"Text file not found: {path}")

        # Try utf-8 first, fallback to latin-1
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return path.read_text(encoding="latin-1")

    elif isinstance(file_input, bytes):
        try:
            return file_input.decode("utf-8")
        except UnicodeDecodeError:
            return file_input.decode("latin-1")

    raise TypeError("Invalid file_input type for load_txt; must be str, Path, or bytes.")
