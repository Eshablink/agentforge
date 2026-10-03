# AgentForge Architecture

## Current State

Phases 0–3 are implemented and verified: repository/application foundations plus a PostgreSQL/pgvector document-ingestion and grounded-RAG vertical slice. See `PROGRESS.md` for the post-merge CI evidence. Agent orchestration, dynamic tool calling, authentication, and conversation memory are not implemented.

## Implemented Ingestion Pipeline

```text
PDF/TXT/Markdown upload
  ↓
Type/size validation and text extraction
  ↓
Normalized text
  ↓
Deterministic chunking
  ↓
Embedding provider abstraction
  ↓
PostgreSQL + pgvector persistence (transactional)
```

## Implemented Query Pipeline

```text
Question
  ↓
Query embedding
  ↓
pgvector cosine-distance retrieval (bounded top_k)
  ↓
Context construction
  ↓
LLM provider abstraction
  ↓
Grounded answer + source references
```

## Layer Responsibilities

### Frontend (React + TypeScript + Vite)

| Group | Count | Responsibility |
|---|---:|---|
| Frontend | 1 | Upload documents |
| Frontend | 2 | List ingested document status/chunk counts |
| Frontend | 3 | Ask grounded questions |
| Frontend | 4 | Render answer and source references |

### API and Service Layers

| Group | Count | Component | Responsibility |
|---|---:|---|
| API | 1 | `GET /health` | Health response |
| API | 2 | `POST /documents` | Upload and ingest document |
| API | 3 | `GET /documents` | List documents and chunk counts |
| API | 4 | `POST /chat` | Retrieval and grounded answer generation |
| Service | 5 | `extractor`, `chunker` | Text extraction and deterministic chunk construction |
| Service | 6 | `embedding_service`, `retrieval_service` | Embedding abstraction and pgvector search |
| Service | 7 | `llm_service`, `rag_service` | Answer-provider abstraction, context assembly, response/source construction |

### Database and Migrations

| Group | Count | Component | Responsibility |
|---|---:|---|
| Data | 1 | PostgreSQL | Relational document/chunk storage |
| Data | 2 | pgvector | Vector storage and cosine-distance query support |
| Data | 3 | SQLAlchemy 2.x | Declarative models, sessions, and ORM operations |
| Data | 4 | Alembic | Versioned schema migration and pgvector extension bootstrap |

`app.db.base` defines the declarative base independently. Model modules register their mappings, and Alembic imports model modules explicitly to populate metadata without circular imports. The supported schema/runtime embedding dimension is 1536. Runtime settings reject unsupported dimensions; migrations are versioned, not generated dynamically from environment values.

### Startup and Verification

Docker Compose waits for PostgreSQL health. The backend container runs `alembic upgrade head` before starting Uvicorn, so a fresh Compose database gets the schema without a manual initialization step. CI uses a PostgreSQL + pgvector service, applies Alembic, runs the import smoke test and full backend pytest suite, then builds the frontend.

## Data Model

| Group | Count | Table | Purpose |
|---|---:|---|---|
| Models | 1 | `documents` | Uploaded document metadata and lifecycle status |
| Models | 2 | `document_chunks` | Chunk text/order, metadata, embedding model, and vector |

## Grounding Behavior

| Group | Count | Behavior |
|---|---:|---|
| Grounding | 1 | Retrieval precedes answer generation |
| Grounding | 2 | LLM instructions constrain answers to retrieved context |
| Grounding | 3 | Source identifiers, filename, chunk index, and similarity are returned |
| Grounding | 4 | Empty retrieval yields explicit insufficient-context response |

## Phase 4+ Non-Goals (Not Yet Implemented)

| Group | Count | Deferred capability |
|---|---:|---|
| Deferred | 1 | Autonomous or multi-agent workflows |
| Deferred | 2 | Dynamic tool-calling runtime |
| Deferred | 3 | Authentication and authorization |
| Deferred | 4 | Multi-user conversation memory |
| Deferred | 5 | Production deployment hardening |
