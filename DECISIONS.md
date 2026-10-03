# AgentForge Decisions

This file records accepted architecture decisions for the current project. See `PROGRESS.md` for phase status and verification.

## ADR-001 — React + TypeScript + Vite
- **Decision:** Use React, TypeScript, and Vite for the frontend.
- **Reason:** Component-driven UI, typed API boundaries, and fast build/development feedback.
- **Status:** Accepted; implemented in Phase 1.

## ADR-002 — FastAPI + Python
- **Decision:** Use FastAPI for the backend REST API and Python service layer.
- **Reason:** Typed validation and clear API/service boundaries.
- **Status:** Accepted; implemented in Phase 1 and extended in Phase 3.

## ADR-003 — PostgreSQL + pgvector
- **Decision:** Use PostgreSQL as the relational database and pgvector for vector storage/search.
- **Reason:** Keep document metadata, chunks, and embedding vectors in one ACID datastore.
- **Alternatives:** SQLite or a separate vector store; not used for runtime/integration verification.
- **Status:** Accepted; implemented and verified in Phase 2.

## ADR-004 — SQLAlchemy 2.x declarative base and model registration
- **Decision:** Define the declarative base independently in `app.db.base`; models import the base, while Alembic imports mapped model modules explicitly.
- **Reason:** Avoid circular imports and ensure `Base.metadata` contains all mapped entities during migrations.
- **Status:** Accepted; implemented and migration-verified.

## ADR-005 — Versioned Alembic migrations
- **Decision:** Manage PostgreSQL schema and pgvector extension with Alembic migrations.
- **Reason:** Deterministic fresh database initialization and auditable schema changes.
- **Status:** Accepted; `upgrade head` verified against PostgreSQL + pgvector in CI.

## ADR-006 — Fixed supported embedding dimension
- **Decision:** Support 1536 dimensions for the Phase 2–3 schema. Runtime settings validate this supported dimension; migration schema uses the same authoritative project constant, not arbitrary environment-driven migration logic.
- **Reason:** Prevent runtime/model/database vector dimensions from silently diverging.
- **Status:** Accepted; implemented and migration-verified.

## ADR-007 — Provider abstractions and deterministic test fakes
- **Decision:** Keep embedding and LLM providers behind service abstractions; use fake providers for automated tests.
- **Reason:** Avoid paid API calls and make CI deterministic while preserving a provider extension point.
- **Status:** Accepted; implemented and CI-verified.

## ADR-008 — Synchronous ingestion for the first verified vertical slice
- **Decision:** Ingest synchronously: upload → extract → deterministic chunk → embed → persist in one database transaction.
- **Reason:** Keep the first feature slice easy to understand and verify; add background work only with a future scoped requirement.
- **Status:** Accepted; implemented in Phase 3. Persistence failures roll back document/chunk changes and surface controlled application errors.

## ADR-009 — pgvector cosine retrieval with provenance
- **Decision:** Rank chunks using PostgreSQL/pgvector cosine distance and return document/chunk source references with grounded answers.
- **Reason:** Keep retrieval close to persisted data and make answer evidence traceable.
- **Status:** Accepted; implemented and exercised by PostgreSQL integration tests.

## ADR-010 — Isolate database-writing tests
- **Decision:** Clear document and chunk rows before and after each PostgreSQL test that uses shared test storage.
- **Reason:** API integration tests commit transactions, so per-test rollback alone cannot undo their writes or prevent cross-test retrieval contamination.
- **Status:** Accepted; verified by passing full pytest suite. The real pgvector retrieval test remains intact.

## ADR-011 — Docker Compose startup and CI
- **Decision:** Use `pgvector/pgvector:pg16`; wait for database health before backend startup, apply Alembic migrations before serving, and verify migrations/import/tests/frontend build in GitHub Actions.
- **Reason:** Reliable fresh local startup and reproducible CI with the actual data stack.
- **Status:** Accepted; Phase 2–3 CI verified. See `PROGRESS.md` for the verified run references.

## Deferred scope

Autonomous agents, multi-agent workflows, dynamic tool calling, authentication/authorization, multi-tenancy, billing, complex conversation history, and production deployment remain unimplemented. Do not treat prior long-term technology direction as shipped functionality. Phase 4 has not started.
