"""
modules/chatbot.py

Stateful chat session manager built on Streamlit's session_state.
Keeps a clean chat_history list and provides helper methods for
adding messages, clearing history, and rendering the conversation.
"""

import streamlit as st
from typing import List, Dict, Any, Optional


def init_session():
    """Initialize session state keys. Call once at app startup."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "uploaded_docs" not in st.session_state:
        # Tracks filenames of documents already processed this session
        st.session_state.uploaded_docs = set()

    if "embed_cache" not in st.session_state:
        # In-memory hash → True cache (complements the persistent JSON cache)
        st.session_state.embed_cache = {}


def add_user_message(content: str):
    """Append a user message to chat history."""
    st.session_state.chat_history.append({
        "role": "user",
        "content": content,
    })


def add_assistant_message(
    content: str,
    source_type: str = "llm",
    sources: Optional[List[Dict[str, Any]]] = None,
    num_results: int = 0,
):
    """Append an assistant message with optional source attribution."""
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": content,
        "source_type": source_type,
        "sources": sources or [],
        "num_results": num_results,
    })


def get_history() -> List[Dict[str, Any]]:
    """Return the full chat history list."""
    return st.session_state.get("chat_history", [])


def clear_history():
    """Reset the chat history."""
    st.session_state.chat_history = []


def mark_document_uploaded(filename: str):
    """Track that a document has been processed this session."""
    st.session_state.uploaded_docs.add(filename)


def is_document_uploaded(filename: str) -> bool:
    """Check if a document was already uploaded this session."""
    return filename in st.session_state.get("uploaded_docs", set())


def get_uploaded_docs() -> List[str]:
    """Return list of uploaded document names for this session."""
    return sorted(st.session_state.get("uploaded_docs", set()))
