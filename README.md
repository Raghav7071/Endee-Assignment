# GovScheme AI

A semantic search app that lets you ask questions about Indian Government Schemes
in plain English. Uses **Endee** as the vector database and retrieves answers
using vector similarity instead of keyword matching.

Built as part of the Endee.io campus assignment.

---

## What it Does

1. Government scheme documents are converted into vector embeddings
2. Embeddings are stored in Endee vector database
3. When you ask a question, it finds the most similar documents
4. Optionally uses an LLM (Groq) to generate a natural language answer

```
User Question → Embedding → Endee (cosine search) → Relevant Docs → LLM Answer
```

---

## How Endee is Used

Endee is the core vector database. The project uses the official Python SDK (`pip install endee`):

- **Index creation**: `client.create_index(name, dimension=384, space_type="cosine")`
- **Document storage**: `index.upsert([{id, vector, meta}])` — stores embeddings with text metadata
- **Similarity search**: `index.query(vector, top_k=3)` — finds closest matching documents

---

## Tech Stack (Fully Dockerized)

- **Endee** — vector database (runs in Docker)
- **Python / Streamlit** — backend logic and frontend UI (runs in Docker)
- **Sentence Transformers** — embedding model (all-MiniLM-L6-v2)
- **Groq API** — LLM for answer generation (optional, free tier)

---

## Setup Instructions

This project is fully containerized. You do **not** need Python installed locally — just Docker.

### Prerequisites
- Docker Desktop (running)
- Git

### Step 1: Set Up Environment

```bash
cp .env.example .env
```

If you want AI-generated LLM answers (optional), get a free API key from
https://console.groq.com and add it to `.env`:

```
GROQ_API_KEY=your_key_here
```

### Step 2: Run the App

Simply run:
```bash
docker-compose up --build -d
```
*(Or use `./setup.sh`)*

What happens under the hood:
1. Docker starts the **Endee server** on port 8080.
2. Docker builds and starts the **app container** which:
   - Waits 5 seconds for Endee to be ready.
   - Runs `backend/ingest.py` to embed and load all documents into Endee.
   - Starts the Streamlit frontend.

### Step 3: View the App

Open [http://localhost:8501](http://localhost:8501) in your browser.

*Note: It may take 10-15 seconds the first time for the embedding model to download and process the documents.*

---

## Sample Queries

| Question | Matches |
|---|---|
| What is PM Kisan? | pm_kisan_yojana.txt |
| How to get health insurance from government? | ayushman_bharat.txt |
| Business loan without collateral | mudra_yojana.txt |
| Free LPG connection | ujjwala_yojana.txt |
| Government support for startups | startup_india.txt |
| UPI and digital payments | digital_india.txt |
| Free skill training | skill_india.txt |

---

## Design Choices

- **Dockerized Architecture**: Everything runs in Docker so there are no pip or python version issues on different machines.
- **all-MiniLM-L6-v2**: lightweight (~80MB), 384-dim embeddings — good enough for this scale.
- **Cosine similarity**: works better than euclidean for text since it compares direction not magnitude.
- **Groq as optional**: app works without it (returns raw text), but with it you get proper AI answers.
- **Streamlit**: simple to build, looks clean, no need for a separate frontend framework.

---

## Limitations

- Ingests full documents without chunking — would need splitting for larger docs.
- No deduplication — re-running ingest creates duplicate entries (though Endee handles exact ID overwrites safely).

---

## Author

**Raghav Yadav**
B.Tech 2026
Endee.io Campus Assignment
