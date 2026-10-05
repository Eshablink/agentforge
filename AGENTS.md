# AgentForge Engineering Instructions

## Project state

Repository: `Eshablink/agentforge`.

**Verified implementation:** Phases 0–6 are complete and merged to `main`. Phase 7 (production AI reliability, streaming, evaluation) is implemented on `feat/agentforge-phase-7`; confirm current GitHub Actions checks before merge. This is a production-oriented foundation, not a deployed service.

Implemented in Phases 4–6: bounded agent orchestration; structured decisions; allowlisted document-search, calculator, and date tools; PostgreSQL conversations with bounded context; PBKDF2 password hashes; hashed bearer sessions with expiry/revocation; owned documents and conversations; owner-filtered pgvector retrieval; React auth/conversation/agent UI.

Phase 7 adds provider timeouts/retries and normalized errors, authenticated SSE streaming (typed event contract), request-ID and safe operational telemetry, per-user process-local rate limiting, resource bounds, deterministic version-controlled evaluations, CI integration, and docs. `/agent/chat` remains backward compatible.

## Engineering method

Inspect current code, tests, migrations, workflows, and docs before editing. Preserve working behavior and interfaces except as required by scope. Make focused changes, add regression tests, run relevant checks, and review the diff. Do not restart completed phases or claim verification without actual results.

## Architecture and data boundaries

Keep UI, API, auth/authorization, conversation services, agent orchestration, providers, tools, retrieval, and persistence separate. Use PostgreSQL + pgvector for integration tests; never substitute SQLite. Reuse existing retrieval and keep Alembic deterministic/model registration acyclic.

Treat user/model input as untrusted. Only registered, typed, validated tools may execute. No generated code, arbitrary SQL, shell, filesystem, or unrestricted network execution. Never expose hidden reasoning. Bound requests, context, tool output, stream output/duration, and trace size. Enforce ownership for user-specific resources.

## Security and testing

Never store plaintext passwords or raw bearer tokens. Enforce expiry and revocation. Production requires explicit CORS origins and credentials for selected external providers. Keep secrets out of Git/logs; `.env.example` uses placeholders only.

Tests use fake providers and PostgreSQL + pgvector. Maintain cross-user isolation and test cleanup for committed rows. For relevant changes, run Alembic, import smoke test, full backend pytest, frontend production build, and evaluation runner.

## Operational limitations

The rate limiter and request-ID context are process-local and not shared across replicas. Use a gateway/shared store for multi-worker/replica deployments. Streaming persists the complete exchange only after successful stream completion; client disconnects do not preserve partial assistant output.

Keep README, PROJECT_BRIEF, ARCHITECTURE, DECISIONS, and PROGRESS synchronized. Distinguish verified code from deployed production.
