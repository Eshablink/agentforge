# AgentForge — Engineering Instructions

## Project state

Repository: `Eshablink/agentforge`.

**Verified implementation:** Phases 0–3 are complete. The Phase 4–6 implementation and audit hardening are on `feat/agentforge-phases-4-6`; GitHub Actions run [37129401744](https://github.com/Eshablink/agentforge/actions/runs/37129401744) passed backend and frontend jobs on commit `445eb36f512e33160df5916e45e1a8f80306903a`. The latest audited state on that commit has successful checks; later documentation-only commits also passed Actions. Verify every application change with a new run. PR #6 is open and must not be merged without explicit authorization.

Implemented in this milestone: bounded agent orchestration; structured decisions; allowlisted document-search, calculator and date tools; PostgreSQL conversations with bounded context; PBKDF2 password hashes; random bearer credentials stored as hashes with expiry/revocation; owner-scoped documents, conversations and vector retrieval; React auth/conversation/agent UI; PostgreSQL migration and CI.

This is a production-oriented foundation, not a deployed production system. Tokens are memory-only in the browser and require re-login after reload. Legacy Phase 3 endpoints support unowned legacy documents. SSO/MFA, rate limiting, cloud deployment, billing, monitoring and Phase 7+ are deferred.

## Engineering method

Inspect current code, tests, migrations, workflows and docs before changes. Preserve working behavior and interfaces except where scoped work requires a change. Make focused changes, add regression tests, run checks, review the diff and document only verified behavior. Do not restart completed phases, make unrelated changes, or infer success without actual results.

## Architecture and data boundaries

Keep UI, API, auth/authorization, conversation services, agent orchestration, providers, tools, retrieval and persistence separated. Use PostgreSQL + pgvector for integration tests, never SQLite. Reuse existing retrieval and keep Alembic deterministic/model registration acyclic.

Treat user/model input as untrusted. Only registered, typed, validated tools may execute. No generated code, arbitrary SQL, shell, filesystem or unrestricted network execution. Never expose hidden reasoning. Bound requests, context, tool output and trace size. Enforce ownership for user-specific resources.

## Security and testing

Never store plaintext passwords or raw bearer tokens. Enforce session expiry/revocation. Production requires explicit CORS origins and selected-provider credentials. Keep secrets out of Git and logs; `.env.example` values are placeholders.

Automated tests use deterministic fake providers and PostgreSQL + pgvector. Maintain cross-user isolation checks and test isolation for committed data. For relevant changes, run migration, import smoke test, full backend pytest and production frontend build.

Keep README, PROJECT_BRIEF, ARCHITECTURE, DECISIONS and PROGRESS synchronized. Distinguish a green CI foundation from actual external production deployment. Do not merge PR #6 or start another phase without explicit instruction.
