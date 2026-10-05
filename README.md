# AgentForge

Full-stack document intelligence application: PostgreSQL/pgvector RAG, bounded registered-tool orchestration, persistent per-user conversations, and authenticated resource ownership.

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

- Phase 4–6 audit-hardened implementation commit `445eb36f512e33160df5916e45e1a8f80306903a`: GitHub Actions run [37129401744](https://github.com/Eshablink/agentforge/actions/runs/37129401744) passed backend and frontend jobs.
- Documentation follow-up runs [37129523143](https://github.com/Eshablink/agentforge/actions/runs/37129523143), [37129536765](https://github.com/Eshablink/agentforge/actions/runs/37129536765), and [37130269888](https://github.com/Eshablink/agentforge/actions/runs/37130269888) passed.
- Latest documented implementation/docs head `3ddffd055739611e405c206b17d7931d2bb93374` passed in run [37130269888](https://github.com/Eshablink/agentforge/actions/runs/37130269888). Later audit-only documentation commits still require their own CI result before claiming those exact commits verified.

CI provisions PostgreSQL + pgvector, applies Alembic, imports the application, runs full backend pytest and builds the frontend with TypeScript and Vite. Fake providers avoid paid API credentials.

## Implemented capabilities

| Group | Count | Capability |
|---|---:|---|
| Backend | 1 | FastAPI health, document, RAG chat, auth, agent and conversation APIs |
| Data | 2 | PostgreSQL + pgvector, SQLAlchemy 2.x, Alembic |
| Ingestion | 3 | PDF/TXT/Markdown extraction, deterministic chunking, embeddings and transactional persistence |
| Retrieval/RAG | 4 | Owner-aware cosine retrieval, grounded context, sources and insufficient-evidence behavior |
| Agent | 5 | Typed decisions; registered document search, Decimal calculator and date offset; bounded execution/trace |
| Identity/memory | 6 | PBKDF2 password hashes, hashed revocable expiring bearer sessions, owned conversations, bounded recent context |
| Frontend | 7 | Registration/login, owned documents, conversations, agent answer, sources, tools and trace |

## Local setup

Copy `.env.example`, configure development values, then run:

```bash
cp .env.example .env
docker compose up --build
```

Compose waits for PostgreSQL health; the backend applies Alembic before serving. Host-based development requires PostgreSQL + pgvector, backend dependency installation and `alembic upgrade head` before starting FastAPI. The React/TypeScript/Vite frontend defaults to port 5173.

## Security boundaries and limitations

Only registered, validated tools execute; there is no arbitrary Python, shell, filesystem, generated SQL or unrestricted network tool. User-owned documents, conversations and retrieval are filtered by authenticated identity. Legacy Phase 3 routes are restricted to unowned records. Operational traces exclude chain-of-thought and secrets.

Bearer tokens are held in browser memory; reload requires reauthentication. This is a production-oriented foundation, not a deployed production service. SSO/MFA, rate limiting, HTTPS/reverse-proxy operations, cloud deployment, billing, analytics, and later phases are deferred.
