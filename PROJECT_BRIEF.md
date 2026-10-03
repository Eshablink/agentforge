# AgentForge Project Brief

## Project summary

AgentForge is a full-stack document question-answering application. The completed Phase 0–3 product slice lets users upload supported documents, persist and search their content with PostgreSQL/pgvector, and receive grounded answers with source references through a minimal web UI.

## Project status

| Group | Count | Phase/capability | Status |
|---|---:|---|---|
| Completed | 1 | Phase 0 — Repository setup and blueprint | Complete |
| Completed | 2 | Phase 1 — FastAPI and React application foundation | Complete; merged into `main` |
| Completed | 3 | Phase 2 — PostgreSQL + pgvector, SQLAlchemy 2.x, Alembic | Implemented and CI-verified |
| Completed | 4 | Phase 3 — Ingestion, retrieval, grounded RAG, source references, minimal UI | Implemented and CI-verified |
| Planned | 5 | Phase 4 — Agentic workflows and tool calling | Not started |
| Planned | 6 | Authentication, authorization, multi-tenancy, complex conversation history, billing, production deployment | Deferred |

## Implemented and verified capabilities

| Group | Count | Capability | Details |
|---|---:|---|---|
| Application | 1 | FastAPI and React + TypeScript + Vite | Foundation routes and minimal RAG UI |
| Database | 2 | PostgreSQL + pgvector | SQLAlchemy 2.x models, session management, vector retrieval, Alembic schema migration |
| Ingestion | 3 | PDF, TXT, and Markdown | Type/size validation, text extraction, deterministic chunking, provider-abstracted embeddings, transactional persistence |
| Retrieval | 4 | Similarity search | pgvector cosine distance and bounded `top_k`, with document/chunk provenance |
| RAG | 5 | Grounded answers | Retrieved context passed through an LLM abstraction; explicit insufficient-context response and source references |
| Verification | 6 | GitHub Actions | PostgreSQL/pgvector service, migration, import smoke test, backend pytest, and frontend production build |

Phase 2–3 checks passed in GitHub Actions on PR #3 before merge. The verified PR run was 37117613154 and the matching push run was 37117610042 on commit `7f77050e739047bc19d955cdc2498054c228b7d4`. Documentation follow-up commit `9099462e914c40d843f6080f96efd016802bdd80` also received successful push and PR CI checks. Re-run checks after later application changes; do not treat historical verification as proof of new code.

## Technology direction

| Group | Count | Technology |
|---|---:|---|
| Frontend | 1 | React, TypeScript, Vite |
| Backend | 2 | Python, FastAPI, Pydantic, SQLAlchemy 2.x |
| Data | 3 | PostgreSQL, pgvector, Alembic |
| AI integration | 4 | Embedding and LLM provider abstractions; fake providers for CI; optional environment-configured external provider |
| Delivery | 5 | Docker Compose and GitHub Actions |

## Explicit boundaries

The shipped scope ends at the Phase 2–3 document RAG vertical slice. Autonomous agents, multi-agent orchestration, dynamic tool calling, SQL/Python/web/chart tools, authentication, authorization, multi-tenancy, billing, persistent complex conversation history, and production deployment are **not implemented**. Keep these items planned until separately scoped, implemented, and verified.

Automated tests use fake providers and PostgreSQL + pgvector; they do not require paid LLM APIs or use SQLite in place of vector integration tests.
