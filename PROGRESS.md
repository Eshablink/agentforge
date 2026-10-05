# AgentForge Progress

## Current status

Phases 0–6 are implemented. Phases 0–3 are complete and merged. Phases 4–6 implementation and release-readiness hardening are CI-verified on PR #6. This is a production-oriented foundation, not a deployed service. Phase 7+ has not started.

## Roadmap

| Group | Count | Phase | Status |
|---|---:|---|---|
| Complete | 1 | Phase 0 — Repository blueprint | Implemented and verified |
| Complete | 2 | Phase 1 — Application foundation | Implemented and merged |
| Complete | 3 | Phase 2 — PostgreSQL + pgvector | Implemented and verified |
| Complete | 4 | Phase 3 — Document ingestion and RAG | Implemented and verified |
| Complete | 5 | Phase 4 — Agent orchestration and safe registered tools | Implemented and verified by CI |
| Complete | 6 | Phase 5 — Persistent conversations and bounded recent memory | Implemented and verified by CI |
| Complete | 7 | Phase 6 — Authentication and ownership foundation | Implemented and verified by CI |
| Deferred | 8 | SSO/MFA, rate limiting, billing, cloud deployment and Phase 7+ | Not implemented |

## Phase 4–6 implementation

- Typed agent decisions and provider abstraction; deterministic fake provider for CI.
- Registered `document_search` (existing owner-aware pgvector retrieval), Decimal calculator, and date-offset utility; strict arguments and bounded tools/iterations/traces.
- PostgreSQL conversations/messages with per-user ownership and bounded recent context, ordered deterministically.
- PBKDF2-SHA256 password hashes, random bearer tokens persisted only as hashes, expiry and revocation.
- Authenticated document upload/list, conversation CRUD/message and agent routes; vector search filters by authenticated user.
- Preserved Phase 3 endpoints for unowned legacy records only.
- Audit hardening: explicit production CORS/provider/resource checks, safe provider error fallback, structured bounded RAG output with source provenance, deterministic message ordering and frontend conversation refresh.

## Verification record

| Group | Count | Verification | Result |
|---|---:|---|---|
| CI | 1 | Run [37129401744](https://github.com/Eshablink/agentforge/actions/runs/37129401744), application audit commit `445eb36f512e33160df5916e45e1a8f80306903a` | Backend + frontend PASS |
| CI | 2 | Run [37130211450](https://github.com/Eshablink/agentforge/actions/runs/37130211450), audit implementation and progress update | Backend + frontend PASS |
| CI | 3 | Run [37130269888](https://github.com/Eshablink/agentforge/actions/runs/37130269888), consolidated app/docs update | Backend + frontend PASS |

The green workflows provision PostgreSQL + pgvector, run Alembic `upgrade head`, import smoke test, full backend pytest (including PostgreSQL ownership/retrieval tests) and frontend production TypeScript/Vite build. Fake providers require no paid credentials. Current PR-head verification is available in the PR checks; historical runs apply only to their associated commits.

## Release-readiness audit findings

- Authenticated `user_id` flows through agent → tool registry → RAG → retrieval; database query filters by owner. Legacy queries filter to unowned rows only.
- Protected conversation operations scope reads/deletes by owner; document listing/upload use owner-specific routes.
- Passwords use salted PBKDF2-SHA256; bearer credentials are random and only token hashes persist; expiry/revocation are checked.
- Registered typed tools reject unknown names/invalid arguments; no arbitrary code, shell, filesystem, generated SQL or unrestricted network tools. Provider errors are controlled; traces omit secrets and chain-of-thought.
- Memory is limited to recent messages of the selected owned conversation, bounded by count and characters, with deterministic order.
- Production rejects wildcard/empty CORS origins, validates selected-provider credentials, and bounds resource limits.

## Deferred scope

Browser bearer token is memory-only and requires reauthentication after reload. There is no deployed cloud/Kubernetes service, SSO/MFA, formal rate limiting, billing, advanced analytics, or Phase 7+ work. Configure HTTPS/reverse proxy, monitoring and production secret operations before external deployment.
