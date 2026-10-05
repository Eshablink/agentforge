# AgentForge production deployment runbook

Phase 7 is complete: PR #9 merged to `main` at `63d7d3f0d417d06b2e57fa63874824de4306450d`; GitHub Actions passed on that merge. Phase 8 prepares, but does not itself deploy, a vendor-neutral container release.

## Dependencies and configuration

Provision managed PostgreSQL with pgvector enabled, a Redis-compatible shared rate-limit store, and an HTTPS-terminating reverse proxy. Inject all secrets as environment variables, never image build arguments or source files. `APP_ENV=production`, `DATABASE_URL=postgresql+psycopg://...` (non-development host/credentials), explicit HTTPS `CORS_ORIGINS`, `RATE_LIMIT_BACKEND=redis`, `REDIS_URL=rediss://...`, and explicit `LLM_PROVIDER`/`EMBEDDING_PROVIDER` are mandatory. If either provider is `openai`, inject `OPENAI_API_KEY`. Fake providers are only intended for tests/development; configure real providers for an externally useful deployment.

`AUTH_SECRET` was unused and removed. Passwords remain salted PBKDF2-SHA256; sessions use random bearer credentials stored only as hashes. The `.env.example` file contains *development* examples only. Never deploy it unchanged. For a cross-origin static UI build, set `VITE_API_BASE_URL=https://api.example`; otherwise omit it and proxy all API paths on the UI origin. Vite values are baked into the build; never put secrets in `VITE_*` variables.

## Safe rollout

1. Verify PostgreSQL and pgvector are available. Grant the one-shot migration job permission to create/alter the schema; application replicas should have only ordinary runtime permissions.
2. Run `alembic -c alembic.ini upgrade head` **once**, using the same image/configuration as the API, before sending traffic. Fail the deployment if it fails. Do not run concurrent migrations from each replica; take a backup and rehearse rollbacks. No automatic destructive startup actions run in the API container.
3. Start the API with `uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips <trusted-proxy-addresses>`. Restrict ingress to the trusted proxy. Never trust forwarded headers from arbitrary clients. `/health` is cheap liveness; `/ready` checks database and, in Redis mode, limiter connectivity. Use readiness to gate traffic; do not call paid models from probes.
4. Terminate TLS at the proxy, forward Authorization and correct Host/proto, and configure explicit browser origin(s). Do not cache authenticated API or SSE responses; disable SSE buffering (for example honor `X-Accel-Buffering: no`), use a proxy read timeout longer than `MAX_STREAM_DURATION_SECONDS` plus provider retry budget, and pass disconnects through. The app sends `Cache-Control: no-cache` and `X-Accel-Buffering: no` for SSE. It does **not** terminate TLS itself.
5. Build the frontend with `npm run build`, then serve the resulting `dist/` through a static host/proxy. The existing frontend Dockerfile runs the Vite development server and is **not** a production static-serving image. Local `docker compose up --build` is development only; it uses a one-shot migration service that gates API startup. Do not use local compose's development credentials in production.

## Maintenance and signals

Run `python cleanup_sessions.py` from the backend working directory on a schedule. Each invocation removes up to 500 sessions whose expiry is past, including revoked sessions only after their expiry; active sessions remain. Repeat periodically if backlog exceeds a batch. The cleanup does not run during request processing or startup.

Monitor bounded request-ID-correlated operational events (HTTP status/latency, readiness, rate-limit categories, stream completion/cancellation). Alert on 503 readiness/limiter failures and 429 abuse. Do not log raw provider exceptions, document contents, prompts, passwords, API keys or bearer credentials.

## Remaining limitations

The Redis limiter uses atomic fixed-window counters (not a sliding window), scoped to server-derived per-user IDs and hashed normalized auth emails; dependency failure fails closed. Auth throttling by email alone is not a complete defense against distributed credential stuffing: add edge/IP rate limits and bot protection at the proxy when exposed publicly. There is no deployed infrastructure here, no SSO/MFA, no distributed tracing, and SSE delivers bounded chunks of completed generated output rather than native provider tokens.
