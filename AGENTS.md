# AgentForge Engineering Instructions

## Verified baseline and current milestone

Phases 0–7 are COMPLETE on `main`. Phase 7 PR #9 was MERGED at `63d7d3f0d417d06b2e57fa63874824de4306450d`; main GitHub Actions run 37320957004 succeeded. Phase 8 lives on `feat/agentforge-phase-8` and is **not** a deployed service. Do not restart completed phases or merge this branch automatically.

## Preserve security and compatibility

Keep PostgreSQL + pgvector, SQLAlchemy/Alembic, owner-filtered retrieval, PBKDF2-SHA256 passwords, hashed revocable bearer sessions, bounded memory, and registered typed tools. Preserve `/health`, document APIs, RAG, `/agent/chat`, conversations, authentication, and SSE. Never expose chain-of-thought or secrets; no arbitrary Python, shell, filesystem, generated SQL or unrestricted network tools.

## Phase 8 boundaries

Production config must be explicit and fail closed: PostgreSQL with non-development credentials, HTTPS CORS origins, provider selection and shared Redis rate limiting. Local `docker compose` is development only. Run migrations as a one-shot job before API startup; do not run migrations in each replica. Liveness `/health` is cheap; readiness `/ready` checks mandatory dependencies. Browser API config must use HTTPS or a same-origin proxy; SSE remains bounded incremental delivery of generated output, not native model token streaming.

Auth throttling is keyed to hashed normalized email; edge/IP controls remain a deployment responsibility. Shared limiter failure must not silently permit requests. Ingestion enforces extracted-text/page/chunk limits and bounded embedding batches. Session cleanup is explicit, batched and operator-scheduled. See DEPLOYMENT.md.

## Method and verification

Inspect code, tests, migrations, workflows and docs before editing. Preserve public behavior unless within the Phase 8 mandate. Use PostgreSQL + pgvector for integration tests, never SQLite. For every change run Alembic upgrade, import smoke, full backend pytest (which runs deterministic evaluation), frontend build and GitHub Actions on the final PR HEAD. Document current implementation and any limitations accurately; do not claim external production deployment merely because CI passes.
