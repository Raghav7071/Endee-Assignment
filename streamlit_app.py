import streamlit as st

# MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="GovScheme AI",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="expanded",
)

import sys
import os
import tempfile

# Add project root to path
_ROOT = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(_ROOT, "backend"))
sys.path.insert(0, _ROOT)

# RAG modules
from modules.chatbot import (
    init_session, add_user_message, add_assistant_message,
    get_history, clear_history, mark_document_uploaded,
    is_document_uploaded, get_uploaded_docs,
)
from modules.document_loader import load_document
from modules.text_chunker import chunk_pages
from modules.embedding_generator import embed_chunks, mark_as_cached
from modules.vector_store import upsert_chunks
from modules.rag_pipeline import run_rag

# ─── Initialize session ────────────────────────────────────────────────────
init_session()

# ─── CSS (minimalist design) ──────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Base */
    html, body, .stApp {
        background-color: #ffffff !important;
        font-family: 'Inter', sans-serif;
        color: #1a1a1a;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f7f7f7 !important;
        border-right: 1px solid #e8e8e8;
    }
    [data-testid="stSidebar"] * { color: #333333 !important; }
    [data-testid="stSidebar"] .stButton > button {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        transition: background 0.2s;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #333333 !important;
    }

    /* Header */
    .app-header {
        text-align: center;
        padding: 2.5rem 0 1rem 0;
        border-bottom: 1px solid #f0f0f0;
        margin-bottom: 1.5rem;
    }
    .app-title {
        font-size: 1.75rem;
        font-weight: 600;
        color: #1a1a1a;
        letter-spacing: -0.03em;
        margin-bottom: 0.35rem;
    }
    .app-subtitle {
        font-size: 0.95rem;
        color: #888888;
        font-weight: 400;
    }

    /* Answer & Source cards */
    .answer-card {
        background: #fafafa;
        border-radius: 8px;
        padding: 1.25rem 1.5rem;
        border: 1px solid #ebebeb;
        margin: 0.4rem 0;
        color: #1a1a1a;
    }
    .source-card {
        background: #ffffff;
        border: 1px solid #ebebeb;
        border-left: 3px solid #1a1a1a;
        border-radius: 6px;
        padding: 0.9rem 1.1rem;
        margin-bottom: 0.6rem;
        font-size: 0.88rem;
        color: #444444;
    }
    .source-meta {
        font-size: 0.72rem;
        color: #999999;
        margin-bottom: 0.4rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-ai {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 4px;
        background: #f0f0f0;
        color: #555555;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-bottom: 0.75rem;
    }
    .badge-retrieval {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 4px;
        background: #f0f0f0;
        color: #888888;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-bottom: 0.75rem;
    }

    /* Suggestion buttons */
    div[data-testid="stButton"] button {
        background: #ffffff !important;
        color: #333333 !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 6px !important;
        font-weight: 400 !important;
        font-size: 0.88rem !important;
        transition: border-color 0.15s, color 0.15s !important;
        width: 100% !important;
        padding: 0.65rem !important;
    }
    div[data-testid="stButton"] button:hover {
        border-color: #1a1a1a !important;
        color: #1a1a1a !important;
    }

    /* Chat input */
    .stChatInput > div > div > textarea {
        border-radius: 6px !important;
        border: 1px solid #e0e0e0 !important;
        background: #ffffff !important;
        color: #1a1a1a !important;
        font-size: 0.95rem !important;
        padding: 0.85rem 1rem !important;
    }
    .stChatInput > div > div > textarea:focus {
        border-color: #1a1a1a !important;
        box-shadow: none !important;
    }

    /* Typography */
    .stMarkdown p, .stMarkdown li {
        color: #333333 !important;
        line-height: 1.7 !important;
        font-size: 0.95rem !important;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #1a1a1a !important;
        font-weight: 600 !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: #fafafa !important;
        color: #666666 !important;
        border-radius: 6px !important;
        border: 1px solid #ebebeb !important;
        font-size: 0.88rem !important;
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#  SIDEBAR — Document Upload & Knowledge Base Manager
# ═══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 📚 Knowledge Base")
    st.markdown("Upload documents to make them searchable.")

    uploaded_files = st.file_uploader(
        "Supported: PDF, TXT, MD, CSV, JSON",
        type=["pdf", "txt", "md", "csv", "json"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded_files:
        new_files = [f for f in uploaded_files if not is_document_uploaded(f.name)]

        if new_files:
            if st.button("⚡ Process & Ingest Documents", use_container_width=True):
                for uploaded_file in new_files:
                    with st.spinner(f"Processing **{uploaded_file.name}**..."):
                        ext = os.path.splitext(uploaded_file.name)[1].lower()
                        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                            tmp.write(uploaded_file.getvalue())
                            tmp_path = tmp.name

                        try:
                            # Step 1: Load
                            pages = load_document(tmp_path, original_filename=uploaded_file.name)
                            if not pages:
                                st.warning(f"⚠️ Could not extract text from **{uploaded_file.name}**.")
                                continue

                            # Step 2: Chunk
                            chunks = chunk_pages(pages, chunk_size=700, chunk_overlap=100)
                            st.markdown(f"📄 **{uploaded_file.name}** → {len(chunks)} chunks")

                            # Step 3: Embed (with caching)
                            progress_bar = st.progress(0, text="Generating embeddings...")
                            embedded = []

                            def _progress(current, total):
                                pct = int(current / total * 100)
                                progress_bar.progress(pct, text=f"Embedding chunk {current}/{total}...")

                            embedded = embed_chunks(chunks, progress_callback=_progress)
                            progress_bar.empty()

                            # Step 4: Upsert into Endee
                            n_upserted = upsert_chunks(embedded)
                            cached_count = sum(1 for c in embedded if c.get("cached"))

                            # Step 5: Mark hashes as cached
                            mark_as_cached([c["hash"] for c in embedded if not c.get("cached")])
                            mark_document_uploaded(uploaded_file.name)

                            st.success(
                                f"✅ **{uploaded_file.name}** ingested!\n\n"
                                f"• {n_upserted} new chunks → Endee\n"
                                f"• {cached_count} chunks skipped (cached)"
                            )

                        except Exception as e:
                            st.error(f"❌ Error processing **{uploaded_file.name}**: {e}")
                        finally:
                            try:
                                os.unlink(tmp_path)
                            except Exception:
                                pass

        else:
            st.info("✓ All uploaded files are already in the knowledge base.")

    # Uploaded docs list
    docs = get_uploaded_docs()
    if docs:
        st.markdown("---")
        st.markdown("**📂 Indexed Documents (this session)**")
        for doc in docs:
            st.markdown(f"• `{doc}`")

    st.markdown("---")
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        clear_history()
        st.rerun()


# ═══════════════════════════════════════════════════════════════════
#  MAIN AREA — Chat Interface
# ═══════════════════════════════════════════════════════════════════

st.markdown("""
<div class="app-header">
    <div class="app-title">GovScheme AI</div>
    <div class="app-subtitle">Ask questions. Get AI-powered answers with source citations.</div>
</div>
""", unsafe_allow_html=True)

# ─── Chat History ────────────────────────────────────────────────
for msg in get_history():
    if msg["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant", avatar="🏛️"):
            _is_ai = msg.get("source_type") == "llm"
            _badge = "badge-ai" if _is_ai else "badge-retrieval"
            _icon = "✨" if _is_ai else "📄"
            _label = "AI Synthesized Answer" if _is_ai else "Direct Document Extraction"

            st.markdown(f"""
            <div class="answer-card">
                <div class="{_badge}">{_icon} {_label}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(msg["content"])

            # Source citations
            sources = msg.get("sources", [])
            if sources:
                with st.expander(f"📎 {len(sources)} Source(s) Used", expanded=False):
                    for s in sources:
                        fname = s.get("filename", "Unknown").replace(".pdf", "").replace(".txt", "")
                        pg = s.get("page_number", "?")
                        score = round(s.get("score", 0) * 100, 1)
                        preview = s.get("preview", "")
                        st.markdown(f"""
                        <div class="source-card">
                            <div class="source-meta">
                                📄 {fname} &nbsp;|&nbsp; Page {pg} &nbsp;|&nbsp; Match {score}%
                            </div>
                            <div>"{preview}"</div>
                        </div>
                        """, unsafe_allow_html=True)

# ─── Quick Suggestions (shown only when history is empty) ───────
active_query = None

if not get_history():
    st.markdown("""
    <p style='text-align:center; color:#aaaaaa; font-size:0.75rem;
              font-weight:500; text-transform:uppercase; letter-spacing:0.08em;
              margin: 2rem 0 0.75rem 0;'>Suggested Questions</p>
    """, unsafe_allow_html=True)
    cols = st.columns(4)
    examples = [
        "Summarize this document",
        "What are the key takeaways?",
        "Extract the main action items",
        "Explain the core concepts",
    ]
    for i, ex in enumerate(examples):
        if cols[i].button(ex, key=f"sug_{i}"):
            active_query = ex

# ─── Chat Input ──────────────────────────────────────────────────
user_input = st.chat_input("Ask a question about your documents or government schemes...")
if user_input:
    active_query = user_input

# ─── Process Query ───────────────────────────────────────────────
if active_query:
    add_user_message(active_query)

    with st.chat_message("user", avatar="👤"):
        st.markdown(active_query)

    with st.chat_message("assistant", avatar="🏛️"):
        with st.spinner("🔍 Searching knowledge base and generating answer..."):
            try:
                result = run_rag(active_query)
            except Exception as e:
                result = {
                    "answer": f"An error occurred: {e}",
                    "sources": [],
                    "source_type": "error",
                    "num_results": 0,
                }

        add_assistant_message(
            content=result["answer"],
            source_type=result.get("source_type", "retrieval"),
            sources=result.get("sources", []),
            num_results=result.get("num_results", 0),
        )
        st.rerun()

# ─── Footer ──────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 3rem 0 1rem 0; color:#cccccc; font-size:0.78rem; border-top: 1px solid #f0f0f0; margin-top: 2rem;">
    GovScheme AI &nbsp;·&nbsp; Streamlit &nbsp;+&nbsp; Endee &nbsp;+&nbsp; Groq
</div>
""", unsafe_allow_html=True)
