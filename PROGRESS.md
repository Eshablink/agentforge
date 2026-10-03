# AgentForge Progress

## Current Phase

Phases 0–3 — Foundation, PostgreSQL/pgvector, Document Ingestion, and RAG Foundation

Status: COMPLETE. The application, database migration, integration tests, and frontend build passed GitHub Actions on `main` after PR #3 merged.

## Development Roadmap

### Phase 0 — Repository Blueprint
Status: COMPLETE

### Phase 1 — Application Foundation
Status: COMPLETE — merged to `main` in PR #2.

### Phase 2 — PostgreSQL + pgvector
Status: COMPLETE — schema, SQLAlchemy models/sessions, Alembic migration, pgvector enabled and verified.

### Phase 3 — Document Ingestion + RAG Foundation
Status: COMPLETE — PDF/TXT/Markdown ingestion, deterministic chunks, embedding abstraction, pgvector retrieval, grounded answer abstraction, source references, and minimal frontend slice.

### Phase 4 — Agentic Workflows + Tool Calling
Status: NOT STARTED.

## Phase 2 + 3 Verification Evidence

- Pre-merge post-fix PR verification passed on commit `9099462e914c40d843f6080f96efd016802bdd80`: PR run [37117686546](https://github.com/Eshablink/agentforge/actions/runs/37117686546) and push run [37117684450](https://github.com/Eshablink/agentforge/actions/runs/37117684450).
- Post-merge `main` verification passed on merge commit `67e983772257dc575475e86ebecbe6548c968eb9`: run [37117875205](https://github.com/Eshablink/agentforge/actions/runs/37117875205).
- Each verification covered PostgreSQL + pgvector service readiness, Alembic migration, `app.main` import smoke test, full backend pytest (including DB integration/retrieval), and frontend production build.

## Test Database Isolation

The pytest session fixture prepares PostgreSQL and applies Alembic when necessary. An autouse function-scoped fixture deletes document-chunk rows and documents before and after every test. This is required because API ingestion tests commit records. It preserves transaction rollback in tests that create their own rows and prevents shared committed records from changing vector retrieval results.

## Scope Boundaries

Not implemented:

- autonomous agents or multi-agent workflows
- dynamic tool calling
- authentication or authorization
- persistent conversation memory or multi-tenancy
- structured database query, Python analysis, web retrieval, or chart tools
- production deployment hardening

## Readiness

The verified Phase 0–3 foundation is ready for Phase 4 planning. Phase 4 should begin with a separate explicit design/scope and threat-model pass. No Phase 4 code has been started.
