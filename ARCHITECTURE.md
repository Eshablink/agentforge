# AgentForge Architecture

**Baseline:** Phases 0–7 COMPLETE on `main`; Phase 7 PR #9 MERGED in `63d7d3f0d417d06b2e57fa63874824de4306450d`, verified by main CI run 37320957004. Phase 8 hardens deployment without changing the owner-aware RAG, typed tools, bounded memory or existing public APIs.

## Serving path

The React/Vite build uses an HTTPS `VITE_API_BASE_URL` or same-origin reverse proxy for JSON and authenticated SSE. The TLS-terminating proxy forwards bearer headers only to the API and disables SSE buffering/caching. FastAPI handles authentication and owner checks, then conversation/agent services invoke allowlisted calculator, date, or owner-filtered document-search tools; PostgreSQL + pgvector stores relational/vector data. The application container does not run migrations: a separate one-shot Alembic job upgrades the schema before startup. Failed migrations stop rollout.

## Configuration and dependency gates

`APP_ENV` is development, test or production. Production requires explicitly injected PostgreSQL+psycopg URL with non-development host/credentials, explicit HTTPS CORS origins, explicit provider choices, and Redis shared limiting. `AUTH_SECRET` was unused by the hashed opaque-token model and has been removed from the example and local compose. No secrets are baked into images or Vite. `/health` is liveness (no external access); `/ready` checks `SELECT 1` and Redis ping when shared limiting is selected, returning a safe 503 on failure. No model calls are made in probes.

## Rate limiting and abuse protection

Both in-memory sliding window (development/test) and Redis atomic fixed-window implementations satisfy the same `Limiter` protocol. Production cannot select memory; Redis connection failures fail closed. AI limiter keys are authenticated user IDs; registration/login keys are hashes of normalized email addresses. A proxy should additionally impose edge/IP abuse limits because email-only throttling cannot prevent distributed account spraying. Both stores bound window duration; Redis keys expire automatically. Limiters do not persist bearer credentials.

## Bounded ingestion and maintenance

Extraction stops on byte/page/character thresholds. Ingestion checks estimated chunk count before allocating chunks, and flushes embedding batches within one transaction. On failure the transaction rolls back. `python cleanup_sessions.py` deletes at most 500 expired session records per run; active sessions are retained. Cleanup never runs in application startup or request flow.

## Existing safety contracts

`/agent/chat` remains backward compatible; SSE delivers generated output in bounded chunks, not provider-native tokens. Authenticated stream and conversation owner checks remain, with one request ID in response header, SSE start and telemetry. No arbitrary Python, shell, filesystem, generated SQL, or unrestricted network tools execute. The evaluation suite remains deterministic and free of paid provider calls.

## Operational limitations

This branch has not been deployed. Redis provides shared fixed-window rather than strict sliding-window behavior; managed PostgreSQL/pgvector, Redis and HTTPS termination must be provisioned externally. Reverse proxies must configure trusted forwarded addresses, SSE buffering and timeouts; see DEPLOYMENT.md. SSO/MFA and cloud infrastructure automation are deferred.
