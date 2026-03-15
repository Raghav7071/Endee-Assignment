import streamlit as st

# MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="GovScheme AI | Premium",
    page_icon="🏛️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

import sys
import os
import tempfile

# add backend to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from query import search
import PyPDF2
from ingest import extract_text
from chunker import chunk_text
from embeddings import generate_embedding
from endee import Endee
from config import ENDEE_URL, INDEX_NAME

# inject advanced CSS for a "Wow" factor
st.markdown("""
<style>
    /* Import premium font */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    /* hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Global styling */
    .stApp {
        background: linear-gradient(135deg, #f0f4f8 0%, #ffffff 100%);
        color: #0f172a;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Animations */
    @keyframes fadeUp {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulseGlow {
        0% { box-shadow: 0 0 0 0 rgba(79, 70, 229, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(79, 70, 229, 0); }
        100% { box-shadow: 0 0 0 0 rgba(79, 70, 229, 0); }
    }

    /* Header styling */
    .header-container {
        padding: 3rem 0 2rem 0;
        text-align: center;
        animation: fadeUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
    .header-badge {
        display: inline-block;
        padding: 6px 16px;
        background: rgba(79, 70, 229, 0.1);
        color: #4f46e5;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }
    .header-title {
        font-size: 3.5rem;
        font-weight: 800;
        line-height: 1.1;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, #0f172a 0%, #334155 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .header-subtitle {
        font-size: 1.2rem;
        color: #64748b;
        font-weight: 400;
        max-width: 600px;
        margin: 0 auto;
        line-height: 1.6;
    }

    /* Search & Chat Input Box Styling */
    .stTextInput>div>div>input, .stChatInput>div>div>textarea {
        border-radius: 16px !important;
        padding: 1.2rem 1.5rem !important;
        font-size: 1.15rem !important;
        font-weight: 500 !important;
        border: 2px solid #e2e8f0 !important;
        background: white !important;
        color: #0f172a !important; /* FIXED TYPING VISIBILITY BUG */
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    .stTextInput>div>div>input:focus, .stChatInput>div>div>textarea:focus {
        border-color: #4f46e5 !important;
        box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.2), 0 0 0 4px rgba(79, 70, 229, 0.1) !important;
        transform: translateY(-2px);
    }

    /* Example Buttons styling */
    div[data-testid="stButton"] button {
        background: white;
        color: #475569;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 0.75rem 1rem;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        width: 100%;
        height: 100%;
    }
    div[data-testid="stButton"] button:hover {
        background: #f8fafc;
        border-color: #cbd5e1;
        color: #0f172a;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* Answer Card (Glassmorphism & Gradients) */
    .answer-card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 2rem;
        border: 1px solid rgba(226, 232, 240, 0.8);
        box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.05), 0 0 0 1px rgba(0,0,0,0.02);
        margin-top: 2rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        animation: fadeUp 0.5s ease-out forwards;
    }
    
    /* decorative top bar for answer card */
    .answer-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #4f46e5, #0ea5e9, #10b981);
    }
    
    .answer-heading {
        font-weight: 800;
        color: #0f172a;
        font-size: 1.5rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .answer-content {
        color: #334155;
        font-size: 1.15rem;
        line-height: 1.7;
        font-weight: 400;
    }
    
    /* Document Cards */
    .doc-card {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid #f1f5f9;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    .doc-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 20px -8px rgba(0, 0, 0, 0.08);
        border-color: #e2e8f0;
    }
    .doc-card::left-accent {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background-color: #94a3b8;
        border-radius: 4px 0 0 4px;
    }
    
    .doc-title {
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.25rem;
        font-size: 1.1rem;
    }
    
    .doc-score {
        display: inline-block;
        font-size: 0.75rem;
        color: #ffffff;
        background-color: #64748b;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .doc-preview {
        font-size: 0.95rem;
        color: #475569;
        line-height: 1.6;
    }
    
    /* Source badges */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 700;
        background-color: #f1f5f9;
        color: #475569;
        margin-top: 1.5rem;
        border: 1px solid #e2e8f0;
    }
    .badge.ai {
        background-color: #eef2ff;
        color: #4f46e5;
        border-color: #e0e7ff;
    }
    
    /* Adjust expander styling */
    .streamlit-expanderHeader {
        font-weight: 600 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: #334155 !important;
        background-color: #f8fafc !important;
        border-radius: 12px !important;
        border: 1px solid #e2e8f0 !important;
        margin-bottom: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- SESSION STATE -----------------
# We use chat_history for rendering the beautiful ChatGPT style layout
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ----------------- UI STRUCTURE -----------------

# Sidebar for Dynamic Uploads
with st.sidebar:
    st.markdown("### 📄 Knowledge Base Manager")
    st.info("Upload new documents to make them instantly searchable.")
    
    uploaded_file = st.file_uploader("Upload Scheme Document", type=["pdf", "txt"])
    
    if uploaded_file is not None:
        filename = uploaded_file.name
        
        # Save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name
            
        if st.button("Process & Add to Knowledge Base", use_container_width=True):
            with st.spinner("Processing document..."):
                try:
                    # extract
                    content = extract_text(tmp_path)
                    
                    if content:
                        # chunk
                        chunks = chunk_text(content, chunk_size=800, overlap=100)
                        
                        # connect and insert
                        client = Endee()
                        client.set_base_url(f"{ENDEE_URL}/api/v1")
                        index = client.get_index(name=INDEX_NAME)
                        
                        for chunk_i, chunk in enumerate(chunks):
                            vector = generate_embedding(chunk)
                            doc_id = filename.replace(".pdf", "").replace(".txt", "")
                            chunk_id = f"{doc_id}_user_chunk{chunk_i}"
                            
                            index.upsert([{
                                "id": chunk_id,
                                "vector": vector,
                                "meta": {
                                    "text": chunk,
                                    "source": filename
                                }
                            }])
                            
                        st.success(f"Added {filename} ({len(chunks)} chunks)!")
                    else:
                        st.warning("Could not extract text from document.")
                        
                except Exception as e:
                    st.error(f"Error processing document: {e}")
                finally:
                    os.unlink(tmp_path)

# Header area
st.markdown("""
<div class="header-container">
    <div class="header-badge">Semantic Search + RAG Vector DB</div>
    <h1 class="header-title">GovScheme AI Assistant</h1>
    <p class="header-subtitle">Instantly discover and understand Indian Government Schemes using Endee vector database and conversational AI.</p>
</div>
""", unsafe_allow_html=True)

# ----------------- RENDER CHAT HISTORY -----------------
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant", avatar="🏛️"):
            # Display Answer
            is_ai = msg["source"] == "llm"
            badge_class = "badge ai" if is_ai else "badge"
            badge_icon = "✨" if is_ai else "📄"
            badge_text = "AI Synthesized Response" if is_ai else "Direct Document Extraction"
            
            st.markdown(f"""
            <div class="answer-card" style="margin-top: 0;">
                <div class="{badge_class}" style="margin-top: 0; margin-bottom: 1rem;">
                    {badge_icon} {badge_text}
                </div>
                <div class="answer-content">
                    {msg["content"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Display Sources Expander
            with st.expander(f"📚 View Retrieved Source Documents ({msg['num_results']})", expanded=False):
                st.markdown("<br>", unsafe_allow_html=True)
                for r in msg.get("results", []):
                    score_pct = round(r.get('score', 0) * 100, 1)
                    st.markdown(f"""
                    <div class="doc-card">
                        <div style="position: absolute; left: 0; top: 0; bottom: 0; width: 4px; background-color: #94a3b8; border-radius: 4px 0 0 4px;"></div>
                        <div class="doc-title">{r.get('source', 'Unknown Document').replace('.txt', '').replace('.pdf', '')}</div>
                        <div class="doc-score">Match: {score_pct}%</div>
                        <div class="doc-preview">"{r.get('preview', '')}"</div>
                    </div>
                    """, unsafe_allow_html=True)

# ----------------- QUICK ACTION BUTTONS (Only if history is empty) -----------------
active_query = None

if not st.session_state.chat_history:
    st.markdown("<p style='color: #64748b; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 12px; text-align: center;'>Suggested Queries</p>", unsafe_allow_html=True)
    cols = st.columns(4)
    examples = [
        "What is Ayushman Bharat?", 
        "How to get MUDRA loan?", 
        "Tell me about Digital India", 
        "PM Kisan Yojana details"
    ]
    
    for i, ex in enumerate(examples):
        if cols[i].button(ex, key=f"ex_{i}", use_container_width=True):
            active_query = ex

# ----------------- CHAT INPUT -----------------
user_input = st.chat_input("Ask about any Government Scheme...")
if user_input:
    active_query = user_input

# ----------------- PROCESS QUERY -----------------
if active_query:
    # Append user question to UI immediately
    st.session_state.chat_history.append({"role": "user", "content": active_query})
    
    # Render user query right away
    with st.chat_message("user", avatar="👤"):
        st.markdown(active_query)

    with st.chat_message("assistant", avatar="🏛️"):
        with st.spinner("Analyzing knowledge base with Endee Vector Search..."):
            result = search(active_query)
            
        if result:
            answer_text = result.get('answer', 'No answer found').replace(chr(10), '\n')
            
            # Append assistant response to history
            st.session_state.chat_history.append({
                "role": "assistant", 
                "content": answer_text,
                "source": result.get("source"),
                "num_results": result.get("num_results"),
                "results": result.get("results")
            })
            
            # Streamlit rerun to cleanly show the beautiful answer markdown UI loop
            st.rerun()

st.markdown("<br><br><br>", unsafe_allow_html=True)
# Footer
st.markdown("""
<div style="text-align: center; margin-top: 4rem; padding-top: 2rem; border-top: 1px solid #e2e8f0; color: #94a3b8; font-size: 0.85rem; font-weight: 500;">
    Developed for Endee.io • Built with Streamlit & Endee Vector DB
</div>
""", unsafe_allow_html=True)
