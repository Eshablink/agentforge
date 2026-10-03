# AgentForge Architecture

## Current verified architecture (Phases 0–3)

AgentForge currently implements a full-stack document RAG slice. Phase 0–3 are complete; Phase 4 agentic workflow/tool-calling work has not started.

```text
React + TypeScript + Vite
          ↓ HTTP
FastAPI routes and request schemas
          ↓
Application services
  ├─ upload → extract PDF/TXT/Markdown → deterministic chunking
  ├─ embedding provider abstraction → SQLAlchemy persistence
  └─ query → embedding → pgvector cosine retrieval → grounded LLM answer + sources
          ↓
PostgreSQL + pgvector (Alembic-managed schema)
```

## Ingestion and query paths

### Ingestion

```text
Upload validation (type/size)
  → PDF/TXT/Markdown extractor
  → deterministic chunker
  → embedding provider
  → one SQLAlchemy transaction for document + chunks
```

The ingestion transaction is rolled back on persistence failures; APIs translate expected service errors to controlled responses. Docker Compose waits for database health and the backend container applies Alembic migrations before starting the API.

### Query

```text
Question
  → query embedding
  → PostgreSQL/pgvector cosine-distance ordering with bounded top_k
  → retrieved text and document/chunk provenance
  → grounded LLM abstraction
  → answer plus source references (or explicit insufficient-context response)
```

## Layer responsibilities

| Group | Count | Layer/component | Responsibility |
|---|---:|---|---|
| Frontend | 1 | React + TypeScript + Vite | Upload, list documents, ask questions, display answers and sources |
| API | 2 | FastAPI | Health, document upload/list, chat routes |
| Services | 3 | Extractor/chunker | Supported-format extraction and deterministic text segmentation |
| Services | 4 | Embedding/LLM abstractions | Provider boundary; fake providers keep automated tests deterministic and free of paid API requirements |
| Services | 5 | Retrieval/RAG | pgvector cosine similarity, context assembly, answer grounding, source propagation |
| Persistence | 6 | SQLAlchemy 2.x + PostgreSQL/pgvector | Relational metadata, chunk text/vectors, constraints and sessions |
| Schema | 7 | Alembic | Versioned PostgreSQL schema and pgvector extension setup |
| Delivery | 8 | Docker Compose + GitHub Actions | Reproducible local services and PostgreSQL-backed CI |

## Data model

| Group | Count | Table | Purpose |
|---|---:|---|---|
| Models | 1 | `documents` | Filename, content type, metadata, status, timestamps |
| Models | 2 | `document_chunks` | Ordered chunk text, metadata, embedding model, pgvector embedding |

Runtime supports the configured 1536-dimensional embedding schema and rejects unsupported dimensions; Alembic schema is fixed to that supported dimension rather than generated from arbitrary runtime environment values. Alembic imports mapped model modules explicitly; SQLAlchemy declarative base definition is independent of model packages to avoid circular imports.

## Verification

Phase 2–3 passed GitHub Actions PR run 37117613154 and push run 37117610042 (PostgreSQL + pgvector readiness, Alembic upgrade, application import smoke test, full backend pytest, and frontend production build). The integration retrieval test uses actual PostgreSQL/pgvector cosine search. Test setup clears document and chunk records before and after each test to isolate API tests that commit rows.

## Explicit non-goals

No autonomous agents, dynamic tool calling, authentication/authorization, multi-tenancy, complex conversation memory, billing, analytics tools, or production deployment are implemented in Phases 0–3. Do not treat these as present architecture or begin Phase 4 without explicit direction.
