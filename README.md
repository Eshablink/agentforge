# AgentForge

Full-stack document question-answering application with PostgreSQL + pgvector retrieval and grounded answers with source references. Phases 0–3 are complete and merged. Agentic workflows and tool calling are not implemented.

## Current Status

| Group | Count | Phase / capability | Status |
|---|---:|---|---|
| Complete | 1 | Phase 0 — Repository setup and blueprint | Complete |
| Complete | 2 | Phase 1 — Application foundation | Complete |
| Complete | 3 | Phase 2 — PostgreSQL + pgvector | Complete; CI-verified |
| Complete | 4 | Phase 3 — Document ingestion + RAG foundation | Complete; CI-verified |
| Deferred | 5 | Agents and tool calling | Not started |
| Deferred | 6 | Authentication, conversation memory, multi-tenancy, billing, production deployment | Not implemented |

### Post-merge CI evidence

- Phase 0–3 merge commit `67e983772257dc575475e86ebecbe6548c968eb9`: GitHub Actions run [37117875205](https://github.com/Eshablink/agentforge/actions/runs/37117875205) passed.
- Documentation cleanup merge commit `cded4a9bf39d267200f1de072600d1648b19182f`: run [37119471555](https://github.com/Eshablink/agentforge/actions/runs/37119471555) passed.
- Each run covered PostgreSQL + pgvector, Alembic migration, application import, backend pytest and frontend production build. These verify the corresponding commits only; run fresh CI for subsequent code changes.

## Implemented Capabilities

| Group | Count | Capability |
|---|---:|---|
| Backend | 1 | FastAPI `/health`, `/documents`, and `/chat` APIs |
| Database | 2 | SQLAlchemy 2.x, PostgreSQL + pgvector, Alembic migration |
| Ingestion | 3 | PDF/TXT/Markdown extraction, validation, deterministic chunking, embedding abstraction, transactional persistence |
| Retrieval/RAG | 4 | pgvector cosine similarity, bounded `top_k`, grounded context/answers, source references |
| Frontend | 5 | React + TypeScript + Vite upload/list/query/source display |
| Development/CI | 6 | Docker Compose; PostgreSQL-backed migration, pytest, import and frontend build checks |

Automated tests use fake embedding and LLM providers and require no paid API credentials.

## Local Setup

```bash
cp .env.example .env
```

For the full stack, including PostgreSQL readiness and backend migration-before-API startup:

```bash
docker compose up --build
```

For host-based development, start PostgreSQL with pgvector first, then run the backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
alembic -c alembic.ini upgrade head
uvicorn app.main:app --reload
```

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

## APIs

| Group | Count | Endpoint | Purpose |
|---|---:|---|---|
| Health | 1 | `GET /health` | Health response |
| Documents | 2 | `POST /documents` | Upload, extract, chunk, embed and persist |
| Documents | 3 | `GET /documents` | List documents and chunk counts |
| RAG | 4 | `POST /chat` | Retrieve context and return grounded answer with sources |

## Verification

With PostgreSQL + pgvector running and `DATABASE_URL` configured:

```bash
cd backend
alembic -c alembic.ini upgrade head
python -c "from app.main import app; print(app.title)"
pytest
cd ../frontend
npm run build
```

## Scope Boundary

No agent orchestration, tool-calling runtime, authentication/authorization, conversation memory, multi-tenancy, analytics tools, billing or production deployment has been implemented. Phase 4 has not started.
