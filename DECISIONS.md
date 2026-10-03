# AgentForge Decisions

This file records architecture choices for the implemented Phase 0–3 document-RAG foundation. See `PROGRESS.md` for verification evidence and deferred roadmap scope.

## ADR-001 — React + TypeScript + Vite
- **Decision:** Use React, TypeScript and Vite for the frontend.
- **Reason:** Component-based UI with typed API boundaries.
- **Status:** Accepted; implemented in Phase 1.

## ADR-002 — FastAPI + Python
- **Decision:** Use FastAPI for the HTTP API and Python service layer.
- **Reason:** Clear request validation and API/service separation.
- **Status:** Accepted; implemented.

## ADR-003 — PostgreSQL + pgvector
- **Decision:** PostgreSQL stores relational records and pgvector embeddings.
- **Reason:** Keep document metadata, chunks and vectors in one ACID datastore.
- **Alternatives considered:** SQLite or a separate vector store (not used for verified DB integration).
- **Status:** Accepted; implemented and CI-verified.

## ADR-004 — Standalone SQLAlchemy declarative base
- **Decision:** Define `DeclarativeBase` independently in `app.db.base`; model modules import it and Alembic imports model modules for metadata registration.
- **Reason:** Avoid circular imports and ensure complete migration metadata.
- **Status:** Accepted; implemented.

## ADR-005 — Deterministic Alembic migrations
- **Decision:** Use versioned migrations for the PostgreSQL schema and vector extension; do not derive schema from arbitrary runtime configuration.
- **Reason:** Reproducible upgrades and schema history.
- **Status:** Accepted; verified with `upgrade head` on PostgreSQL + pgvector.

## ADR-006 — Fixed supported embedding dimension
- **Decision:** Support 1536 dimensions in the current schema; runtime validation rejects unsupported dimensions and migrations use the same project constant.
- **Reason:** Prevent model/database vector shape divergence.
- **Status:** Accepted; implemented.

## ADR-007 — Provider abstraction with deterministic test fakes
- **Decision:** Keep embedding and answer generation behind provider abstractions; use fake providers for automated tests.
- **Reason:** Keep CI reproducible without paid API credentials.
- **Status:** Accepted; implemented and verified.

## ADR-008 — Synchronous transactional ingestion
- **Decision:** The first vertical slice extracts, chunks, embeds and persists in one synchronous request/transaction.
- **Reason:** Small, verifiable initial scope; persistence failures roll back the transaction.
- **Status:** Accepted; implemented.

## ADR-009 — pgvector cosine retrieval with provenance
- **Decision:** Use PostgreSQL/pgvector cosine distance with bounded `top_k` and return document/chunk sources.
- **Reason:** Traceable evidence from the same persistence layer.
- **Status:** Accepted; exercised by PostgreSQL integration tests.

## ADR-010 — Isolate PostgreSQL-writing tests
- **Decision:** Clear document/chunk records before and after each test against the shared test database.
- **Reason:** API upload tests commit data; rollback of another test’s session cannot undo those commits.
- **Status:** Accepted; validated by the passing full pytest suite.

## ADR-011 — Docker Compose and CI startup sequence
- **Decision:** Use `pgvector/pgvector:pg16`; wait for DB health, apply Alembic, then start the API. CI uses the same PostgreSQL/pgvector family.
- **Reason:** Reproducible local initialization and actual-database CI.
- **Status:** Accepted; verified in post-merge Actions runs listed in `PROGRESS.md`.

## Deferred decisions and scope

No agent framework has been selected for the current implementation; LangChain/agent orchestration is deferred. Agents, tool calling, authentication, authorization, conversation memory, multi-tenancy, billing, analytics tools, and deployment are outside Phase 0–3 and remain unimplemented. Do not interpret earlier long-term technology ideas as implemented decisions.
