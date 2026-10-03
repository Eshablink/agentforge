# AgentForge

Full-stack AI application for document ingestion and grounded document question answering. Phases 0–3 provide a verified foundation and RAG vertical slice; agent workflows and tool calling remain future work.

## Current Status

| Group | Count | Phase/item | Status |
|---|---:|---|---|
| Project Status | 1 | Phase 0 — Repository Setup | Complete |
| Project Status | 2 | Phase 1 — Application Foundation | Complete |
| Project Status | 3 | Phase 2 — PostgreSQL + pgvector | Complete and CI-verified |
| Project Status | 4 | Phase 3 — Document Ingestion + RAG Foundation | Complete and CI-verified |
| Project Status | 5 | Phase 4 — Agentic workflows/tool calling | Not started |

Latest post-merge `main` verification: GitHub Actions run [37117875205](https://github.com/Eshablink/agentforge/actions/runs/37117875205), successful on 2026-10-03.

## Implemented Capabilities

| Group | Count | Capability |
|---|---:|---|
| Backend | 1 | FastAPI application with `/health`, `/documents`, and `/chat` |
| Backend | 2 | SQLAlchemy 2.x models and PostgreSQL sessions for documents and chunks |
| Backend | 3 | PostgreSQL + pgvector vector persistence and cosine similarity retrieval |
| Backend | 4 | Alembic migration creates pgvector extension and schema |
| Backend | 5 | PDF/TXT/Markdown extraction, validated uploads, deterministic chunking and embedding abstraction |
| Backend | 6 | Grounded RAG context assembly, controlled answer generation, source references |
| Frontend | 7 | Minimal upload/list/question/answer/source vertical-slice UI |
| Tooling | 8 | Docker Compose with PostgreSQL/pgvector, backend migrations before API start, and GitHub Actions verification |

## Deferred Scope

| Group | Count | Item |
|---|---:|---|
| Deferred | 1 | Autonomous/agentic workflows |
| Deferred | 2 | Tool-calling runtime |
| Deferred | 3 | Authentication and authorization |
| Deferred | 4 | Persistent conversation memory or multi-tenancy |
| Deferred | 5 | Structured-data query, Python analysis, external retrieval, and chart tools |
| Deferred | 6 | Production deployment hardening |

## Technology Stack

| Group | Count | Area | Technologies |
|---|---:|---|---|
| Frontend | 1 | UI | React, TypeScript, Vite |
| Backend | 2 | API/services | Python, FastAPI, Pydantic, SQLAlchemy 2.x |
| Data | 3 | Persistence | PostgreSQL, pgvector, Alembic |
| Delivery | 4 | Local/CI | Docker Compose, GitHub Actions |

## Local Setup

Create and configure environment variables:

```bash
cp .env.example .env
```

Install backend dependencies:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

For local runtime, start PostgreSQL with pgvector (for example, `docker compose up db -d` from repository root), then apply the schema and run the API:

```bash
cd backend
alembic -c alembic.ini upgrade head
uvicorn app.main:app --reload
```

Backend URL: `http://localhost:8000`.

Start the frontend separately:

```bash
cd frontend
npm install
npm run dev
```

Frontend URL: `http://localhost:5173`.

Or start the full Docker development stack with deterministic database readiness and backend migration-before-start:

```bash
docker compose up --build
```

The Docker Compose stack uses `pgvector/pgvector:pg16` and a persistent `postgres_data` volume. First-time database schema initialization is run by the backend container before the API server starts.

## API Overview

| Group | Count | Endpoint | Purpose |
|---|---:|---|---|
| Health | 1 | `GET /health` | Health check |
| Documents | 2 | `POST /documents` | Upload, extract, chunk, embed and persist |
| Documents | 3 | `GET /documents` | List ingested documents and chunk counts |
| RAG | 4 | `POST /chat` | Retrieve relevant chunks, construct context, generate grounded answer |

## Automated Verification

GitHub Actions provisions PostgreSQL + pgvector, applies `alembic upgrade head`, runs an import smoke test and the backend pytest suite (including DB integration/retrieval tests), and builds the production frontend. Both post-merge backend and frontend checks passed in run 37117875205.

For local verification, with PostgreSQL/pgvector running and `DATABASE_URL` configured:

```bash
cd backend
pytest

cd ../frontend
npm run build
```

Automated tests use fake embedding and LLM providers; no paid API key is needed.

## Architecture Summary

```text
Upload → Extract → Deterministic chunks → Embeddings → PostgreSQL + pgvector
Question → Query embedding → Cosine vector retrieval → Grounded context → LLM abstraction → Answer + sources
```
