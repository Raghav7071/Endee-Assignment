"""
llm.py — optional LLM layer using Groq (free tier).
if no API key is set, the app still works — just returns raw retrieved text.
"""

import requests
from config import GROQ_API_KEY, GROQ_MODEL

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def is_llm_available():
    return bool(GROQ_API_KEY and GROQ_API_KEY.strip())


def generate_answer(query, context_docs):
    """send retrieved docs + user query to groq and get a natural answer"""
    if not is_llm_available():
        return None

    # build context from retrieved documents
    context = "\n\n".join([f"Document {i+1}:\n{doc}" for i, doc in enumerate(context_docs)])

    system_msg = (
        "You are an expert AI Assistant specializing in Indian Government Schemes. "
        "Analyze the provided context documents thoroughly to answer the user's question in EXTREME DETAIL. "
        "Your response MUST be formatted beautifully in Markdown, utilizing headers, bold text highlights, "
        "and bullet points for readability. DO NOT provide a short 3-sentence summary. Be highly informative "
        "and professional. If the exact answer is not in the context, synthesize the closest relevant information, "
        "but clarify any assumptions."
    )

    try:
        resp = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": GROQ_MODEL,
                "messages": [
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
                ],
                "temperature": 0.3,
                "max_tokens": 2048
            },
            timeout=30
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    except Exception as e:
        print(f"LLM call failed: {e}")
        return None
