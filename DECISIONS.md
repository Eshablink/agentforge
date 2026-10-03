# AgentForge Decisions

This file records architecture choices for the Phase 0–6 foundation. Verification is tied to specific GitHub Actions runs/commits in `PROGRESS.md` and PR #6. A green CI foundation is not a claim of external production deployment.

## ADR-001 — React + TypeScript + Vite
- **Decision:** Use React, TypeScript and Vite for the browser UI.
- **Reason:** Typed interfaces and incremental development.
- **Status:** Accepted; implemented.

## ADR-002 — FastAPI + Python
- **Decision:** Use FastAPI and typed Pydantic schemas for APIs and service composition.
- **Reason:** Request validation and separation of transport from business logic.
- **Status:** Accepted; implemented.

## ADR-003 — PostgreSQL + pgvector
- **Decision:** PostgreSQL stores relational data and pgvector embeddings/search.
- **Reason:** Keep documents, chunks, ownership, conversations and vectors in one transactional datastore.
- **Status:** Accepted; implemented and tested with PostgreSQL + pgvector.

## ADR-004 — SQLAlchemy base and explicit model registration
- **Decision:** Define `DeclarativeBase` independently in `app.db.base`; import models explicitly for Alembic metadata.
- **Reason:** Avoid circular imports and keep migrations deterministic.
- **Status:** Accepted; implemented.

## ADR-005 — Versioned migrations and fixed vector shape
- **Decision:** Use Alembic for PostgreSQL schema evolution and preserve the supported 1536-dimensional embedding schema; do not derive migrations from runtime overrides.
- **Reason:** Reproducible upgrades and no vector-shape drift.
- **Status:** Accepted; implemented.

## ADR-006 — Provider abstraction with deterministic fakes
- **Decision:** Keep embedding, grounded-answer and agent-decision providers behind interfaces; use fake providers in tests/CI.
- **Reason:** Core logic remains replaceable and CI needs no paid provider key.
- **Status:** Accepted; implemented.

## ADR-007 — Minimal typed agent loop and registered tools
- **Decision:** Use typed decisions and a bounded orchestration loop with three explicitly registered tools: retrieval-backed `document_search`, explicit Decimal arithmetic, and date offset.
- **Reason:** Current workflow does not justify an agent framework; direct orchestration is small and auditable. Arbitrary code execution is prohibited.
- **Status:** Accepted; implemented and CI-tested.

## ADR-008 — Operational execution trace only
- **Decision:** Store and return bounded operational events, tool names and safe status; no hidden reasoning or secrets.
- **Reason:** Debuggability without chain-of-thought retention.
- **Status:** Accepted; implemented.

## ADR-009 — Persistent conversations with bounded recent context
- **Decision:** Store conversations/messages in PostgreSQL, scope them by owner, and send only a bounded recent-message window from the requested conversation.
- **Reason:** Multi-turn continuity without unbounded context or cross-conversation leakage.
- **Status:** Accepted; implemented.

## ADR-010 — Hashed passwords and revocable bearer sessions
- **Decision:** Salt and hash passwords using PBKDF2-SHA256; issue random bearer tokens, persist only token hashes, and enforce expiry/revocation.
- **Reason:** Avoid plaintext credentials and permit server-side logout/session invalidation.
- **Status:** Accepted; implemented. HTTPS/operations remain deployment requirements.

## ADR-011 — Ownership-aware documents and backward compatibility
- **Decision:** Store nullable owner on documents; authenticated retrieval and conversation queries filter by user ID. Legacy Phase 3 routes can access only unowned legacy records.
- **Reason:** Preserve existing single-user records and API compatibility without exposing new private documents.
- **Status:** Accepted; implemented and covered by PostgreSQL integration tests.

## ADR-012 — Isolated PostgreSQL tests
- **Decision:** Clear test-created messages, conversations, chunks, documents, sessions and users around tests in reverse FK dependency order.
- **Reason:** Integration handlers commit; rollback in a different session cannot clean those records.
- **Status:** Accepted; implemented.

## ADR-013 — PostgreSQL-backed CI and health-gated startup
- **Decision:** PostgreSQL + pgvector service, health check, Alembic migration, import smoke test, full pytest and TypeScript/Vite build in GitHub Actions; Docker backend migrates before serving.
- **Reason:** Verify actual persistence/vector behavior and deterministic fresh startup.
- **Status:** Accepted; green Actions run 37129401744 on audit-hardened code. Newer docs/CI runs are referenced in `PROGRESS.md`.

## Deferred scope

No SSO/MFA, rate limiting, billing, advanced analytics, cloud/Kubernetes deployment or Phase 7+ implementation. This is not a deployed production service.
