"""
modules/text_chunker.py

Splits loaded document pages into overlapping chunks using a
RecursiveCharacterTextSplitter-style algorithm.

Each chunk includes metadata:
  - filename
  - page_number
  - chunk_id  (e.g. "my_doc.pdf_p1_c0")
"""

import re
from typing import List, Dict, Any


# Separator hierarchy (try to split on paragraphs, then sentences, then words)
_SEPARATORS = ["\n\n", "\n", ". ", "! ", "? ", " ", ""]


def chunk_pages(
    pages: List[Dict[str, Any]],
    chunk_size: int = 700,
    chunk_overlap: int = 100,
) -> List[Dict[str, Any]]:
    """
    Chunk a list of pages (from document_loader) into smaller pieces.

    Args:
        pages:         Output of document_loader.load_document()
        chunk_size:    Target max chars per chunk
        chunk_overlap: How many trailing chars to carry into next chunk

    Returns:
        List of chunk dicts:
          {
            "text":        str,
            "filename":    str,
            "page_number": int,
            "chunk_id":    str,
          }
    """
    all_chunks: List[Dict[str, Any]] = []

    for page in pages:
        raw_text = page["text"]
        filename = page["filename"]
        page_num = page["page"]

        # Generate base slug for chunk IDs
        slug = re.sub(r"[^a-zA-Z0-9_]", "_", filename)

        texts = _recursive_split(raw_text, chunk_size, chunk_overlap)

        for chunk_idx, text in enumerate(texts):
            chunk_id = f"{slug}_p{page_num}_c{chunk_idx}"
            all_chunks.append({
                "text": text,
                "filename": filename,
                "page_number": page_num,
                "chunk_id": chunk_id,
            })

    return all_chunks



# Core splitting logic (RecursiveCharacterTextSplitter equivalent)


def _recursive_split(text: str, chunk_size: int, overlap: int) -> List[str]:
    """Recursively split text using separator hierarchy."""
    if len(text) <= chunk_size:
        return [text] if text.strip() else []

    for sep in _SEPARATORS:
        if sep == "":
            # Fallback: hard split by character count
            return _hard_split(text, chunk_size, overlap)

        parts = text.split(sep)
        if len(parts) > 1:
            return _merge_splits(parts, sep, chunk_size, overlap)

    return _hard_split(text, chunk_size, overlap)


def _merge_splits(parts: List[str], separator: str, chunk_size: int, overlap: int) -> List[str]:
    """Merge split parts back into chunks of the target size."""
    chunks = []
    current_chunk = ""

    for part in parts:
        part_with_sep = part if not current_chunk else separator + part
        candidate = current_chunk + part_with_sep

        if len(candidate) <= chunk_size:
            current_chunk = candidate
        else:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            # Start new chunk with overlap from end of previous
            overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
            current_chunk = overlap_text + separator + part if overlap_text else part

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def _hard_split(text: str, chunk_size: int, overlap: int) -> List[str]:
    """Last-resort character-level split."""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return [c for c in chunks if c.strip()]
