# AgentForge

Full-stack document intelligence application: PostgreSQL/pgvector RAG, bounded registered-tool orchestration, persistent per-user conversations, authenticated resource ownership, and (Phase 7) provider reliability, authenticated SSE streaming, observability, and a deterministic evaluation suite.

## Phase status

| Group | Count | Phase | Status |
|---|---:|---|---|
| Complete | 1 | Phase 0 — Blueprint | Complete |
| Complete | 2 | Phase 1 — Application foundation | Complete |
| Complete | 3 | Phase 2 — PostgreSQL + pgvector | Implemented and verified |
| Complete | 4 | Phase 3 — Ingestion + grounded RAG | Implemented and verified |
| Complete | 5 | Phase 4 — Agent workflow and safe tools | Implemented and CI-verified |
| Complete | 6 | Phase 5 — Persistent conversations and bounded memory | Implemented and CI-verified |
| Complete | 7 | Phase 6 — Authentication and ownership foundation | Implemented and CI-verified |
| Complete | 8 | Phase 7 — Reliability, streaming, evaluation | Implemented; CI on PR branch |
| Deferred | 9 | SSO/MFA, cloud production deployment, distributed rate limiting | Not implemented |

## Implemented capabilities

| Group | Count | Capability |
|---|---:|---|
| Backend | 1 | FastAPI health, document, RAG chat, auth, agent, conversation, and streaming APIs |
| Data | 2 | PostgreSQL + pgvector, SQLAlchemy 2.x, Alembic |
| Ingestion | 3 | PDF/TXT/Markdown extraction, chunking, embeddings, transactional persistence |
| Retrieval/RAG | 4 | Owner-aware cosine retrieval, grounded context, sources, insufficient-evidence behavior |
| Agent | 5 | Typed decisions; document search, calculator, date offset; bounded execution/trace |
| Identity/memory | 6 | PBKDF2 hashes, hashed revocable expiring sessions, owned conversations, bounded context |
| Reliability | 7 | Bounded provider timeouts/retries, normalized errors, config-driven provider selection |
| Streaming | 8 | Authenticated SSE (`/agent/chat/stream`) with typed event contract; incremental frontend rendering |
| Observability | 9 | Request-ID propagation; bounded, sanitized operational metadata |
| Evaluation | 10 | Deterministic version-controlled RAG/tool/agent regression suite (no paid API) |
| Frontend | 11 | Registration/login, owned documents, conversations, streaming agent answer, sources, tools |

## Local setup

Copy `.env.example`, configure development values, then run:

```bash
cp .env.example .env
docker compose up --build
```

Compose waits for PostgreSQL health; the backend applies Alembic before serving. Host-based development requires PostgreSQL + pgvector, backend dependency installation and `alembic upgrade head` before starting FastAPI.

### Evaluation

```bash
cd backend
pip install -r requirements.txt
python ../evaluation/runner/run_evals.py
```

The runner exits non-zero on any failure and requires no paid credentials (fake providers).

## Security boundaries and limitations

Only registered, validated tools execute; there is no arbitrary Python, shell, filesystem, generated SQL or unrestricted network tool. User-owned documents, conversations and retrieval are filtered by authenticated identity. Operational traces and SSE frames exclude chain-of-thought and secrets.

Bearer tokens are held in browser memory; reload requires reauthentication. Rate limiting and request IDs are process-local (single-process); multi-worker deployments require a gateway/shared store. SSO/MFA, HTTPS/reverse-proxy operations, cloud deployment, billing, and analytics remain deferred.
