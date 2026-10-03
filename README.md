# AgentForge

Full-stack document intelligence application: PostgreSQL/pgvector RAG, bounded registered-tool orchestration, persisted per-user conversations, and authenticated resource ownership.

## Phase status

| Group | Count | Phase | Status |
|---|---:|---|---|
| Complete | 1 | Phase 0 — Blueprint | Complete |
| Complete | 2 | Phase 1 — Application foundation | Complete |
| Complete | 3 | Phase 2 — PostgreSQL + pgvector | Implemented and verified |
| Complete | 4 | Phase 3 — Ingestion + grounded RAG | Implemented and verified |
| Complete | 5 | Phase 4 — Agent workflow and safe tools | Implemented and CI-verified on PR branch |
| Complete | 6 | Phase 5 — Persistent conversations and bounded memory | Implemented and CI-verified on PR branch |
| Complete | 7 | Phase 6 — Authentication and ownership foundation | Implemented and CI-verified on PR branch |
| Deferred | 8 | SSO/MFA, rate limiting, billing, cloud production deployment, later phases | Not implemented |

### Verification evidence

- Implementation audit commit `445eb36f512e33160df5916e45e1a8f80306903a`: GitHub Actions run [37129401744](https://github.com/Eshablink/agentforge/actions/runs/37129401744) passed backend and frontend jobs.
- Documentation follow-up commits passed runs [37129523143](https://github.com/Eshablink/agentforge/actions/runs/37129523143), [37129536765](https://github.com/Eshablink/agentforge/actions/runs/37129536765), and [371296?](https://github.com/Eshablink/agentforge/actions).
- Latest audit regression/hardening run should be checked on the PR before merge; only call the exact current head green when its own GitHub checks pass.

CI provisions PostgreSQL + pgvector; applies Alembic; imports the application; runs full backend pytest; and runs `npm run build` (TypeScript and Vite). Fake providers avoid paid API credentials.

## Core capabilities

| Group | Count | Capability |
|---|---:|---|
| Backend | 1 | FastAPI health, documents, RAG chat, auth, agent and conversation APIs |
| Data | 2 | PostgreSQL + pgvector, SQLAlchemy 2.x, Alembic |
| Ingestion | 3 | PDF/TXT/Markdown extraction, deterministic chunking, embeddings, transactional persistence |
| RAG | 4 | Owner-aware cosine retrieval, grounded context, source references, insufficient-evidence response |
| Agent | 5 | Typed decisions; registered document search, Decimal calculator, date offset; bounded execution and operational trace |
| Identity/memory | 6 | PBKDF2 passwords, hashed revocable expiring sessions, owner-filtered documents/conversations, bounded recent context |
| Frontend | 7 | Registration/login, owned document upload/listing, conversations, agent responses, citations and tool trace |

## Local setup

```bash
cp .env.example .env
docker compose up --build
```

The Compose database health check gates backend startup; backend runs Alembic migrations before starting Uvicorn. To run locally outside Compose, start PostgreSQL + pgvector, install backend dependencies, migrate, and start FastAPI. Frontend uses React + TypeScript + Vite on port 5173.

## Security boundaries

Only registered validated tools run. There is no arbitrary Python, shell, filesystem, generated SQL or unrestricted network tool. User-owned retrieval/conversation/document routes scope records by authenticated user ID. Legacy Phase 3 routes are restricted to unowned legacy records. No chain-of-thought or secret is stored in traces.

Bearer tokens are stored in browser memory; reload requires reauthentication. This is a production-oriented foundation, not a deployed production system. SSO/MFA, rate limiting, HTTPS/reverse proxy, deployment operations, billing, analytics and Phase 7+ are deferred.
