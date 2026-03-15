# GovScheme AI Assistant | Endee Internship Project

A production-style conversational AI application built using the **Endee Vector Database**, Streamlit, and Groq LLMs. This project is submitted as part of the Endee Software Development / Machine Learning Internship evaluation.

---

## Mandatory Usage Steps (For Evaluators & Contributors)
To ensure uniformity and authenticity, please strictly follow these repository usage steps before working with the codebase:
1. **Star** the official [Endee GitHub Repository](https://github.com/endee-io/endee) 
2. **Fork** this repository to your personal GitHub account.
3. Use the forked version as the base for building or testing this project.

---

## 1. Project Overview & Problem Statement
Understanding Indian Government Schemes (Yojanas) can be extremely complex for the average citizen. Documents detailing scheme guidelines (such as *Pradhan Mantri Anusuchit Jaati Abhyuday Yojna*, *Ayushman Bharat*, etc.) are often massive PDFs spanning hundreds of pages. 

**Problem**: Keyword-based searches fail to understand the *intent* of a citizen's question. A citizen asking "How to get a business loan without collateral" will fail to find the *Mudra Yojana* if the exact word "collateral" isn't explicitly mapped.

**Solution**: The **GovScheme AI Assistant** is a Retrieval Augmented Generation (RAG) system. It ingests massive government PDFs, generates semantic vector embeddings, and uses the **Endee Vector Database** to perform ultra-fast cosine similarity searches. It then passes the highly relevant document chunks to an LLM to synthesize a continuous, beautiful, chat-based response for the user. 

---

## 2. System Design & Technical Approach

The system uses a completely containerized architecture (Docker Compose) separating the vector database from the frontend application stream.

### Architecture Flow:
1. **Document Ingestion Layer (`ingest.py`, `chunker.py`)**: 
   - Reads raw `.txt` files and massive `.pdf` documents in real-time.
   - Extracts text using `PyPDF2` and intelligently chunks strings into 800-word segments (with 100-word overlaps) to preserve contextual meaning.
2. **Embedding Layer (`embeddings.py`)**:
   - Converts the text chunks into dense 384-dimensional vectors using `all-MiniLM-L6-v2`.
3. **Storage & Retrieval (`query.py`)**:
   - Vectors are stored and indexed continuously in **Endee**.
4. **Generation (`llm.py`)**:
   - Retrieved chunks (Top K=5) are injected into a rigorous System Prompt and sent to Groq's API (`llama-3.1-8b-instant`). The LLM synthesizes the final professional Markdown output.
5. **Frontend UI (`streamlit_app.py`)**:
   - A ChatGPT-style conversational loop leveraging Streamlit `session_state` and dynamic Sidebar PDF uploading.

---

## 3. Explanation of How Endee is Used

**Endee** operates as the core vector search engine powering this application's RAG pipeline.

### Integration Details:
- **Python SDK**: The project connects via the official Endee python package natively over HTTP (`endee:8080`).
- **Index Creation**: The system boots up and automatically defines an index named `govt_schemes` using the `cosine` space type natively optimized for semantic text comparison.
- **Dynamic Upserting**: As users upload new PDFs via the Streamlit UI Sidebar, the Python backend intercepts the upload, creates chunk embeddings, and uses `index.upsert()` to ingest the vectors *on the fly* with metadata (text and source filename). 
- **Similarity Search**: When a user queries the chatbot, `index.query(vector, top_k=5)` pulls the 5 most mathematically similar text chunks in milliseconds.

---

## 4. Clear Setup and Execution Instructions

This project is completely Dockerized for foolproof deployment. You only need Docker Desktop installed.

### Prerequisites:
- Docker Desktop (Running)
- Git

### Step-by-Step Execution:

**1. Clone & Setup Environment**
```bash
cp .env.example .env
```
*(Optional but Highly Recommended)*: Add a free Groq API key into the `.env` file to enable the AI Synthesizer fallback. Otherwise, the app defaults to raw extracted text.

**2. Run the Multi-Container Cluster**
```bash
docker-compose up --build -d
```
*This command starts Endee in the background, rebuilds the Streamlit container, downloads the embedding model, and auto-ingests the `data/docs` folder.*

**3. Access the Chat Application**
Open your browser to: **[http://localhost:8501](http://localhost:8501)**

**4. Testing the RAG Pipeline**
- Type: *"Explain the Pradhan Mantri Anusuchit Jaati Abhyuday Yojna in detail"* in the chat input.
- Watch as Endee retrieves the relevant chunks and the LLM renders a perfect Markdown response.
- Use the **Sidebar Manager** to upload a brand new Government PDF and ask a question about it immediately!
