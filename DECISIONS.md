# AgentForge Decisions

This file records the decisions implemented in the current Phase 0–6 foundation. Completion/verification evidence is tracked in `PROGRESS.md` and PR #6. Passing CI establishes a tested engineering foundation; it does not mean the application is deployed to production.

## ADR-001 — React + TypeScript + Vite
- **Decision:** Use React, TypeScript and Vite for the browser UI.
- **Reason:** Typed interfaces and incremental application development.
- **Status:** Accepted; implemented.

## ADR-002 — FastAPI + Python
- **Decision:** Use FastAPI and typed Pydantic schemas for API contracts and service composition.
- **Reason:** Explicit routing, validation, and separation from frontend behavior.
- **Status:** Accepted; implemented.

## ADR-003 — PostgreSQL + pgvector
- **Decision:** Use PostgreSQL as relational store and pgvector for embeddings/cosine similarity.
- **Reason:** Keep documents, chunks, ownership, conversations and vectors in one ACID database.
- **Status:** Accepted; phases 2–6 migrations and integration tests use PostgreSQL + pgvector.

## ADR-004 — SQLAlchemy 2.x declarative base and Alembic registration
- **Decision:** Define a standalone `DeclarativeBase` in `app.db.base`; import model modules explicitly for Alembic metadata.
- **Reason:** Avoid circular imports and make migrations deterministic.
- **Status:** Accepted; implemented.

## ADR-005 — Fixed embedding dimension and versioned migrations
- **Decision:** Maintain the supported 1536-dimensional embedding schema and reject unsupported runtime dimensions; do not generate migrations from environment-specific schema values.
- **Reason:** Avoid database/vector shape drift and make upgrades reproducible.
- **Status:** Accepted; implemented.

## ADR-006 — Provider abstractions and test fakes
- **Decision:** Keep embedding, answer-generation, and agent-decision providers behind application-independent interfaces; CI uses deterministic fakes.
- **Reason:** Core services stay testable without paid APIs and provider output remains untrusted.
- **Status:** Accepted; implemented.

## ADR-007 — Bounded registered-tool agent, no general code executor
- **Decision:** Agent decisions use typed structured schemas. Only explicitly registered tools execute: existing retrieval-backed `document_search`, explicit Decimal calculator, and deterministic date-offset utility.
- **Reason:** A small auditable tool surface with schema validation, allowlisting and bounded outputs is safer than arbitrary Python/shell/SQL execution.
- **Alternatives:** LangChain/LangGraph and custom unrestricted tool execution; no orchestration framework is required for the current simple loop, and arbitrary execution is rejected.
- **Status:** Accepted; implemented and covered by CI tests.

## ADR-008 — Operational trace, not chain-of-thought
- **Decision:** Store/return bounded operational event names, tool names and safe status details; never persist hidden reasoning or secrets.
- **Reason:** Debuggability with less sensitive model/user data exposure.
- **Status:** Accepted; implemented.

## ADR-009 — Persistent user-owned conversations with bounded recent memory
- **Decision:** Store conversations/messages in PostgreSQL; include only a bounded recent message window from the conversation being updated.
- **Reason:** Multi-turn continuity without unbounded context growth or cross-conversation leakage.
- **Status:** Accepted; implemented.

## ADR-010 — Bearer sessions with hashed passwords and revocation
- **Decision:** Hash passwords with salted PBKDF2-SHA256; issue opaque random bearer tokens, store only token hashes, and enforce session expiry/revocation server-side.
- **Reason:** Avoid plaintext credentials and allow sessions to be invalidated without retaining raw tokens.
- **Status:** Accepted; implemented. Deployment must use HTTPS and secret management.

## ADR-011 — Per-user authorization and legacy compatibility
- **Decision:** Store document owner IDs and scope private document retrieval and conversation access to authenticated user identity. Preserve legacy Phase 3 routes for records with no owner; exclude owned rows from their queries.
- **Reason:** Maintain existing single-user behavior without exposing new users’ private records.
- **Status:** Accepted; implemented and exercised by PostgreSQL ownership tests.

## ADR-012 — Test isolation across committed database writes
- **Decision:** Clear test data before and after tests against the shared PostgreSQL test database, in reverse FK dependency order.
- **Reason:** API tests commit transactions; per-test rollback alone cannot undo other sessions’ commits.
- **Status:** Accepted; implemented.

## ADR-013 — Docker and GitHub Actions
- **Decision:** Use PostgreSQL health-gated startup, Alembic-before-Uvicorn, and Actions checks for PostgreSQL/pgvector, migration, import, backend tests, and frontend build.
- **Reason:** Reproducible fresh initialization and test against the actual storage engine.
- **Status:** Accepted; implemented and green on the latest audited PR commit/run recorded in `PROGRESS.md`.

## Deferred decisions

Not implemented: SSO/MFA, formal rate limiting, cloud deployment/operations, billing, advanced analytics, or any Phase 7+ scope. This repository is not represented as deployed production software.
