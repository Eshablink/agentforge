# AgentForge Project Brief

## Project summary

AgentForge is a full-stack application for document ingestion, grounded RAG, safe registered-tool orchestration, persistent conversations and authenticated user-owned resources.

## Phase status

| Group | Count | Phase | Status |
|---|---:|---|---|
| Complete | 1 | Phase 0 — Repository blueprint | Implemented |
| Complete | 2 | Phase 1 — FastAPI and React foundation | Implemented |
| Complete | 3 | Phase 2 — PostgreSQL + pgvector + SQLAlchemy + Alembic | Implemented and verified |
| Complete | 4 | Phase 3 — Ingestion + vector retrieval + grounded RAG | Implemented and verified |
| Complete | 5 | Phase 4 — Safe agent workflow and registered tools | Implemented; CI-verified on PR branch |
| Complete | 6 | Phase 5 — Persistent conversations and bounded recent context | Implemented; CI-verified on PR branch |
| Complete | 7 | Phase 6 — Authentication and ownership foundation | Implemented; CI-verified on PR branch |
| Deferred | 8 | Deployment, SSO/MFA, rate limiting, billing, analytics and Phase 7+ | Not implemented |

## Implemented capabilities

| Group | Count | Capability | Implementation |
|---|---:|---|---|
| Agent | 1 | Structured orchestration | Typed decisions; bounded execution loop and operational trace |
| Agent | 2 | Safe tool registry | Existing retrieval-backed document search, Decimal calculator, date offset; strict schemas and bounded outputs |
| Conversation | 3 | Persistent sessions | PostgreSQL conversations/messages; ownership checks; bounded recent-message context |
| Authentication | 4 | Account/session foundation | PBKDF2-SHA256 password hashes; opaque random bearer tokens stored as hashes; expiry and revocation |
| Ownership | 5 | Private user data | Owned document routes and per-user pgvector filtering; conversation queries scoped to current user |
| UI/CI | 6 | Full-stack flow | Registration/login, owned documents, conversations, agent answers/sources/tool trace |

## Verification

GitHub Actions run [37129401744](https://github.com/Eshablink/agentforge/actions/runs/37129401744) passed backend and frontend checks on audit-hardened implementation commit `445eb36f512e33160df5916e45e1a8f80306903a`. Subsequent documentation commits passed CI in runs [37129523143](https://github.com/Eshablink/agentforge/actions/runs/37129523143) and [37129536765](https://github.com/Eshablink/agentforge/actions/runs/37129536765). Latest cleanup/audit commit `90d02d03c54b15e3ad571e93b5a817a9fa5b83d9` still requires its own fresh run before making a claim about that exact commit.

CI provisions PostgreSQL + pgvector, runs Alembic upgrade and app import smoke test, the complete pytest suite, and the TypeScript/Vite production build. Tests require no paid provider keys.

## Security boundaries and limitations

Only registered tools can execute. There is no arbitrary Python, shell, filesystem, generated SQL or unrestricted network tool. Model output is validated; chain-of-thought is not stored or returned. User-owned documents and conversations are isolated by authenticated identity. Legacy Phase 3 APIs remain for unowned legacy records only.

The browser keeps bearer tokens in memory, so reload requires sign-in. This is a production-oriented foundation, not a deployed production system. SSO/MFA, rate limiting, cloud deployment, billing, analytics, and later phases remain deferred.
