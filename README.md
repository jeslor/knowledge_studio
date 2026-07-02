# Knowledge Studio

Knowledge Studio is a Django-based Retrieval-Augmented Generation (RAG) web application for uploading knowledge documents, indexing them into Qdrant, and answering user questions with cited context.

The current implementation uses:

- Local LLM inference through Ollama (`qwen2.5:7b`) for query rewriting and final response generation.
- Hybrid retrieval in Qdrant (dense + sparse BM25).
- Local embedding/reranking models from Hugging Face (`BAAI/bge-large-en-v1.5`, `BAAI/bge-reranker-large`).

## Features

- User authentication, profile, and dashboard pages.
- Document ingestion API for PDF/TXT/MD uploads.
- OCR fallback for scanned PDF pages.
- Multi-stage RAG pipeline:
  1.  Query processing
  2.  Retrieval from Qdrant
  3.  Re-ranking
  4.  Context building
  5.  LLM answer generation
- Streaming API responses for real-time pipeline updates.

## Tech Stack

- Python / Django
- PostgreSQL-compatible database URI (currently expected via `SUPABASE_URI`)
- Qdrant Cloud (vector database)
- LangChain ecosystem (`langchain-ollama`, `langchain-qdrant`, `langchain-huggingface`)
- Ollama (local LLM serving)
- PyTorch, SentenceTransformers
- OCR tooling: PyMuPDF (`fitz`) + Tesseract

## Prerequisites

Install and configure the following before running the app:

1. Python 3.12+
2. pip and virtualenv
3. Ollama installed and running locally
4. Tesseract OCR installed on your machine
5. A PostgreSQL-compatible connection string (for `SUPABASE_URI`)
6. A Qdrant Cloud account, cluster endpoint, and API key

### macOS system prerequisites

```bash
brew install tesseract
brew install ollama
```

Start Ollama service (if not already running):

```bash
ollama serve
```

Pull the model currently used by this project:

```bash
ollama pull qwen2.5:7b
```

## Qdrant Cloud Signup and Requirements

This project stores vectors in Qdrant Cloud and requires three values:

- `QDRANT_ENDPOINT`: your cluster URL
- `QDRANT_API_KEY`: API key for that cluster
- `COLLECTION_NAME`: target collection (for example `knowledge_base`)

### Steps

1. Go to Qdrant Cloud and create an account.
2. Create a new cluster (free tier is fine for development).
3. Copy the cluster endpoint URL.
4. Generate an API key in the cluster security/settings section.
5. Choose a collection name and set it in your environment file.

## Project Setup

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Install core dependencies (if you do not already have a pinned requirements file):

```bash
pip install -r requirements.txt
```

## Environment Configuration

Create a `.env` file in the project root (do not commit secrets):

```env
SUPABASE_URI=postgresql://<user>:<password>@<host>/<db>?sslmode=require

QDRANT_API_KEY=<your_qdrant_api_key>
QDRANT_ENDPOINT=https://<your-cluster-id>.<region>.cloud.qdrant.io
COLLECTION_NAME=knowledge_base
```

Notes:

- The app loads `.env` in Django settings.
- The KB config also attempts to load `config/.env.local`; keep variables in `.env` for normal app execution, and optionally duplicate them into `config/.env.local` if you run service modules independently.

## Run the Application

Apply migrations and start the server:

```bash
python manage.py migrate
python manage.py createsuperuser
python ../manage.py runserver
```

Open:

- Home: `http://127.0.0.1:8000/`
- Admin: `http://127.0.0.1:8000/admin/`

## API Endpoints

- `POST /api/embed/` - Ingest and index uploaded documents into Qdrant
- `POST /api/rag/` - Execute streaming RAG answer pipeline

## LLM Query Options

This repo supports two architecture options for answer generation.

### Option A (Current Setup): Local LLM via Ollama

Current code path in `apps/kb/services/llm_generation_05.py`:

- Uses `ChatOllama(model="qwen2.5:7b", temperature=0)`
- Keeps inference local (no third-party LLM API required)
- Requires Ollama daemon + downloaded model

Recommended when:

- You want local/offline inference
- You want to avoid per-token API cost
- You are comfortable running models on local hardware

### Option B (Alternative): Remote LLM API (for example OpenAI)

OpenAI is not wired in the current code, but you can switch by replacing the `ChatOllama` client with a LangChain OpenAI client.

Typical requirements:

- `OPENAI_API_KEY` in `.env`
- Install provider package (for example `langchain-openai`)
- Update the LLM initialization in `apps/kb/services/llm_generation_05.py`

Benefits:

- No local model hosting
- Easy scaling and model upgrades

Trade-offs:

- Network dependency
- Ongoing API usage cost
- External data processing considerations

## Local Models Used in This Project

The following models are referenced by the current implementation:

- Generation model (Ollama):
  - `qwen2.5:7b`

- Dense embedding model (Hugging Face):
  - `BAAI/bge-large-en-v1.5`

- Sparse retrieval model:
  - `Qdrant/bm25`

- Re-ranker model (CrossEncoder):
  - `BAAI/bge-reranker-large`

First-time startup can download model artifacts and may take several minutes depending on network and hardware.

## Security and Secrets

- Do not commit `.env` with real keys.
- Rotate any API keys that were ever exposed in repository history.
- Use separate development/staging/production credentials.

## Troubleshooting

- `Connection error to Qdrant`:
  - Verify `QDRANT_ENDPOINT` and `QDRANT_API_KEY`.
  - Confirm your cluster is running and reachable.

- `Ollama model not found`:
  - Run `ollama pull qwen2.5:7b`.
  - Ensure `ollama serve` is active.

- `OCR not working`:
  - Confirm Tesseract is installed (`tesseract --version`).

- `Database connection issues`:
  - Validate `SUPABASE_URI` format and SSL parameters.

## Suggested Next Improvements

- Add a pinned `requirements.txt` or `pyproject.toml` for reproducible installs.
- Add an `.env.example` template with non-secret placeholders.
- Add Docker compose services for app + Ollama + local Qdrant (optional).
