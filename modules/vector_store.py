"""
modules/vector_store.py

Clean abstraction over the Endee Vector Database.
Handles:
  - Index creation / retrieval
  - Batch upsert with full metadata
  - Similarity search returning structured results
"""

import sys
import os
from typing import List, Dict, Any, Optional

# Resolve backend path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend"))

from endee import Endee, Precision
from config import ENDEE_URL, INDEX_NAME


def _get_client() -> Endee:
    client = Endee()
    client.set_base_url(f"{ENDEE_URL}/api/v1")
    return client


def get_or_create_index(index_name: str = INDEX_NAME, dimension: int = 384):
    """
    Return an Endee index, creating it if it doesn't already exist.

    Args:
        index_name: Name of the index
        dimension:  Vector dimension (384 for all-MiniLM-L6-v2)
    """
    client = _get_client()
    try:
        client.create_index(
            name=index_name,
            dimension=dimension,
            space_type="cosine",
            precision=Precision.FLOAT32
        )
    except Exception:
        # Already exists — that's fine
        pass
    return client.get_index(name=index_name)


def upsert_chunks(
    chunks: List[Dict[str, Any]],
    index_name: str = INDEX_NAME,
    batch_size: int = 50
) -> int:
    """
    Upsert embedded chunks into Endee. Skips chunks marked as cached.

    Args:
        chunks:     List of chunk dicts with "vector" key (from embedding_generator)
        index_name: Endee index to upsert into
        batch_size: How many vectors to push per API call

    Returns:
        Number of chunks actually upserted (excluding cache hits)
    """
    index = get_or_create_index(index_name)
    to_upsert = [c for c in chunks if not c.get("cached", False)]

    upserted = 0
    for i in range(0, len(to_upsert), batch_size):
        batch = to_upsert[i:i + batch_size]
        records = []
        for chunk in batch:
            records.append({
                "id": chunk["chunk_id"],
                "vector": chunk["vector"],
                "meta": {
                    "text": chunk["text"],
                    "filename": chunk["filename"],
                    "page_number": chunk["page_number"],
                    "chunk_id": chunk["chunk_id"],
                }
            })
        index.upsert(records)
        upserted += len(records)

    return upserted


def query_similar(
    vector: List[float],
    top_k: int = 5,
    index_name: str = INDEX_NAME
) -> List[Dict[str, Any]]:
    """
    Perform semantic search against Endee.

    Returns a list of result dicts:
      {
        "text":        str,
        "filename":    str,
        "page_number": int,
        "chunk_id":    str,
        "score":       float,
        "preview":     str  (first 200 chars of text)
      }
    """
    index = get_or_create_index(index_name)

    try:
        raw_results = index.query(vector=vector, top_k=top_k)
    except Exception as e:
        raise RuntimeError(f"Endee query failed: {e}")

    results = []
    for r in raw_results:
        meta = r.get("meta", {}) if isinstance(r, dict) else getattr(r, "meta", {})
        if not isinstance(meta, dict):
            meta = {}

        text = meta.get("text", "")
        score = r.get("similarity", 0) if isinstance(r, dict) else getattr(r, "similarity", 0)

        results.append({
            "text": text,
            "filename": meta.get("filename", meta.get("source", "Unknown Document")),
            "page_number": meta.get("page_number", 1),
            "chunk_id": meta.get("chunk_id", r.get("id", "?") if isinstance(r, dict) else getattr(r, "id", "?")),
            "score": round(float(score), 4) if score else 0.0,
            "preview": text[:200] + "..." if len(text) > 200 else text,
        })

    return results
