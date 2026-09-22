"""Transcript chunking for long meeting inputs."""

from typing import List, Dict, Any


def chunk_segments(
    segments: List[Dict[str, Any]],
    max_tokens_approx: int = 1500,
    overlap_segments: int = 2,
) -> List[List[Dict[str, Any]]]:
    """
    Chunk segments into manageable windows for LLM processing with overlap.
    Assumes average 1 token ≈ 4 characters for conservative estimate.
    """
    if not segments:
        return []

    chunks: List[List[Dict[str, Any]]] = []
    current_chunk: List[Dict[str, Any]] = []
    current_chars = 0
    max_chars = max_tokens_approx * 4

    for seg in segments:
        seg_len = len(seg.get("cleaned_text", "")) + len(seg.get("speaker", "")) + 20
        if current_chars + seg_len > max_chars and current_chunk:
            chunks.append(list(current_chunk))
            # Retain overlap from end of current chunk
            overlap = current_chunk[-overlap_segments:] if overlap_segments > 0 else []
            current_chunk = list(overlap)
            current_chars = sum(len(s.get("cleaned_text", "")) + 20 for s in current_chunk)

        current_chunk.append(seg)
        current_chars += seg_len

    if current_chunk:
        chunks.append(current_chunk)

    return chunks
