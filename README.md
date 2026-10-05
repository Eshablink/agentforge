# AgentForge

Full-stack document intelligence application: PostgreSQL/pgvector RAG, bounded registered-tool orchestration, persistent per-user conversations, authenticated resource ownership, and (Phase 7) provider reliability, authenticated SSE delivery, safe observability, and deterministic regression evaluation.

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
| Complete | 8 | Phase 7 — Reliability, SSE delivery, deterministic regression suite | Implemented; see current PR checks |
| Deferred | 9 | SSO/MFA, cloud production deployment, distributed rate limiting | Not implemented |

## Implemented capabilities

| Group | Count | Capability |
|---|---:|---|
| Backend | 1 | FastAPI health, document, RAG chat, auth, agent, conversation, and SSE APIs |
| Data | 2 | PostgreSQL + pgvector, SQLAlchemy 2.x, Alembic |
| Ingestion | 3 | PDF/TXT/Markdown extraction, chunking, embeddings, transactional persistence |
| Retrieval/RAG | 4 | Owner-aware cosine retrieval, grounded context, sources, insufficient-evidence behavior |
| Agent | 5 | Typed decisions; document search, calculator, date offset; bounded execution/trace |
| Identity/memory | 6 | PBKDF2 hashes, hashed revocable expiring sessions, owned conversations, bounded context |
| Reliability | 7 | Per-attempt provider timeout, bounded retries, normalized errors, config-driven selection |
| Streaming | 8 | Authenticated SSE with typed events; bounded generated answer chunks delivered incrementally to the frontend |
| Observability | 9 | Single canonical request ID across header, SSE start event and telemetry |
| Evaluation | 10 | Deterministic version-controlled RAG/tool/agent regression suite; no paid API calls |
| Frontend | 11 | Registration/login, owned documents, conversations, SSE answer chunks, sources and tool activity |

## Streaming semantics

`POST /agent/chat/stream` sends one `message_start`, followed by safe operational events and bounded answer chunks. The provider currently returns structured decisions/final answer text; the service chunks that generated text for SSE delivery. This is **incremental SSE delivery**, not provider-native token streaming. The existing `/agent/chat` endpoint remains unchanged.

## Local setup

```bash
cp .env.example .env
docker compose up --build
```

Compose waits for PostgreSQL health; the backend applies Alembic before serving. Host-based development requires PostgreSQL + pgvector, backend dependencies, and `alembic upgrade head` before starting FastAPI.

### Deterministic evaluation

```bash
cd backend
pip install -r requirements.txt
python ../evaluation/runner/run_evals.py
```

This regression suite checks retrieval/source presence, grounding-related behavior, tool selection and invalid-tool rejection, bounded agent execution, and safe provider failures. It is not a general LLM quality benchmark. It exits non-zero on failure and requires no paid credentials.

## Security and limitations

Only registered, validated tools execute; no arbitrary Python, shell, filesystem, generated SQL, or unrestricted network tool. User-owned documents, conversations, and retrieval remain identity-filtered. Operational traces and SSE frames exclude chain-of-thought and secrets.

Bearer tokens are held in browser memory; reload requires reauthentication. Rate limiting and request-ID context are process-local; multi-worker deployments require a gateway/shared store. Provider timeout is per attempt, so retries can extend total operation duration. SSO/MFA, HTTPS/reverse-proxy operations, cloud deployment, billing, and analytics remain deferred.
