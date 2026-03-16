# GovScheme AI Chatbot — RAG with Endee Vector Database

A RAG-based virtual assistant that lets you upload Indian Government Scheme documents (PDF, TXT, CSV, JSON) and ask questions about them. It uses Endee as the vector database for semantic search and Llama 3.1 (via Groq) for generating answers with page-level citations.

## Problem

Understanding Indian Government Schemes (Yojanas) can be extremely complex for the average citizen. Documents detailing scheme guidelines are often massive PDFs spanning hundreds of pages. Keyword search fails to understand the intent of a citizen's question. This project uses semantic search and RAG to give precise, cited answers directly from official documents.

## Architecture

User (Streamlit UI)
    |
    |-- Upload Document ----> Backend Processing
    |                         |
    |                         |-- Extract text (PyPDF2, etc.)
    |                         |-- Chunk text (700 chars, 100 overlap)
    |                         |-- Generate embeddings (all-MiniLM-L6-v2)
    |                         |-- Store in Endee Vector DB
    |
    |-- Ask Question -------> Query Pipeline
                              |
                              |-- Embed query (all-MiniLM-L6-v2)
                              |-- Search Endee (top 5 similar chunks)
                              |-- Generate answer (Llama 3.1 via Groq)
                                  |-- Return answer + citations

## How Endee is Used

Endee is the core vector database powering this application's RAG pipeline. Here is what it does:

* Stores 384-dimensional embeddings for each document chunk
* Indexes vectors dynamically with metadata (filename, page number, chunk ID, hash) using a cosine similarity space
* Searches using cosine similarity to find the most mathematically relevant chunks for a user query in milliseconds

I chose Endee because it operates natively over HTTP with a very clean, lightweight REST interface, avoiding the need for heavy SDK dependencies while providing high-performance search capabilities.

## Project Structure

├── backend/
|   └── query.py           # Backend query handler for metadata
├── data/
|   ├── cache/             # Persistent embedding cache (SHA-256)
|   └── docs/              # Default scheme documents
├── modules/
|   ├── chatbot.py         # Session state manager
|   ├── document_loader.py # Multi-format text extractor
|   ├── embedding_generator.py # Embedding and caching logic
|   ├── rag_pipeline.py    # End-to-end RAG orchestrator
|   ├── text_chunker.py    # Text splitting with metadata
|   └── vector_store.py    # Endee abstraction layer
├── streamlit_app.py       # Streamlit chat and upload UI
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md

## Tech Stack

| Component | Tech |
|---|---|
| Vector DB | Endee |
| LLM | Llama 3.1 8B-Instant (Groq) |
| Embeddings | all-MiniLM-L6-v2 (SentenceTransformers) |
| Core Logic | Python Modules |
| Frontend | Streamlit |
| Containerization | Docker Compose |

## Setup

### Prerequisites

* Docker Desktop (running)
* Git
* Groq API key (free)

### 1. Clone this project

```bash
git clone <your-fork-url>
cd Endee-Assignment
cp .env.example .env
# edit .env and add your GROQ_API_KEY
```

### 2. Run with Docker (recommended)

```bash
docker-compose up --build -d
```
This starts both the Endee Vector Database and the Streamlit frontend application.

### 2b. Or run manually

If you prefer running without Docker:

Requirements:
* Endee server running on port 8080 (see Endee documentation for installation)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run the Streamlit app
streamlit run streamlit_app.py
```

## Use it

1. Open http://localhost:8501
2. Upload a PDF, TXT, CSV, or JSON file in the sidebar
3. Click "Process & Ingest Documents"
4. Ask questions about the schemes in the chat

## Limitations

* Scanned PDFs without embedded text are not supported (no OCR)
* System currently uses a single Endee index (`govt_schemes`) for all documents
* Chat history resets upon hard browser reload
* Best performance and formatting with English text
