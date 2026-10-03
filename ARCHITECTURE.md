# AgentForge Architecture

## Architecture Goal

AgentForge is designed as a modular full-stack AI system with clear boundaries between UI, API, document processing, retrieval, and answer generation.

## Current Vertical Slice (Phases 2 + 3)

### Ingestion Pipeline

```text
File
  ↓
Extractor (PDF/TXT/Markdown)
  ↓
Normalized Text
  ↓
Deterministic Chunker
  ↓
Embedding Service
  ↓
PostgreSQL + pgvector
```

### Query Pipeline

```text
Question
  ↓
Query Embedding
  ↓
pgvector Similarity Retrieval
  ↓
Context Construction
  ↓
LLM Service
  ↓
Answer + Source References
```

## Layer Responsibilities

### Frontend (React + TypeScript)

| Group | Count | Responsibility |
|---|---:|---|
| Frontend | 1 | Upload documents |
| Frontend | 2 | List document status/chunk count |
| Frontend | 3 | Ask grounded questions |
| Frontend | 4 | Render answers and cited sources |

### API Layer (FastAPI)

| Group | Count | Endpoint | Responsibility |
|---|---:|---|---|
| API | 1 | `GET /health` | Service health check |
| API | 2 | `POST /documents` | Upload + ingest document pipeline |
| API | 3 | `GET /documents` | List ingested documents |
| API | 4 | `POST /chat` | Retrieval + grounded answer generation |

### Database Layer

| Group | Count | Component | Responsibility |
|---|---:|---|---|
| Data | 1 | PostgreSQL | Relational storage for documents and chunks |
| Data | 2 | pgvector | Dense vector storage and similarity search |
| Data | 3 | Alembic | Schema migrations and extension bootstrap |

## Data Model (Current)

| Group | Count | Table | Purpose |
|---|---:|---|---|
| Models | 1 | `documents` | Document metadata and lifecycle status |
| Models | 2 | `document_chunks` | Chunk text, ordering, and embeddings |

## Service Boundaries

| Group | Count | Service | Responsibility |
|---|---:|---|---|
| Services | 1 | `extractor` | File-type-specific text extraction |
| Services | 2 | `chunker` | Deterministic chunking with overlap |
| Services | 3 | `embedding_service` | Provider-abstracted embedding generation |
| Services | 4 | `retrieval_service` | pgvector similarity retrieval (`top_k`) |
| Services | 5 | `llm_service` | Provider-abstracted answer generation |
| Services | 6 | `rag_service` | Context assembly + answer + source references |

## Retrieval and Grounding Guarantees

| Group | Count | Guarantee |
|---|---:|---|
| Grounding | 1 | Retrieval happens before generation |
| Grounding | 2 | LLM prompt enforces context-only answering |
| Grounding | 3 | Source metadata is returned with each answer |
| Grounding | 4 | Insufficient context returns explicit uncertainty |

## Current Non-Goals

| Group | Count | Not Implemented Yet |
|---|---:|---|
| Deferred | 1 | Autonomous agent workflows |
| Deferred | 2 | Dynamic tool-calling runtime |
| Deferred | 3 | Authentication/authorization |
| Deferred | 4 | Multi-user conversation memory |
| Deferred | 5 | Production deployment hardening |
