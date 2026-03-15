import streamlit as st

# MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="GovScheme AI | RAG Chatbot",
    page_icon="🏛️",
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

# ─── Initialize session ────────────────────────────────────────────────────
init_session()

# ─── CSS (premium design) ──────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Main App Background - Sleek Dark */
    .stApp {
        background: #0f1117;
        background-image: 
            radial-gradient(at 0% 0%, hsla(253,16%,7%,1) 0, transparent 50%), 
            radial-gradient(at 50% 0%, hsla(225,39%,30%,0.1) 0, transparent 50%), 
            radial-gradient(at 100% 0%, hsla(339,49%,30%,0.1) 0, transparent 50%);
        font-family: 'Outfit', sans-serif;
        color: #e2e8f0;
    }

    /* Sidebar - Glassmorphism */
    [data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.6) !important;
        backdrop-filter: blur(12px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    [data-testid="stSidebar"] * { color: #cbd5e1 !important; }
    [data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        transition: all 0.3s ease;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
    }

    /* Header */
    .app-header {
        text-align: center;
        padding: 2rem 0 1.5rem 0;
        animation: fadeUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
    @keyframes fadeUp {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    .app-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(to right, #818cf8, #c084fc, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    .app-subtitle {
        font-size: 1.15rem;
        color: #94a3b8;
        font-weight: 300;
        letter-spacing: 0.01em;
    }

    /* Chat messages - Dark cards */
    .answer-card {
        background: rgba(30, 41, 59, 0.5);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 1.5rem 2rem;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
        margin: 0.5rem 0;
        position: relative;
        overflow: hidden;
        color: #f1f5f9;
    }
    .answer-card::before {
        content: '';
        position: absolute; top: 0; left: 0; right: 0; height: 3px;
        background: linear-gradient(90deg, #6366f1, #c084fc, #ec4899);
    }
    .source-card {
        background: rgba(15, 23, 42, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
        border-left: 3px solid #8b5cf6;
        font-size: 0.9rem;
        color: #cbd5e1;
    }
    .source-meta {
        font-size: 0.75rem;
        color: #64748b;
        margin-bottom: 0.5rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-ai {
        display: inline-flex; align-items: center; gap: 6px;
        padding: 4px 14px; border-radius: 6px;
        background: rgba(99, 102, 241, 0.15); 
        color: #818cf8;
        font-size: 0.75rem; font-weight: 600;
        border: 1px solid rgba(99, 102, 241, 0.3);
        margin-bottom: 1rem;
        letter-spacing: 0.02em;
        text-transform: uppercase;
    }
    .badge-retrieval {
        display: inline-flex; align-items: center; gap: 6px;
        padding: 4px 14px; border-radius: 6px;
        background: rgba(148, 163, 184, 0.1); 
        color: #94a3b8;
        font-size: 0.75rem; font-weight: 600;
        border: 1px solid rgba(148, 163, 184, 0.2); 
        margin-bottom: 1rem;
        letter-spacing: 0.02em;
        text-transform: uppercase;
    }

    /* Quick suggestion buttons - Outline style */
    div[data-testid="stButton"] button {
        background: rgba(30, 41, 59, 0.3) !important;
        color: #cbd5e1 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
        padding: 0.75rem !important;
    }
    div[data-testid="stButton"] button:hover {
        background: rgba(99, 102, 241, 0.1) !important;
        border-color: rgba(99, 102, 241, 0.5) !important;
        color: #e0e7ff !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
    }

    /* Chat input - Neon glowing focus */
    .stChatInput > div > div > textarea {
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        background: rgba(15, 23, 42, 0.6) !important;
        color: #f8fafc !important;
        font-size: 1rem !important;
        padding: 1rem 1.25rem !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
    }
    .stChatInput > div > div > textarea:focus {
        border-color: #8b5cf6 !important;
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.3), 0 0 15px rgba(139, 92, 246, 0.1) !important;
    }
    
    /* Markdown Text Colors */
    .stMarkdown p, .stMarkdown li {
        color: #cbd5e1 !important;
        line-height: 1.6 !important;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #f8fafc !important;
    }
    
    /* Expander override */
    .streamlit-expanderHeader {
        background: rgba(30, 41, 59, 0.3) !important;
        color: #94a3b8 !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
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
    <div class="app-title">🏛️ GovScheme AI Chatbot</div>
    <div class="app-subtitle">
        Upload any document → Ask questions → Get AI-powered answers with source citations
    </div>
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
    <p style='text-align:center; color:#94a3b8; font-size:0.8rem;
              font-weight:600; text-transform:uppercase; letter-spacing:0.05em;
              margin: 1.5rem 0 0.75rem 0;'>✦ Suggested Questions</p>
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
<div style="text-align:center; padding: 3rem 0 1rem 0; color:#94a3b8; font-size:0.82rem;">
    🏛️ GovScheme AI · Built with Streamlit + Endee Vector DB + Groq LLM
</div>
""", unsafe_allow_html=True)
