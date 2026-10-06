# AgentForge deployment runbook

Phases 0–8 are COMPLETE and MERGED on main. Phases 9–11 are implemented on PR #11 and deployment-artifact validated only when the **final PR HEAD** has a green `AgentForge Deployment Validation` workflow. **No cloud production deployment has occurred.**

## Operator rollout (not performed by CI)

1. Provision managed PostgreSQL+pgvector, Redis over TLS, an HTTPS reverse proxy and injected secrets. Production settings require explicit non-development PostgreSQL credentials, HTTPS CORS origin, provider selection and shared Redis limiting.
2. Back up data, then run `alembic -c alembic.ini upgrade head` **once** using the backend image before routing traffic. A failed migration stops rollout; rollback of database schema is not automatic or necessarily safe.
3. Start the unprivileged backend and static frontend images; gate traffic on backend `/ready`. `/health` is cheap liveness; `/ready` checks serving dependencies. The Deployment Validation workflow builds both production images, uses PostgreSQL+pgvector plus a TLS-enabled Redis validation service, runs Alembic once before serving traffic, validates production settings and fake-provider rejection, proves `/ready` fails closed when Redis is unavailable, runs backend/frontend smoke probes and checks Nginx syntax. It does not make paid provider calls or deploy a cloud service.
4. Configure `deploy/nginx.edge.example.conf` for real domains, certificates and upstreams. Restrict direct API access. Trust only proxy IPs via Uvicorn `--forwarded-allow-ips` (never `*`); enforce edge IP authentication/AI limits, concurrent streams and request body caps. SSE requires `proxy_buffering off`, `proxy_cache off`, `Cache-Control: no-store`, sufficient read timeout and disconnect forwarding. API bearer credentials must never be logged.
5. Monitor request-ID-correlated, content-free status, readiness, rate-limit and stream lifecycle metrics. Schedule the bounded expired-session cleanup separately; repeat in batches if needed. Image/traffic rollback must be planned by the operator; no automatic rollback is implemented.

## Provider, retrieval and evaluation limits

OpenAI-compatible native final-answer text deltas are supported after structured decisions; fake and completed-answer fallback modes are explicit. Tool calls remain typed, validated and owner-scoped. PostgreSQL owner predicate applies before a bounded candidate rerank; RAG sources represent included context, not mathematical proof of generated claims. Deterministic CI fixture pass rates do not measure real-world model factuality or retrieval hit rate. The Redis limiter uses a fixed window with boundary bursts, and the edge example is a template rather than a production configuration. No paid provider or real cloud credential is used for CI. SSO/MFA and broad live model-quality benchmarking remain deferred.
