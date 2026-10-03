# AgentForge Architecture

## Current Verified Architecture — Phases 0–3

AgentForge currently delivers a full-stack document ingestion and grounded-RAG application. PostgreSQL + pgvector stores document metadata, chunk text, and embeddings; FastAPI exposes the API; React/TypeScript/Vite provides the minimal user interface.

```text
React + TypeScript + Vite
          ↓ HTTP
FastAPI routes and schemas
          ↓
Application services
  ├─ upload → extract PDF/TXT/Markdown → deterministic chunking
  ├─ embedding provider → transactional SQLAlchemy persistence
  └─ query → embedding → pgvector cosine retrieval → grounded answer + sources
          ↓
PostgreSQL + pgvector (Alembic-managed schema)
```

## Data Flows

### Ingestion

```text
Upload validation (format/size)
  → extraction
  → deterministic chunking
  → embedding provider abstraction
  → document and chunks persisted transactionally
```

On persistence failures, ingestion rolls back and returns a controlled service/API error. Docker Compose waits for PostgreSQL health; backend startup applies `alembic upgrade head` before Uvicorn starts.

### Query

```text
Question → embedding → bounded pgvector cosine-distance search
         → retrieved chunk text and provenance → LLM abstraction
         → grounded answer and source references
```

An empty retrieval result yields an explicit insufficient-context response. Retrieval is handled by the shared Phase 3 retrieval service.

## Responsibilities

| Group | Count | Layer | Responsibility |
|---|---:|---|---|
| Frontend | 1 | React + TypeScript + Vite | Upload/list documents, ask questions, display answers and sources |
| API | 2 | FastAPI | Health, upload/list documents, chat |
| Services | 3 | Extractor/chunker | Supported-format text extraction and deterministic chunks |
| Services | 4 | Embeddings/LLM | Provider abstractions; fake providers for deterministic CI |
| Services | 5 | Retrieval/RAG | pgvector cosine retrieval, context assembly, grounded responses and citations |
| Persistence | 6 | SQLAlchemy 2.x + PostgreSQL/pgvector | Relational records, chunks, vectors, constraints, sessions |
| Schema | 7 | Alembic | Versioned schema and pgvector extension bootstrap |
| Delivery | 8 | Docker Compose + GitHub Actions | Local DB health/migration startup and PostgreSQL-backed CI |

## Data Model

| Group | Count | Table | Purpose |
|---|---:|---|---|
| Models | 1 | `documents` | Filename, content type, metadata, status, timestamps |
| Models | 2 | `document_chunks` | Ordered chunk text, metadata, embedding model and vector |

SQLAlchemy's declarative base is independent of model packages. Alembic imports model modules to register metadata. The current schema and runtime support 1536-dimensional embeddings; unsupported runtime dimensions are rejected, and migrations do not derive their schema from arbitrary environment overrides.

## Verification Evidence

- Phase 0–3 merge commit `67e983772257dc575475e86ebecbe6548c968eb9` passed in GitHub Actions run [37117875205](https://github.com/Eshablink/agentforge/actions/runs/37117875205).
- Documentation cleanup merge commit `cded4a9bf39d267200f1de072600d1648b19182f` passed in run [37119471555](https://github.com/Eshablink/agentforge/actions/runs/37119471555).
- Both runs included PostgreSQL + pgvector readiness, Alembic migration, application import smoke test, backend pytest and frontend production build.
- PostgreSQL integration tests exercise actual pgvector similarity. Test setup clears committed test rows before and after each test to isolate fixtures.

## Deferred Scope

Agents, multi-agent orchestration, dynamic tool calling, authentication/authorization, conversation memory, multi-tenancy, billing, analytics tools, and production deployment are not implemented. Phase 4 has not started.
