import os
from dotenv import load_dotenv

load_dotenv()

# endee config
ENDEE_URL = os.getenv("ENDEE_URL", "http://localhost:8080")
INDEX_NAME = os.getenv("INDEX_NAME", "govt_schemes")

# embedding model — using MiniLM since its lightweight and fast
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# how many results to return per query
TOP_K = int(os.getenv("TOP_K", "5"))

# groq llm (optional — works without it too)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

# path to our documents
DOCS_DIR = os.getenv("DOCS_DIR", "../data/docs")
