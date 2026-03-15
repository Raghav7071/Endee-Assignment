"""
ingest.py — reads docs from data/docs and pushes them into endee.
run this once before starting the app.
"""

import os
import sys
from endee import Endee, Precision
from embeddings import generate_embedding
from config import ENDEE_URL, INDEX_NAME, DOCS_DIR
import PyPDF2
from chunker import chunk_text

def extract_text(filepath):
    text = ""
    if filepath.endswith(".pdf"):
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    elif filepath.endswith(".txt"):
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
    return text.strip()

def ingest():
    # connect to endee
    client = Endee()
    client.set_base_url(f"{ENDEE_URL}/api/v1")
    print(f"Connected to Endee at {ENDEE_URL}")

    # create index if it doesnt exist already
    try:
        client.create_index(
            name=INDEX_NAME,
            dimension=384,  # matches MiniLM output
            space_type="cosine",
            precision=Precision.FLOAT32
        )
        print(f"Created index: {INDEX_NAME}")
    except Exception as e:
        # index probably already exists, thats fine
        print(f"Index '{INDEX_NAME}' already exists, skipping creation")

    index = client.get_index(name=INDEX_NAME)

    # find all txt and pdf files in docs folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    docs_path = os.path.normpath(os.path.join(script_dir, DOCS_DIR))

    if not os.path.exists(docs_path):
        print(f"ERROR: docs folder not found at {docs_path}")
        sys.exit(1)

    files = [f for f in os.listdir(docs_path) if f.endswith(".txt") or f.endswith(".pdf")]
    if not files:
        print("No .txt or .pdf files found")
        sys.exit(1)

    print(f"Found {len(files)} documents to ingest\n")

    # process each document
    total_chunks = 0
    for i, filename in enumerate(files, 1):
        filepath = os.path.join(docs_path, filename)
        
        try:
            content = extract_text(filepath)
        except Exception as e:
            print(f"  [{i}/{len(files)}] error reading {filename}: {e}")
            continue

        if not content:
            print(f"  [{i}/{len(files)}] skipping {filename} (empty)")
            continue

        print(f"  [{i}/{len(files)}] {filename} ({len(content)} chars)...", end=" ")

        chunks = chunk_text(content, chunk_size=800, overlap=100)
        
        for chunk_i, chunk in enumerate(chunks):
            # generate embedding and push to endee
            vector = generate_embedding(chunk)
            doc_id = filename.replace(".txt", "").replace(".pdf", "")
            chunk_id = f"{doc_id}_chunk{chunk_i}"

            index.upsert([{
                "id": chunk_id,
                "vector": vector,
                "meta": {
                    "text": chunk,
                    "source": filename
                }
            }])
            total_chunks += 1
            
        print(f"done ({len(chunks)} chunks)")

    print(f"\nAll {len(files)} documents ({total_chunks} total chunks) ingested successfully!")


if __name__ == "__main__":
    ingest()

