# AgentForge production deployment runbook

Phase 7 PR #9 is merged on main at `63d7d3f0d417d06b2e57fa63874824de4306450d` and verified by main CI 37320957004. Phase 8 prepares but does not itself deploy a vendor-neutral container release.

## Dependencies and configuration

Provision managed PostgreSQL with pgvector, Redis-compatible shared rate limiting over TLS, and an HTTPS-terminating reverse proxy. Inject secrets through environment/secret management, not source code or image build arguments. Production requires APP_ENV=production, explicit non-development DATABASE_URL with postgresql+psycopg, HTTPS CORS_ORIGINS, RATE_LIMIT_BACKEND=redis, REDIS_URL=rediss://..., and explicit LLM_PROVIDER and EMBEDDING_PROVIDER. Inject OPENAI_API_KEY when either selected provider is openai. Fake providers are intended for tests/development, not externally useful AI answers. AUTH_SECRET was unused and removed; existing PBKDF2 and hashed opaque sessions remain.

The .env.example file is for local development, not production. For cross-origin UI builds set VITE_API_BASE_URL to an HTTPS backend URL. Otherwise omit it and proxy API routes through the UI origin. Vite values are embedded in public builds, so never place secrets in VITE_* variables.

## Safe rollout

1. Verify PostgreSQL and pgvector availability; grant schema privileges only to a one-shot migration job. Back up the database and rehearse rollback.
2. From the backend image and working directory run `alembic -c alembic.ini upgrade head` once. Fail rollout on migration failure; do not migrate concurrently in API replicas. Local compose gates API startup on this one-shot job.
3. Start backend API with `uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips <trusted-proxy-addresses>`. Restrict direct backend ingress and do not trust arbitrary forwarded headers. GET /health is cheap liveness; GET /ready checks DB and Redis when selected. Gate traffic on readiness; probes never call paid LLMs.
4. Terminate TLS at the proxy, pass Authorization and trusted Host/proto, disable buffering on `/agent/chat/stream` (honor X-Accel-Buffering: no), and do not cache authenticated responses. SSE sends Cache-Control: no-store. Configure proxy request/body limits and read timeouts longer than stream duration plus provider retry budget, and propagate disconnects. The app does not terminate TLS.
5. Build the frontend with `npm run build` and serve `dist/` via a static host/proxy. The frontend Dockerfile runs a development Vite server, not a production static server. Local docker compose uses development credentials and is not a production template.

## Maintenance and signals

Schedule `python cleanup_sessions.py` from the backend directory: each run removes at most 500 expired records; no active session is deleted. Monitor request-ID-correlated HTTP/readiness/rate-limit/stream status and latency. Do not log prompts, document text, credentials, raw provider exceptions or hidden reasoning.

## Limits

Redis uses atomic fixed windows rather than strict sliding windows; shared-store failures fail closed. Hashed-email auth throttling must be complemented by edge/IP abuse controls against account spraying. Provider timeout is per attempt; retries add elapsed time. There is no live deployment, SSO/MFA, cloud provisioning, distributed tracing or provider-native token streaming.
