# AgentForge Engineering Instructions

## Project state

Repository: `Eshablink/agentforge`.

**Verified implementation:** Phases 0–3 are complete. The Phase 4–6 implementation and release-readiness audit are on `main`. GitHub Actions run [37129401744](https://github.com/Eshablink/agentforge/actions/runs/37129401744) passed backend and frontend jobs on audit-hardened application commit `445eb36f512e33160df5916e45e1a8f80306903a`; the latest full run [37130269888](https://github.com/Eshablink/agentforge/actions/runs/37130269888) passed backend and frontend on commit `3ddffd055739611e405c206b17d7931d2bb93374`. PR #6 is merged into `main` and Phases 4–6 are implemented and verified. Verification is commit-specific; rerun CI after later application changes.

Implemented in Phases 4–6: bounded agent orchestration; structured decisions; allowlisted document-search, calculator, and date tools; PostgreSQL conversations with bounded context; PBKDF2 password hashes; hashed bearer sessions with expiry/revocation; owned documents and conversations; owner-filtered pgvector retrieval; and React auth/conversation/agent UI.

This is a production-oriented foundation, not a deployed service. Browser tokens are memory-only, so reload requires sign-in. Legacy Phase 3 endpoints are retained for unowned records. SSO/MFA, rate limiting, cloud deployment, billing, monitoring, and Phase 7+ remain deferred.

## Engineering method

Inspect current code, tests, migrations, workflows, and docs before editing. Preserve working behavior and interfaces except as required by scope. Make focused changes, add regression tests, run relevant checks, and review the diff. Do not restart completed phases, add unrelated features, or claim verification without actual results.

## Architecture and data boundaries

Keep UI, API, auth/authorization, conversation services, agent orchestration, providers, tools, retrieval, and persistence separate. Use PostgreSQL + pgvector for integration tests; never substitute SQLite. Reuse existing retrieval and keep Alembic deterministic/model registration acyclic.

Treat user/model input as untrusted. Only registered, typed, validated tools may execute. No generated code, arbitrary SQL, shell, filesystem, or unrestricted network execution. Never expose hidden reasoning. Bound requests, context, tool output, and trace size. Enforce ownership for user-specific resources.

## Security and testing

Never store plaintext passwords or raw bearer tokens. Enforce expiry and revocation. Production requires explicit CORS origins and credentials for selected external providers. Keep secrets out of Git/logs; `.env.example` uses placeholders.

Tests use fake providers and PostgreSQL + pgvector. Maintain cross-user isolation and test cleanup for committed rows. For relevant changes, run Alembic, import smoke test, full backend pytest, and frontend production build.

Keep README, PROJECT_BRIEF, ARCHITECTURE, DECISIONS, and PROGRESS synchronized. Distinguish verified code from deployed production. Do not begin another phase without explicit authorization.
