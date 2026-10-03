# AgentForge Progress

## Current Status

Phases 0–3 are complete, merged to `main`, and verified by post-merge GitHub Actions. Phase 4 has not started.

## Roadmap

| Group | Count | Phase | Status |
|---|---:|---|---|
| Complete | 1 | Phase 0 — Repository blueprint | Complete |
| Complete | 2 | Phase 1 — Application foundation | Complete; merged |
| Complete | 3 | Phase 2 — PostgreSQL + pgvector | Complete; implemented and verified |
| Complete | 4 | Phase 3 — Document ingestion + RAG | Complete; implemented and verified |
| Planned | 5 | Phase 4 — Agentic workflows and tool calling | Not started |
| Deferred | 6 | Authentication, conversation memory, multi-tenancy, billing, deployment | Not implemented |

## Phase 2–3 Delivered Scope

- SQLAlchemy 2.x PostgreSQL sessions and models for documents/chunks, with vector constraints.
- Alembic migration enabling pgvector and creating the schema.
- PDF/TXT/Markdown extraction and upload validation; deterministic chunking; embedding abstraction; transactional persistence and rollback.
- Bounded pgvector cosine retrieval, context-grounded answer abstraction, insufficient-evidence handling, and source references.
- Minimal React/TypeScript/Vite upload, listing, chat, answer, and citation interface.
- Docker Compose waits for database health and runs migrations before the backend serves requests.

## Verification Evidence

- Post-merge Phase 0–3 code commit `67e983772257dc575475e86ebecbe6548c968eb9`: successful Actions run [37117875205](https://github.com/Eshablink/agentforge/actions/runs/37117875205).
- Documentation cleanup merge commit `cded4a9bf39d267200f1de072600d1648b19182f`: successful Actions run [37119471555](https://github.com/Eshablink/agentforge/actions/runs/37119471555).
- Both runs covered PostgreSQL + pgvector service readiness, Alembic upgrade, `app.main` import smoke test, backend pytest (including DB integration/retrieval), and frontend production build.

## Test Isolation

Pytest prepares PostgreSQL and applies Alembic where needed. A function-scoped autouse fixture clears messages, conversations, chunks, documents, sessions and users before and after each test. This isolates real committed API writes while preserving actual PostgreSQL/pgvector tests. Row deletion occurs in a transaction and is rolled back if cleanup fails.

## Deferred Scope

Agents, multi-agent orchestration, dynamic tool calling, authentication/authorization, conversation memory, multi-tenancy, billing, analytics tools, and production deployment remain unimplemented. No Phase 4+ work has been started.

## Notes

Verification claims refer to the exact commits/runs above. Any later code change requires fresh tests/CI before being described as verified.
