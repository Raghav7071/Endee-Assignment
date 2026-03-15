"""
ingest.py — reads docs from data/docs and pushes them into endee.
run this once before starting the app.
"""

import os
import sys
from endee import Endee, Precision
from embeddings import generate_embedding
from config import ENDEE_URL, INDEX_NAME, DOCS_DIR


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
    except Exception:
        # index probably already exists, thats fine
        print(f"Index '{INDEX_NAME}' already exists, skipping creation")

    index = client.get_index(name=INDEX_NAME)

    # find all txt files in docs folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    docs_path = os.path.normpath(os.path.join(script_dir, DOCS_DIR))

    if not os.path.exists(docs_path):
        print(f"ERROR: docs folder not found at {docs_path}")
        sys.exit(1)

    files = [f for f in os.listdir(docs_path) if f.endswith(".txt")]
    if not files:
        print("No .txt files found")
        sys.exit(1)

    print(f"Found {len(files)} documents to ingest\n")

    # process each document
    for i, filename in enumerate(files, 1):
        filepath = os.path.join(docs_path, filename)

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()

        if not content:
            print(f"  [{i}/{len(files)}] skipping {filename} (empty)")
            continue

        print(f"  [{i}/{len(files)}] {filename} ({len(content)} chars)...", end=" ")

        # generate embedding and push to endee
        vector = generate_embedding(content)
        doc_id = filename.replace(".txt", "")

        index.upsert([{
            "id": doc_id,
            "vector": vector,
            "meta": {
                "text": content,
                "source": filename
            }
        }])

        print("done")

    print(f"\nAll {len(files)} documents ingested successfully!")


if __name__ == "__main__":
    ingest()
