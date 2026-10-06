# AgentForge

AgentForge provides PostgreSQL/pgvector RAG, typed safe agent tools, authenticated conversations, and incremental SSE delivery. **Phases 0–7 are complete**; Phase 7 PR #9 merged to `main` in `63d7d3f0d417d06b2e57fa63874824de4306450d` with passing main CI. Phase 8 adds production deployment hardening on this branch; this is not a claim that a live environment has been deployed.

## Phase 8 overview

Production configuration now requires explicit PostgreSQL credentials and host, HTTPS CORS origins, explicit provider selection and Redis-backed rate limiting. `/health` is dependency-free liveness; `/ready` tests PostgreSQL and the shared limiter without paid calls. A one-shot Alembic migration must complete before API startup; runtime replicas do not migrate. The API container runs as a non-root user. The browser uses a configured HTTPS API URL or same-origin proxy (also for SSE).

A shared atomic fixed-window limiter protects AI endpoints, while hashed normalized email keys throttle registration/login; shared-store failure blocks expensive/auth calls rather than silently disabling protection. Extraction/page/chunk limits and small embedding batches bound ingestion pressure. Expired sessions can be pruned via explicit bounded maintenance. See [DEPLOYMENT.md](DEPLOYMENT.md) for setup, TLS proxying, migration rollout, probes, SSE buffering and operational limits.

## Local development

```bash
cp .env.example .env
docker compose up --build
```

The compose stack is **development only**; its one-shot migration service gates API startup on PostgreSQL health. For tests/CI, use PostgreSQL + pgvector, fake providers, and `pytest` in `backend/`. Full pytest invokes `evaluation/runner/run_evals.py` without paid API calls. Frontend verification is `npm run build` in `frontend/`. Browser `VITE_API_BASE_URL` is optional for same-origin proxying; when set in production it must be an HTTPS URL.

## Security and limits

Only allowlisted, validated tools execute; there is no arbitrary Python, shell, filesystem, generated SQL or unrestricted network tool. Passwords use salted PBKDF2 and bearer tokens persist only as hashes; owner-scoped retrieval/conversations remain intact. No hidden reasoning, credentials, prompts or raw document contents are logged. Phase 7 SSE is transport-level chunk delivery, not provider-native token generation.

There is no cloud deployment, SSO/MFA or native TLS termination. Redis fixed-window limiting is shared across replicas but needs a provisioned backend; add edge/IP abuse controls for public authentication. Session cleanup is an operator-scheduled command, not a background startup task. See [ARCHITECTURE.md](ARCHITECTURE.md), [PROGRESS.md](PROGRESS.md) and [DEPLOYMENT.md](DEPLOYMENT.md).
