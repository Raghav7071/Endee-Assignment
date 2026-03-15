import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def get_config(key, default=None):
    # 1. Try streamlit secrets (for cloud)
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    
    # 2. Try OS environment (for local/docker)
    return os.getenv(key, default)

# endee config
ENDEE_URL = get_config("ENDEE_URL", "http://localhost:8080")
INDEX_NAME = get_config("INDEX_NAME", "govt_schemes")

# embedding model — using MiniLM since its lightweight and fast
EMBEDDING_MODEL = get_config("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# how many results to return per query
TOP_K = int(get_config("TOP_K", "5"))

# groq llm (optional — works without it too)
GROQ_API_KEY = get_config("GROQ_API_KEY", "")
GROQ_MODEL = get_config("GROQ_MODEL", "llama-3.1-8b-instant")

# path to our documents
DOCS_DIR = get_config("DOCS_DIR", "../data/docs")
