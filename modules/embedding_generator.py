"""
modules/embedding_generator.py

Generates vector embeddings for text chunks using the SentenceTransformer model.
Implements a two-level caching strategy to avoid redundant computation:

  1. In-memory: dict stored in st.session_state["embed_cache"]
  2. Persistent: data/cache/embed_cache.json (SHA-256 hash → "already_stored" flag)

The persistent cache tells us whether a chunk (by content hash) has already been
upserted into Endee, so we can skip re-embedding AND re-uploading across restarts.
"""

import hashlib
import json
import os
from typing import List, Dict, Any, Optional


_model = None


_CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "cache")
_CACHE_FILE = os.path.join(_CACHE_DIR, "embed_cache.json")


def _get_model():
    """Lazy-load the SentenceTransformer model (loads once per process)."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend"))
        from config import EMBEDDING_MODEL
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def content_hash(text: str) -> str:
    """Return SHA-256 hex digest of text — used as cache key."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _load_persistent_cache() -> Dict[str, bool]:
    """Load the persistent cache from disk."""
    os.makedirs(_CACHE_DIR, exist_ok=True)
    if os.path.exists(_CACHE_FILE):
        try:
            with open(_CACHE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_persistent_cache(cache: Dict[str, bool]) -> None:
    """Save the persistent cache to disk."""
    os.makedirs(_CACHE_DIR, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump(cache, f)


def embed_chunks(
    chunks: List[Dict[str, Any]],
    progress_callback=None
) -> List[Dict[str, Any]]:
    """
    Generate embeddings for a list of chunks.
    Skips chunks whose content hash is already in the persistent cache.

    Args:
        chunks:            Output of text_chunker.chunk_pages()
        progress_callback: Optional callable(current, total) for progress UI

    Returns:
        List of chunk dicts with an added "vector" key (and "cached" bool).
        Chunks already in persistent cache are returned with cached=True and no vector
        (they don't need to be re-upserted into Endee).
    """
    model = _get_model()
    persistent_cache = _load_persistent_cache()

    # In-memory cache: hash → vector
    mem_cache: Dict[str, List[float]] = {}

    result = []
    total = len(chunks)

    for idx, chunk in enumerate(chunks):
        text = chunk["text"]
        h = content_hash(text)

        # Check persistent cache (already in Endee)
        if h in persistent_cache:
            result.append({**chunk, "cached": True, "hash": h})
            if progress_callback:
                progress_callback(idx + 1, total)
            continue

        # Check in-memory cache (same session, same text)
        if h in mem_cache:
            vector = mem_cache[h]
        else:
            vector = model.encode(text).tolist()
            mem_cache[h] = vector

        result.append({**chunk, "vector": vector, "cached": False, "hash": h})

        if progress_callback:
            progress_callback(idx + 1, total)

    return result


def mark_as_cached(hashes: List[str]) -> None:
    """Mark a list of content hashes as stored in Endee (update persistent cache)."""
    cache = _load_persistent_cache()
    for h in hashes:
        cache[h] = True
    _save_persistent_cache(cache)


def embed_query(query: str) -> List[float]:
    """Embed a single query string (no caching — queries are unique)."""
    return _get_model().encode(query).tolist()
