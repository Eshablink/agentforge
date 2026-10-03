# AgentForge Project Brief

## Product summary

AgentForge is a full-stack application for document ingestion, grounded RAG, safe registered-tool orchestration, persistent conversations and authenticated user-owned resources.

## Phase status

| Group | Count | Phase | Status |
|---|---:|---|---|
| Complete | 1 | Phase 0 — Repository blueprint | Implemented and verified |
| Complete | 2 | Phase 1 — FastAPI and React foundation | Implemented and verified |
| Complete | 3 | Phase 2 — PostgreSQL + pgvector + SQLAlchemy + Alembic | Implemented and verified |
| Complete | 4 | Phase 3 — Document ingestion, retrieval and grounded RAG | Implemented and verified |
| Complete | 5 | Phase 4 — Agent orchestration and safe registered tools | Implemented and verified by GitHub Actions |
| Complete | 6 | Phase 5 — Persistent conversations and bounded memory | Implemented and verified by GitHub Actions |
| Complete | 7 | Phase 6 — Authentication and ownership foundation | Implemented and verified by GitHub Actions |
| Deferred | 8 | SSO/MFA, rate limiting, deployed cloud operations, billing, analytics and Phase 7+ | Not implemented |

## Implemented capabilities

| Group | Count | Capability | Implementation |
|---|---:|---|
| Agent | 1 | Structured orchestration | Typed decisions; bounded execution loop and operational trace |
| Agent | 2 | Safe tool registry | Existing retrieval-backed document search, Decimal calculator, date offset; strict schemas and bounded outputs |
| Conversation | 3 | Persistent sessions | PostgreSQL conversations/messages; ownership checks; bounded recent-message context |
| Authentication | 4 | Account/session foundation | PBKDF2-SHA256 password hashes; opaque random bearer tokens stored as hashes; expiry and revocation |
| Ownership | 5 | Private user data | Owned document routes and per-user pgvector filtering; conversation queries scoped to current user |
| UI/CI | 6 | Full-stack flow | Registration/login, owned documents, conversations, agent answers/sources/tool trace |

## Verification record

GitHub Actions run [37129401744](https://github.com/Eshablink/agentforge/actions/runs/37129401744) passed backend and frontend checks on audit-hardened application commit `445eb36f512e33160df5916e45e1a8f80306903a`. Documentation follow-up runs [37129523143](https://github.com/Eshablink/agentforge/actions/runs/37129523143), [37129536765](https://github.com/Eshablink/agentforge/actions/runs/37129536765), and consolidated run [37130269888](https://github.com/Eshablink/agentforge/actions/runs/37130269888) passed the application and documentation checks then present. Later audit-only commits are being checked by fresh runs; verify the current PR-head checks before merge.

CI uses PostgreSQL + pgvector, Alembic, import smoke test, complete backend pytest, and frontend TypeScript/Vite production build. Fake providers avoid paid API credentials.

## Security boundaries and limitations

Only registered tools execute. No arbitrary Python, shell, filesystem, generated SQL or unrestricted network tool. Model output is validated; chain-of-thought is neither stored nor returned. User-owned documents and conversations are isolated by authenticated user ID. Legacy Phase 3 routes are preserved for unowned records only.

Browser bearer tokens are memory-only, so reload requires sign-in. This is a production-oriented foundation, not a deployed production service. SSO/MFA, rate limiting, cloud deployment, billing, analytics and Phase 7+ remain deferred.
