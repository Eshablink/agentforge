# AgentForge

Production-style full-stack AI platform for grounded document question answering.

## Current Status

| Group | Count | Item | Status |
|---|---:|---|---|
| Project Status | 1 | Phase 0 — Repository Setup | Complete |
| Project Status | 2 | Phase 1 — Application Foundation | Complete |
| Project Status | 3 | Phase 2 — PostgreSQL + pgvector Foundation | Implemented |
| Project Status | 4 | Phase 3 — Document Ingestion + RAG Foundation | Implemented |
| Project Status | 5 | Agentic workflows/tool calling/auth | Planned |

## Implemented Capabilities

| Group | Count | Capability |
|---|---:|---|
| Backend | 1 | FastAPI application with `/health`, `/documents`, and `/chat` |
| Backend | 2 | SQLAlchemy 2.x models for `documents` and `document_chunks` |
| Backend | 3 | PostgreSQL + pgvector vector storage and similarity retrieval |
| Backend | 4 | Alembic migration with `CREATE EXTENSION vector` |
| Backend | 5 | PDF/TXT/Markdown extraction, deterministic chunking, embedding pipeline |
| Backend | 6 | RAG service with grounded context construction and source references |
| Frontend | 7 | Minimal upload/list/query UI for end-to-end RAG slice |
| Tooling | 8 | Docker Compose with backend, frontend, and pgvector PostgreSQL |

## Out of Scope (Not Yet Implemented)

| Group | Count | Item |
|---|---:|---|
| Deferred Scope | 1 | Autonomous/agentic workflows |
| Deferred Scope | 2 | Tool-calling runtime |
| Deferred Scope | 3 | Authentication/authorization |
| Deferred Scope | 4 | Persistent conversation memory |
| Deferred Scope | 5 | Production deployment hardening |

## Technology Stack

### Frontend

| Group | Count | Stack Item |
|---|---:|---|
| Frontend | 1 | React |
| Frontend | 2 | TypeScript |
| Frontend | 3 | Vite |

### Backend

| Group | Count | Stack Item |
|---|---:|---|
| Backend | 1 | Python |
| Backend | 2 | FastAPI |
| Backend | 3 | SQLAlchemy 2.x |
| Backend | 4 | Alembic |
| Backend | 5 | PostgreSQL + pgvector |

## Environment Variables

Copy and edit:

```bash
cp .env.example .env
```

Key variables:

| Group | Count | Variable | Purpose |
|---|---:|---|---|
| App | 1 | `APP_NAME`, `APP_ENV`, `APP_VERSION`, `API_PREFIX` | API metadata and base path |
| Database | 2 | `DATABASE_URL` | SQLAlchemy/Alembic connection URL |
| Database | 3 | `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT` | Docker PostgreSQL configuration |
| RAG | 4 | `EMBEDDING_PROVIDER`, `EMBEDDING_MODEL`, `EMBEDDING_DIMENSION` | Embedding config boundary |
| RAG | 5 | `LLM_PROVIDER`, `LLM_MODEL`, `OPENAI_API_KEY` | LLM provider and model configuration |
| RAG | 6 | `CHUNK_SIZE`, `CHUNK_OVERLAP`, `RAG_TOP_K_DEFAULT`, `RAG_TOP_K_MAX` | Retrieval and chunking behavior |
| Upload | 7 | `MAX_UPLOAD_SIZE_BYTES`, `SUPPORTED_CONTENT_TYPES` | Upload validation controls |

## Local Setup

### 1) Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Run migrations

```bash
cd backend
alembic -c alembic.ini upgrade head
```

### 3) Start backend

```bash
cd backend
uvicorn app.main:app --reload
```

Backend URL: `http://localhost:8000`

### 4) Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend URL: `http://localhost:5173`

### 5) Docker Compose

```bash
docker compose up --build
```

Uses `pgvector/pgvector:pg16` with persistent `postgres_data` volume.

## API Overview

| Group | Count | Endpoint | Purpose |
|---|---:|---|---|
| Health | 1 | `GET /health` | Service readiness check |
| Documents | 2 | `POST /documents` | Upload + extract + chunk + embed + persist |
| Documents | 3 | `GET /documents` | List ingested documents and chunk counts |
| RAG | 4 | `POST /chat` | Retrieve similar chunks, construct context, generate grounded answer |

### Example chat request

```json
{
  "question": "What does the document say about refunds?",
  "top_k": 5
}
```

### Example chat response

```json
{
  "answer": "...",
  "sources": [
    {
      "document_id": "...",
      "filename": "policy.pdf",
      "chunk_id": "...",
      "chunk_index": 2,
      "similarity": 0.91
    }
  ],
  "retrieved_chunks": 5
}
```

## Testing

```bash
cd backend
pytest

cd ../frontend
npm run build
```

## Architecture Summary

Ingestion pipeline:

```text
File -> Extractor -> Normalized Text -> Chunker -> Embedding Service -> PostgreSQL + pgvector
```

Query pipeline:

```text
Question -> Embedding -> Vector Retrieval -> Context -> LLM -> Answer + Sources
```
