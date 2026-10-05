# AgentForge Progress

**Verified main baseline:** Phases 0–7 complete. Phase 7 PR #9 merged at `63d7d3f0d417d06b2e57fa63874824de4306450d`; GitHub Actions main run 37320957004 succeeded (PostgreSQL + pgvector, Alembic, import smoke, full pytest including deterministic evaluation, frontend build). Phase 8 is implemented on `feat/agentforge-phase-8` and requires final PR-head green CI before it may be called ready. No Phase 8 production environment has been deployed.

## Phase 8 implementation

- Production configuration: distinct development/test/production selection; explicit managed PostgreSQL URL, HTTPS CORS origins, provider choice and Redis limiter in production; reject default DB credentials, SQLite and unsafe resource ceilings. Removed unused `AUTH_SECRET` from examples.
- Deployment: non-root API image does not run migrations. Local compose has a one-shot migration service gated on DB health; production runbook mandates one migration job and traffic gating. `/health` stays cheap; `/ready` checks DB and shared limiter using safe status-only responses.
- Rate/auth: protocol-based local sliding-window and atomic Redis fixed-window shared implementations; production fails closed on Redis failure. Hashed normalized email throttles registration/login, with edge/IP protections deferred to deployment. Sessions can be cleaned in batches through explicit command without affecting active sessions.
- Pressure/UX: PDF page/extracted-text and document chunk ceilings; bounded embedding batches in a transaction; frontend uses configured HTTPS or same-origin API base including SSE rather than a localhost production URL. Request-ID telemetry and typed SSE remain unchanged.
- Security and compatibility: Phase 0–7 routes remain; owner-filtered retrieval/conversations and safe tool boundaries preserved. Production is not a claim of deployment; see DEPLOYMENT.md for requirements.

## Verification

Use the latest Phase 8 PR-head GitHub Actions result, not an earlier Phase 7 run, to verify this branch. Existing CI provisions PostgreSQL + pgvector, upgrades Alembic, imports the application, runs complete backend pytest (which invokes the deterministic evaluation runner) and builds the frontend. New tests cover production config, shared/local limiters, readiness failure, ingestion pressure, auth throttling and session cleanup. No paid API calls occur in CI.

## Limitations

Redis limiting is an atomic fixed window rather than a strict sliding window; shared Redis must be provisioned externally. Auth throttling by hashed email is not a substitute for proxy-level IP and bot protection. There is no SSO/MFA or cloud automation; the frontend dev Docker image is not a production static server. SSE still delivers bounded chunks of generated text rather than provider-native tokens. The application does not terminate TLS; use a trusted HTTPS reverse proxy.
