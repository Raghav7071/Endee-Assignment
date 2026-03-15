"""
modules/document_loader.py

Multi-format document loader. Extracts text and basic metadata from:
  - PDF  (.pdf)  → PyPDF2, page-by-page
  - TXT  (.txt)  → plain read
  - MD   (.md)   → plain read (markdown)
  - CSV  (.csv)  → pandas, row-to-text
  - JSON (.json) → json.load, record-to-text
"""

import json
import os
from typing import List, Dict, Any


def load_document(filepath: str, original_filename: str = None) -> List[Dict[str, Any]]:
    """
    Load a document and return a list of pages/records.

    Each item is a dict:
      {
        "text":        str,   # raw text content
        "page":        int,   # page number (1-indexed) or record index
        "filename":    str    # original filename
      }

    Raises ValueError for unsupported formats.
    """
    filename = original_filename if original_filename else os.path.basename(filepath)
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".pdf":
        return _load_pdf(filepath, filename)
    elif ext in (".txt", ".md"):
        return _load_text(filepath, filename)
    elif ext == ".csv":
        return _load_csv(filepath, filename)
    elif ext == ".json":
        return _load_json(filepath, filename)
    else:
        raise ValueError(f"Unsupported file type: {ext}. Supported: pdf, txt, md, csv, json")




def _load_pdf(filepath: str, filename: str) -> List[Dict[str, Any]]:
    """Extract text page-by-page from a PDF."""
    try:
        import PyPDF2
    except ImportError:
        raise ImportError("PyPDF2 is required for PDF loading: pip install PyPDF2")

    pages = []
    with open(filepath, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            text = text.strip()
            if text:
                pages.append({
                    "text": text,
                    "page": page_num,
                    "filename": filename,
                })
    return pages


def _load_text(filepath: str, filename: str) -> List[Dict[str, Any]]:
    """Load a plain text or markdown file as a single page."""
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read().strip()
    if not content:
        return []
    return [{"text": content, "page": 1, "filename": filename}]


def _load_csv(filepath: str, filename: str) -> List[Dict[str, Any]]:
    """Load CSV and convert each row to a text record."""
    try:
        import pandas as pd
    except ImportError:
        raise ImportError("pandas is required for CSV loading: pip install pandas")

    df = pd.read_csv(filepath, dtype=str).fillna("")
    records = []
    for idx, row in df.iterrows():
        text = " | ".join(f"{col}: {val}" for col, val in row.items() if val.strip())
        if text:
            records.append({"text": text, "page": idx + 1, "filename": filename})
    return records


def _load_json(filepath: str, filename: str) -> List[Dict[str, Any]]:
    """Load JSON and convert each record/key to text."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = []

    # Handle list of objects
    if isinstance(data, list):
        for idx, item in enumerate(data):
            text = json.dumps(item, ensure_ascii=False, indent=2) if isinstance(item, dict) else str(item)
            records.append({"text": text, "page": idx + 1, "filename": filename})
    # Handle single object
    elif isinstance(data, dict):
        for idx, (key, value) in enumerate(data.items()):
            text = f"{key}: {json.dumps(value, ensure_ascii=False)}"
            records.append({"text": text, "page": idx + 1, "filename": filename})
    else:
        records.append({"text": str(data), "page": 1, "filename": filename})

    return records
