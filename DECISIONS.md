# AgentForge Decisions

This file records decisions implemented in the Phase 0–6 foundation and the Phase 7 additions. Verification is tied to specific GitHub Actions runs/commits in `PROGRESS.md` and the Phase 7 PR. Passing CI demonstrates the tested foundation, not external production deployment.

## ADR-001 — React + TypeScript + Vite
- **Decision:** Use React, TypeScript and Vite for the frontend.
- **Reason:** Typed interfaces and incremental UI development.
- **Status:** Accepted; implemented.

## ADR-002 — FastAPI + Python
- **Decision:** Use FastAPI and Pydantic schemas for APIs and service composition.
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
- **Reason:** Direct orchestration is small and auditable; arbitrary code execution is prohibited.
- **Status:** Accepted; implemented and CI-tested.

## ADR-008 — Operational execution trace only
- **Decision:** Store and return bounded operational events, tool names and safe status; no hidden reasoning or secrets.
- **Reason:** Debuggability without chain-of-thought retention.
- **Status:** Accepted; implemented.

## ADR-009 — Persistent conversations with bounded recent context
- **Decision:** Store conversations/messages in PostgreSQL, scope them by owner, and send only a bounded recent-message window.
- **Reason:** Multi-turn continuity without unbounded context or cross-conversation leakage.
- **Status:** Accepted; implemented.

## ADR-010 — Hashed passwords and revocable bearer sessions
- **Decision:** Salt and hash passwords using PBKDF2-SHA256; issue random bearer tokens, persist only token hashes, and enforce expiry/revocation.
- **Reason:** Avoid plaintext credentials and permit server-side logout.
- **Status:** Accepted; implemented. HTTPS/operations remain deployment requirements.

## ADR-011 — Ownership-aware documents and backward compatibility
- **Decision:** Store nullable owner on documents; authenticated retrieval filters by user ID; legacy Phase 3 routes access only unowned legacy records.
- **Status:** Accepted; implemented.

## ADR-012 — Isolated PostgreSQL tests
- **Decision:** Clear test-created rows in reverse FK order around integration tests.
- **Status:** Accepted; implemented.

## ADR-013 — PostgreSQL-backed CI and health-gated startup
- **Decision:** PostgreSQL + pgvector service, Alembic migration, import smoke test, full pytest and frontend build in GitHub Actions.
- **Status:** Accepted; green on prior phases.

## ADR-014 — Normalized provider errors and bounded retries
- **Decision:** Map provider failures to a small safe taxonomy and bound timeouts/retries via settings (`llm_timeout_seconds`, `llm_max_retries`).
- **Reason:** Predictable degradation without leaking secrets; no unbounded waiting.
- **Status:** Accepted; implemented in Phase 7.

## ADR-015 — SSE streaming with a typed, secret-free event contract
- **Decision:** Add `POST /agent/chat/stream` using Server-Sent Events and a fixed event vocabulary (`message_start`, `tool_start`, `tool_result`, `retrieval`, `token`, `message_end`, `error`); keep `/agent/chat` non-streaming for backward compatibility.
- **Reason:** Incremental UX with a stable, auditable wire contract that cannot leak chain-of-thought or secrets.
- **Status:** Accepted; implemented in Phase 7.

## ADR-016 — Process-local rate limiting with documented limits
- **Decision:** Use a single-process sliding-window limiter rather than distributed infrastructure.
- **Reason:** Lightweight protection of expensive endpoints without fragile shared state; deployment limitation is documented.
- **Status:** Accepted; implemented in Phase 7 (multi-worker deployments require a gateway/shared store).

## ADR-017 — Deterministic version-controlled evaluation suite
- **Decision:** Keep RAG/tool/agent regression datasets in Git and run them via a deterministic runner with fake providers; exit non-zero on failure; integrate into CI.
- **Reason:** Reproducible, credential-free regression coverage.
- **Status:** Accepted; implemented in Phase 7.

## Deferred scope

SSO/MFA, deployed cloud/Kubernetes operations, billing, advanced analytics, and distributed (multi-process) rate limiting remain deferred. This is not a deployed production service.
