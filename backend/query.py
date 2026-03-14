"""
query.py — handles semantic search against endee.
takes a user question, embeds it, searches endee, optionally generates an LLM answer.
"""

from endee import Endee
from embeddings import generate_embedding
from llm import generate_answer, is_llm_available
from config import ENDEE_URL, INDEX_NAME, TOP_K


def search(query, top_k=None):
    if top_k is None:
        top_k = TOP_K

    # embed the query
    query_vector = generate_embedding(query)

    # search endee for similar docs
    client = Endee()
    client.set_base_url(f"{ENDEE_URL}/api/v1")
    index = client.get_index(name=INDEX_NAME)

    try:
        results = index.query(vector=query_vector, top_k=top_k)
    except Exception as e:
        return {
            "query": query,
            "error": f"Search failed: {e}",
            "results": [],
            "answer": None
        }

    # pull out the document texts from results
    retrieved_docs = []
    formatted = []

    for r in results:
        meta = r.get("meta", {}) if isinstance(r, dict) else getattr(r, "meta", {})
        doc_text = meta.get("text", "") if isinstance(meta, dict) else ""
        score = r.get("similarity", 0) if isinstance(r, dict) else getattr(r, "similarity", 0)
        doc_id = r.get("id", "?") if isinstance(r, dict) else getattr(r, "id", "?")
        source = meta.get("source", "unknown") if isinstance(meta, dict) else "unknown"

        if doc_text:
            retrieved_docs.append(doc_text)

        formatted.append({
            "id": doc_id,
            "score": round(float(score), 4) if score else 0,
            "source": source,
            "preview": doc_text[:200] + "..." if len(doc_text) > 200 else doc_text
        })

    # try to generate an LLM answer if groq key is set
    llm_answer = None
    if retrieved_docs and is_llm_available():
        llm_answer = generate_answer(query, retrieved_docs)

    return {
        "query": query,
        "results": formatted,
        "answer": llm_answer if llm_answer else (retrieved_docs[0][:300] if retrieved_docs else "No relevant docs found."),
        "source": "llm" if llm_answer else "retrieval",
        "num_results": len(formatted)
    }
