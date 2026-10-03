# AgentForge Project Brief

## Project summary

AgentForge is a full-stack application for document ingestion, grounded RAG, safe registered-tool orchestration, persistent conversations, and authenticated user-owned resources.

## Phase status

| Group | Count | Phase | Status |
|---|---:|---|---|
| Complete | 1 | Phase 0 — Repository blueprint | Implemented |
| Complete | 2 | Phase 1 — FastAPI and React foundation | Implemented |
| Complete | 3 | Phase 2 — PostgreSQL + pgvector + SQLAlchemy + Alembic | Implemented and verified |
| Complete | 4 | Phase 3 — Ingestion + vector retrieval + grounded RAG | Implemented and verified |
| Complete | 5 | Phase 4 — Safe agent workflow and registered tools | Implemented; latest Actions verification to be recorded after final audit commit |
| Complete | 6 | Phase 5 — Persistent conversations and bounded recent context | Implemented; latest Actions verification to be recorded after final audit commit |
| Complete | 7 | Phase 6 — Authentication and ownership foundation | Implemented; latest Actions verification to be recorded after final audit commit |
| Deferred | 8 | Deployment, SSO/MFA, rate limiting, billing, analytics, Phase 7+ | Not implemented |

## Implemented capabilities

| Group | Count | Capability | Implementation |
|---|---:|---|---|
| Agent | 1 | Structured orchestration | Typed decisions; bounded execution loop and operational trace |
| Agent | 2 | Safe tool registry | Existing retrieval-backed document search, Decimal calculator, date offset; strict schemas and bounded outputs |
| Conversation | 3 | Persistent sessions | PostgreSQL conversations/messages; ownership checks; bounded recent-message context |
| Authentication | 4 | Account/session foundation | PBKDF2-SHA256 password hashes; opaque random bearer tokens stored as hashes; expiry and revocation |
| Ownership | 5 | Private user data | Owned document routes and per-user pgvector filtering; conversation queries scoped to current user |
| UI/CI | 6 | Full-stack flow | Existing UI extended for registration/login, documents, conversations, agent answers, sources and trace |

## Verification policy

Only claim Phases 4–6 verified when the current branch head has a fresh green GitHub Actions run covering PostgreSQL + pgvector, Alembic upgrade, import smoke test, full backend pytest, and frontend production build. A green run proves CI behavior for that commit, not external production deployment.

## Security and known boundaries

No arbitrary code, shell, filesystem, generated SQL, or unrestricted network tools. Model output is validated as data; chain-of-thought is neither stored nor returned. Legacy Phase 3 endpoints remain scoped to unowned legacy documents; new user content uses authenticated owner-scoped routes.

The browser stores the bearer token in memory, so reload requires reauthentication. This is a development/deployment foundation, not a deployed production service. SSO/MFA, rate limiting, multi-tenancy administration, deployment, billing, and analytics remain deferred.
