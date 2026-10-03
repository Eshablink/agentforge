# AgentForge — Engineering Instructions

## Project state

Repository: `Eshablink/agentforge`.

**Verified phases:** Phases 0–3 are complete. Phase 4–6 code is implemented on `feat/agentforge-phases-4-6`; Actions run [37128835442](https://github.com/Eshablink/agentforge/actions/runs/37128835442) passed both backend and frontend jobs on commit `5544bdd1b9c168ac627c67a2af610f65a3e4287d`. Re-run all checks after any subsequent application-code changes. PR #6 remains open and must not be merged without explicit authorization.

The branch adds bounded agent orchestration; typed structured provider decisions; registered document-search, calculator, and date tools; PostgreSQL conversations with bounded recent context; PBKDF2 password hashing; hashed expiring/revocable bearer sessions; per-user document/conversation ownership; owner-scoped pgvector retrieval; and React authentication/conversation/agent UI.

This is a production-oriented foundation, not a deployed production service. The browser holds bearer tokens in memory (reload requires sign-in); legacy Phase 3 endpoints are retained for unowned documents. SSO/MFA, rate limiting, cloud deployment, Kubernetes, billing, and Phase 7+ work remain deferred.

## Engineering method

Inspect current branch, code, tests, migrations, workflows, and docs before changing anything. Preserve existing behavior and interfaces unless the scoped task requires otherwise. Make focused changes, add regression tests, run relevant checks, and inspect the final diff. Do not restart completed phases, introduce unrelated features, or claim verification without actual results.

## Architecture and data boundaries

Keep frontend, API, authentication/authorization, conversation services, agent orchestration, providers, tools, retrieval, and persistence separate. PostgreSQL + pgvector is required for DB integration tests; do not substitute SQLite. Reuse the existing retrieval service for document search. Keep Alembic deterministic and model registration acyclic.

Treat user and model data as untrusted. Only registered typed tools may execute; reject unknown tools and invalid arguments. Never execute generated code, unrestricted SQL, shell, arbitrary filesystem operations, or unrestricted network requests. Do not expose chain-of-thought. Bound requests, tool output, traces, agent steps, and memory context. Enforce ownership on every user-specific read/write path.

## Security and configuration

Never store plaintext passwords. Store only hashes of random bearer tokens and enforce expiry/revocation. Production settings require explicit CORS origins and credentials when a paid provider is selected. Never commit secrets; use environment variables and safe `.env.example` placeholders.

## Testing and delivery

Tests must be deterministic and must not require paid APIs. Preserve PostgreSQL + pgvector integration and cross-user isolation coverage. For affected changes, run Alembic, import smoke test, full backend pytest, and frontend production build. CI is the source for current verification. Do not merge PR #6 or begin another phase without explicit direction.

Keep README, PROJECT_BRIEF, ARCHITECTURE, DECISIONS, and PROGRESS synchronized. Distinguish verified foundation from deployed production readiness.
