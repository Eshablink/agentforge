# AgentForge Decisions

Phases 0–7 are complete on `main`. Phase 7 PR #9 merged in `63d7d3f0d417d06b2e57fa63874824de4306450d`; CI run 37320957004 passed. Existing decisions ADR-001–017 (React/Vite, FastAPI, PostgreSQL/pgvector, Alembic, fake providers, typed allowlisted tools, bounded memory, owner isolation, hashed credentials, SSE operational events, deterministic evaluation) remain accepted without redesign.

## ADR-018 — Explicit production dependency configuration

**Decision:** APP_ENV distinguishes development, test and production; production requires explicit PostgreSQL+psycopg credentials and non-development host, HTTPS CORS origins, provider choices and Redis limiter configuration. Remove unused AUTH_SECRET from examples rather than invent new cryptography. **Reason:** avoid silently deploying development credentials or process-local abuse protection. **Limit:** secrets must be injected by the operator; no deployment is performed by CI.

## ADR-019 — Separate schema migration and traffic readiness

**Decision:** image startup does not migrate. Run Alembic once as a migration job before exposing API replicas; local compose gates startup on a one-shot migration. `/health` checks process liveness only; `/ready` checks PostgreSQL and Redis (when selected) without model calls and returns safe 503 on failure. **Reason:** deterministic rollout without concurrent schema changes in every replica.

## ADR-020 — Small shared limiter and auth throttling

**Decision:** Retain Phase 7 local sliding window for dev/test and add atomic Redis fixed-window limiter behind a protocol for production. Redis errors fail closed, not unlimited; auth attempts use hashes of normalized email while AI requests use authenticated IDs. **Reason:** minimal shared per-user protection. **Limit:** edge/IP throttling must be deployed externally for distributed abuse resistance.

## ADR-021 — Resource limits and explicit session maintenance

**Decision:** enforce extraction bytes/pages/text, cap chunk counts before allocation, embed in small batches in one transaction, and provide an operator-triggered bounded expired-session cleanup command. **Reason:** avoid amplification and unbounded retention without background process complexity. Cleanup does not delete active sessions.

## ADR-022 — HTTPS reverse proxy and browser configuration

**Decision:** serve the browser against a configured HTTPS API URL or same-origin proxy; do not hardcode localhost in production bundles. App trusts only explicitly configured proxy IPs; image does not terminate TLS. SSE proxy buffering/caching must be disabled. **Limit:** frontend Dockerfile is for development, not production static serving; see DEPLOYMENT.md.

This is a production-oriented software foundation, not a live deployment. SSO/MFA, cloud provisioning and native provider token streaming remain deferred.
