import streamlit as st

# MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="GovScheme AI | RAG Chatbot",
    layout="wide",
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


init_session()


st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

    /* ── Palette ──────────────────────────────────────
       #F1EFEC  warm cream     → background
       #123458  deep navy      → primary text & accent
       #D4C9BE  warm tan       → borders / secondary text
       #030303  near-black     → dark details
    ───────────────────────────────────────────────── */

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* App background — warm cream */
    html, body, .stApp {
        background-color: #F1EFEC !important;
        font-family: 'Outfit', sans-serif;
        color: #123458;
    }

    /* Sidebar — slightly deeper cream */
    [data-testid="stSidebar"] {
        background-color: #e5dfd8 !important;
        border-right: 1px solid #D4C9BE;
    }
    [data-testid="stSidebar"] * { color: #123458 !important; }
    [data-testid="stSidebar"] .stButton > button {
        background: #123458 !important;
        color: #D4C9BE !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        transition: all 0.25s ease;
    }
    [data-testid="stSidebar"] .stButton > button p,
    [data-testid="stSidebar"] .stButton > button span,
    [data-testid="stSidebar"] .stButton > button div {
        color: #D4C9BE !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: #1a4a7a !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 14px rgba(18, 52, 88, 0.3);
    }

    /* Header */
    .app-header {
        text-align: center;
        padding: 2rem 0 1.5rem 0;
        animation: fadeUp 0.55s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
    @keyframes fadeUp {
        0% { opacity: 0; transform: translateY(16px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    .app-title {
        font-size: 2.6rem;
        font-weight: 800;
        color: #123458;
        line-height: 1.2;
        margin-bottom: 0.4rem;
        letter-spacing: -0.02em;
    }
    .app-subtitle {
        font-size: 1.05rem;
        color: #5a7a9a;
        font-weight: 300;
        letter-spacing: 0.01em;
    }

    /* Answer card */
    .answer-card {
        background: #ffffff;
        border-radius: 14px;
        padding: 1.4rem 1.8rem;
        border: 1px solid #D4C9BE;
        border-top: 3px solid #123458;
        margin: 0.5rem 0;
        color: #123458;
    }

    /* Source card */
    .source-card {
        background: #faf8f6;
        border: 1px solid #D4C9BE;
        border-left: 3px solid #123458;
        border-radius: 10px;
        padding: 0.9rem 1.1rem;
        margin-bottom: 0.65rem;
        font-size: 0.88rem;
        color: #2c4a6a;
    }
    .source-meta {
        font-size: 0.72rem;
        color: #8a9aaa;
        margin-bottom: 0.4rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    /* Badges */
    .badge-ai {
        display: inline-flex; align-items: center; gap: 6px;
        padding: 3px 12px; border-radius: 5px;
        background: rgba(18, 52, 88, 0.08);
        color: #123458;
        font-size: 0.72rem; font-weight: 700;
        border: 1px solid rgba(18, 52, 88, 0.25);
        margin-bottom: 0.9rem;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    .badge-retrieval {
        display: inline-flex; align-items: center; gap: 6px;
        padding: 3px 12px; border-radius: 5px;
        background: rgba(212, 201, 190, 0.3);
        color: #5a7a9a;
        font-size: 0.72rem; font-weight: 700;
        border: 1px solid rgba(212, 201, 190, 0.6);
        margin-bottom: 0.9rem;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    /* Suggestion buttons */
    div[data-testid="stButton"] button {
        background: #ffffff !important;
        color: #123458 !important;
        border: 1px solid #D4C9BE !important;
        border-radius: 9px !important;
        font-weight: 500 !important;
        font-size: 0.88rem !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
        padding: 0.7rem !important;
    }
    div[data-testid="stButton"] button:hover {
        background: #123458 !important;
        border-color: #123458 !important;
        color: #F1EFEC !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(18, 52, 88, 0.2) !important;
    }

    /* Chat input */
    .stChatInput > div > div > textarea {
        border-radius: 10px !important;
        border: 1px solid #D4C9BE !important;
        background: #ffffff !important;
        color: #123458 !important;
        font-size: 1rem !important;
        padding: 0.9rem 1.1rem !important;
    }
    .stChatInput > div > div > textarea:focus {
        border-color: #123458 !important;
        box-shadow: 0 0 0 2px rgba(18, 52, 88, 0.15) !important;
    }

    /* Markdown text */
    .stMarkdown p, .stMarkdown li {
        color: #2c4a6a !important;
        line-height: 1.65 !important;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #123458 !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: #ffffff !important;
        color: #5a7a9a !important;
        border-radius: 8px !important;
        border: 1px solid #D4C9BE !important;
    }
    /* File uploader — red background, white text */
    [data-testid="stFileUploaderDropzone"] {
        background: #e63946 !important;
        border-color: #e63946 !important;
        border-radius: 10px !important;
    }
    [data-testid="stFileUploader"] * {
        color: #ffffff !important;
    }
    [data-testid="stFileUploader"] small {
        color: #ffffff !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] * {
        color: #ffffff !important;
    }
    [data-testid="stFileUploaderDropzone"] button {
        color: #ffffff !important;
        border-color: rgba(255,255,255,0.6) !important;
        background: transparent !important;
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#  SIDEBAR — Document Upload & Knowledge Base Manager
# ═══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## Knowledge Base")
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
            if st.button("Process & Ingest Documents", use_container_width=True):
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
                                st.warning(f"Could not extract text from **{uploaded_file.name}**.")
                                continue

                            # Step 2: Chunk
                            chunks = chunk_pages(pages, chunk_size=700, chunk_overlap=100)
                            st.markdown(f"**{uploaded_file.name}** → {len(chunks)} chunks")

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
                                f"**{uploaded_file.name}** ingested!\n\n"
                                f"• {n_upserted} new chunks → Endee\n"
                                f"• {cached_count} chunks skipped (cached)"
                            )

                        except Exception as e:
                            st.error(f"Error processing **{uploaded_file.name}**: {e}")
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
        st.markdown("**Indexed Documents (this session)**")
        for doc in docs:
            st.markdown(f"• `{doc}`")

    st.markdown("---")
    if st.button("Clear Chat History", use_container_width=True):
        clear_history()
        st.rerun()


# ═══════════════════════════════════════════════════════════════════
#  MAIN AREA — Chat Interface
# ═══════════════════════════════════════════════════════════════════

st.markdown("""
<div class="app-header">
    <div class="app-title">GovScheme AI Chatbot</div>
    <div class="app-subtitle">
        Upload any document → Ask questions → Get AI-powered answers with source citations
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Chat History ────────────────────────────────────────────────
for msg in get_history():
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant"):
            _is_ai = msg.get("source_type") == "llm"
            _badge = "badge-ai" if _is_ai else "badge-retrieval"
            _label = "AI Synthesized Answer" if _is_ai else "Direct Document Extraction"

            st.markdown(f"""
            <div class="answer-card">
                <div class="{_badge}">{_label}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(msg["content"])

            # Source citations
            sources = msg.get("sources", [])
            if sources:
                with st.expander(f"{len(sources)} Source(s) Used", expanded=False):
                    for s in sources:
                        fname = s.get("filename", "Unknown").replace(".pdf", "").replace(".txt", "")
                        pg = s.get("page_number", "?")
                        score = round(s.get("score", 0) * 100, 1)
                        preview = s.get("preview", "")
                        st.markdown(f"""
                        <div class="source-card">
                            <div class="source-meta">
                                {fname} &nbsp;|&nbsp; Page {pg} &nbsp;|&nbsp; Match {score}%
                            </div>
                            <div>"{preview}"</div>
                        </div>
                        """, unsafe_allow_html=True)

# ─── Quick Suggestions (shown only when history is empty) ───────
active_query = None

if not get_history():
    st.markdown("""
    <p style='text-align:center; color:#94a3b8; font-size:0.8rem;
              font-weight:600; text-transform:uppercase; letter-spacing:0.05em;
              margin: 1.5rem 0 0.75rem 0;'>Suggested Questions</p>
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

    with st.chat_message("user"):
        st.markdown(active_query)

    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge base and generating answer..."):
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
<div style="text-align:center; padding: 3rem 0 1rem 0; color:#94a3b8; font-size:0.82rem;">
    GovScheme AI · Built with Streamlit + Endee Vector DB + Groq LLM
</div>
""", unsafe_allow_html=True)
