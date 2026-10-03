# AgentForge Decisions

This file records significant technology and architecture decisions. See `PROGRESS.md` for the current verified implementation status.

## ADR-001 — React + TypeScript for the Frontend
- **Decision:** Use React with TypeScript.
- **Reason:** Component-oriented UI and type-safe API integration.
- **Alternatives considered:** Vanilla JavaScript SPA (rejected for weaker typing/maintainability).
- **Status:** Accepted; implemented.

## ADR-002 — FastAPI + Python for the Backend
- **Decision:** Use Python and FastAPI for HTTP APIs and service orchestration.
- **Reason:** Clear typed REST API development and Pydantic validation.
- **Alternatives considered:** Flask (not selected for this project).
- **Status:** Accepted; implemented.

## ADR-003 — PostgreSQL for Relational Data
- **Decision:** Use PostgreSQL as the primary datastore.
- **Reason:** ACID relational storage and extension ecosystem.
- **Alternatives considered:** SQLite as production runtime (rejected; integration uses PostgreSQL).
- **Status:** Accepted; implemented.

## ADR-004 — pgvector for Vector Search
- **Decision:** Store embeddings in PostgreSQL using pgvector.
- **Reason:** Keeps relational document metadata and vectors in one operational database.
- **Alternatives considered:** Separate vector store (deferred).
- **Status:** Accepted; implemented and tested against PostgreSQL + pgvector.

## ADR-005 — LangChain / Agent Orchestration
- **Decision:** Agent orchestration framework is not selected or implemented in Phases 0–3.
- **Reason:** Keep the current document-RAG vertical slice independently testable; evaluate agent needs in its own phase.
- **Alternatives considered:** LangChain and custom orchestration; decision deferred until Phase 4 design.
- **Status:** Deferred; earlier provisional LangChain preference is superseded for implementation purposes.

## ADR-006 — LLM Provider Abstraction
- **Decision:** Keep answer generation behind an LLM service/provider boundary; default provider settings may target OpenAI.
- **Reason:** Isolates provider SDK usage and allows deterministic fake behavior in automated tests.
- **Alternatives considered:** Direct provider calls from API routes (rejected).
- **Status:** Accepted; current abstraction implemented. No live paid provider is required for CI.

## ADR-007 — Docker for Reproducible Development
- **Decision:** Use Docker Compose for PostgreSQL/pgvector, backend, and frontend development services.
- **Reason:** Repeatable dependency setup and startup ordering.
- **Alternatives considered:** Host-native setup only (not selected as sole workflow).
- **Status:** Accepted; implemented.

## ADR-008 — GitHub Actions for Continuous Integration
- **Decision:** Use GitHub Actions to validate database-backed backend behavior and frontend builds.
- **Reason:** Repeatable repository-hosted verification.
- **Alternatives considered:** External CI service (not needed).
- **Status:** Accepted; implemented. CI provisions PostgreSQL + pgvector, migrates, imports the app, runs pytest, and builds frontend.

## ADR-009 — Typed Backend Configuration
- **Decision:** Use `pydantic-settings` for application configuration.
- **Reason:** Typed environment loading and validation.
- **Alternatives considered:** Scattered `os.getenv` access (rejected).
- **Status:** Accepted; implemented.

## ADR-010 — Frontend API Client Boundary
- **Decision:** Centralize frontend API calls and API base URL handling.
- **Reason:** Keeps components separate from raw environment configuration and HTTP details.
- **Alternatives considered:** Direct fetch/environment access in every component (rejected).
- **Status:** Accepted; implemented.

## ADR-011 — SQLAlchemy Declarative Base and Package Boundaries
- **Decision:** Define one standalone SQLAlchemy 2.x `DeclarativeBase` under `app.db.base`; ORM models import it, and Alembic imports model modules separately.
- **Reason:** Avoid circular imports while ensuring model metadata is populated for migrations.
- **Alternatives considered:** Importing all model modules from the base module (rejected; caused a cycle).
- **Status:** Accepted; implemented.

## ADR-012 — pgvector PostgreSQL Image
- **Decision:** Use `pgvector/pgvector:pg16` in local Compose and CI.
- **Reason:** Provides PostgreSQL and pgvector support without a separate extension build step.
- **Alternatives considered:** Plain PostgreSQL image with manual extension install (rejected for avoidable setup fragility).
- **Status:** Accepted; implemented.

## ADR-013 — Fixed Supported Embedding Dimension
- **Decision:** Support 1536 dimensions for the current schema and default `text-embedding-3-small` model. Runtime rejects unsupported dimensions; migration schema uses the same project constant and does not vary dynamically with arbitrary runtime environment settings.
- **Reason:** Prevent silent ORM/database vector shape mismatch.
- **Alternatives considered:** Environment-dependent migrations (rejected; schema migrations must be deterministic).
- **Status:** Accepted; implemented.

## ADR-014 — Fake Providers for Automated Tests
- **Decision:** Use deterministic fake embeddings and fake LLM behavior in automated tests/CI.
- **Reason:** No paid APIs or credentials are required; tests remain repeatable.
- **Alternatives considered:** Live provider calls in CI (rejected due to cost, secrets, and flakiness).
- **Status:** Accepted; implemented.

## ADR-015 — Synchronous Ingestion for the First RAG Vertical Slice
- **Decision:** Ingest synchronously through upload, extraction, chunking, embedding, and persistence.
- **Reason:** Simpler initial vertical slice with clear service boundaries; transaction handling makes persistence all-or-nothing.
- **Alternatives considered:** Queue-based async processing (deferred).
- **Status:** Accepted; implemented.

## ADR-016 — Isolate PostgreSQL State Across Tests
- **Decision:** Use function-scoped autouse cleanup of document and chunk rows before and after each test that runs in the shared PostgreSQL test database.
- **Reason:** API tests commit real ingestion transactions; leaked records affected later vector retrieval assertions. Cleanup preserves real pgvector query execution while preventing cross-test contamination.
- **Alternatives considered:** Rewriting retrieval query behavior for test artifacts (rejected), or SQLite test substitution (rejected).
- **Status:** Accepted; implemented and verified in green PostgreSQL CI.

## Phase 4 Decision Gate

Agent workflows, dynamic tool calling, authentication, conversation memory, and deployment are not implemented by these decisions. Define explicit scope, threat boundaries, schemas, and tests before starting any such phase.
