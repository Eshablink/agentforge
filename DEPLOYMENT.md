# AgentForge deployment runbook

Phases 0–8 are merged; Phases 9–11 are implemented in PR #11 and require final HEAD CI before merge. **No cloud deployment has taken place.** The Deployment Validation workflow uses local PostgreSQL+pgvector and fake providers to build production backend and static frontend images, run migrations before API startup, and probe `/health`, `/ready`, API schema and frontend health. No paid LLM calls or real credentials are used.

## Operator rollout

Provision managed PostgreSQL+pgvector, TLS Redis, an HTTPS reverse proxy and external secret injection. Production APP_ENV requires explicit non-development PostgreSQL credentials, HTTPS CORS origin, provider choice and shared limiter. Run `alembic -c alembic.ini upgrade head` **once** from the backend image before traffic; fail rollout on migration errors. Validate readiness after dependencies are up, then switch traffic. Back up schema/data and rehearse image rollback; database downgrade is not automatic or guaranteed safe.

`frontend/Dockerfile.production` builds a static non-root frontend; `frontend/Dockerfile` remains a Vite development image. Set an HTTPS browser API URL at build or proxy API paths on the same origin. `deploy/nginx.edge.example.conf` is an example only; replace domain/cert/upstream paths, restrict direct API access, and set `--forwarded-allow-ips` to trusted proxy addresses (never `*`). Configure IP-based login/AI request limits, concurrent streams, body limits, SSE `proxy_buffering off`, `proxy_cache off`, `Cache-Control: no-store`, read timeout longer than provider/stream bounds and disconnect forwarding. The application does not terminate TLS.

## Maintenance and limits

Schedule bounded expired-session cleanup separately. Monitor request-ID-correlated, content-free HTTP/readiness/rate-limit/stream metadata. Never log credentials, prompts, answer text, provider frames or document contents. Native OpenAI-compatible final-answer deltas are supported when the provider supports the API; fake/fallback modes remain explicit. Retrieval owner filtering happens in SQL before bounded reranking; source references mean included evidence, not independently verified truth. Redis's shared limiter has fixed-window boundary bursts, and a live cloud rollout is deferred.
