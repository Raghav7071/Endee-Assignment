"""
modules/rag_pipeline.py

End-to-end Retrieval Augmented Generation (RAG) pipeline.

Flow:
  User Question
    → embed_query()
    → query_similar() in Endee
    → Retrieve top-K chunks
    → Build prompt with context
    → Call Groq LLM
    → Return {answer, sources}
"""

import sys
import os
import requests
from typing import List, Dict, Any, Optional

# Resolve backend path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend"))

from config import GROQ_API_KEY, GROQ_MODEL, TOP_K
from modules.embedding_generator import embed_query
from modules.vector_store import query_similar

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """You are an expert AI Assistant specializing in Indian Government Schemes and policy documents.

You are given relevant context chunks retrieved from a vector database. Your job is to:
1. Answer the user's question ACCURATELY and COMPREHENSIVELY based on the provided context.
2. Format your answer in clean, readable Markdown (use headers, bullet points, bold text).
3. Be detailed and professional — do NOT give short 2-sentence answers.
4. If the answer is not in the context, say: "I could not find relevant information in the uploaded documents."
5. NEVER make up facts. Only use information from the provided context.

At the end of your answer, briefly mention which document(s) the information came from."""


def run_rag(
    question: str,
    top_k: Optional[int] = None,
    index_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run the full RAG pipeline for a given user question.

    Returns:
      {
        "question":   str,
        "answer":     str,
        "sources":    List[{filename, page_number, chunk_id, score, preview}],
        "source_type": "llm" | "retrieval",
        "num_results": int,
      }
    """
    if top_k is None:
        top_k = TOP_K

    # 1. Embed the query
    query_vector = embed_query(question)

    # 2. Retrieve similar chunks from Endee
    kwargs = {}
    if index_name:
        kwargs["index_name"] = index_name
    retrieved = query_similar(query_vector, top_k=top_k, **kwargs)

    # Filter out low-confidence matches (prevent hallucinating from unrelated docs)
    retrieved = [r for r in retrieved if r["score"] >= 0.20]

    if not retrieved:
        return {
            "question": question,
            "answer": "I could not find relevant information in the uploaded documents. Please ensure the documents contain the answer, or try rephrasing your question.",
            "sources": [],
            "source_type": "none",
            "num_results": 0,
        }

    # 3. Build context from retrieved chunks
    context_parts = []
    for i, chunk in enumerate(retrieved, 1):
        doc_ref = f"[Doc {i}: {chunk['filename']} — Page {chunk['page_number']}]"
        context_parts.append(f"{doc_ref}\n{chunk['text']}")
    context = "\n\n---\n\n".join(context_parts)

    # 4. Try LLM synthesis
    llm_answer = _call_groq(question, context) if _is_llm_available() else None

    # 5. Fallback to best retrieved chunk
    answer = llm_answer or retrieved[0]["text"]
    source_type = "llm" if llm_answer else "retrieval"

    return {
        "question": question,
        "answer": answer,
        "sources": retrieved,
        "source_type": source_type,
        "num_results": len(retrieved),
    }


def _is_llm_available() -> bool:
    return bool(GROQ_API_KEY and GROQ_API_KEY.strip())


def _call_groq(question: str, context: str) -> Optional[str]:
    """Call Groq API with context + question and return the answer string."""
    try:
        resp = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": GROQ_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"Context:\n\n{context}\n\n---\n\nQuestion: {question}",
                    },
                ],
                "temperature": 0.3,
                "max_tokens": 2048,
            },
            timeout=45,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[RAG] LLM call failed: {e}")
        return None
