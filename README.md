# AgentForge README

Full-stack document question answering with PostgreSQL + pgvector retrieval and grounded responses with source references.

## Project status

| Group | Count | Phase | Status |
|---|---:|---|---|
| Completed | 1 | Phase 0 — Repository setup and blueprint | Complete |
| Completed | 2 | Phase 1 — Application foundation | Complete; merged into `main` |
| Completed | 3 | Phase 2 — PostgreSQL + pgvector foundation | Implemented and CI-verified |
| Completed | 4 | Phase 3 — Document ingestion and RAG foundation | Implemented and CI-verified |
| Planned | 5 | Phase 4 — Agentic workflows and tool calling | Not started |
| Deferred | 6 | Authentication, complex conversation history, multi-tenancy, billing, production deployment | Not implemented |

Phase 2–3 GitHub Actions verification passed on PR #3: run 37117613154 (PR) and 37117610042 (push), commit `7f77050e739047bc19d955cdc2498054c228b7d4`. Follow-up documentation commit `9099462e914c40d843f6080f96efd016802bdd80` also had successful PR/push CI. Subsequent code changes must be verified by fresh checks.

## Implemented capabilities

| Group | Count | Capability |
|---|---:|---|
| Backend | 1 | FastAPI health, document upload/list, and chat APIs |
| Database | 2 | SQLAlchemy 2.x, PostgreSQL + pgvector, Alembic migrations |
| Ingestion | 3 | PDF/TXT/Markdown extraction, upload validation, deterministic chunking, embeddings, transactional persistence |
| Retrieval/RAG | 4 | pgvector cosine similarity, bounded `top_k`, grounded context/answers, source references |
| Frontend | 5 | React + TypeScript + Vite upload/list/query/source display vertical slice |
| Development/CI | 6 | Docker Compose with PostgreSQL/pgvector; CI migration, import smoke test, pytest, and frontend build |

Automated tests use fake embedding and LLM providers and PostgreSQL + pgvector; no paid external API is needed.

## Local setup

Copy `.env.example` to `.env` and adjust values as needed:

```bash
cp .env.example .env
```

Run the full development stack (database becomes healthy before backend migration/startup):

```bash
docker compose up --build
```

Frontend: `http://localhost:5173`  
Backend: `http://localhost:8000`

For host-based backend development, start PostgreSQL with pgvector first, install dependencies, then migrate and start the API:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
alembic -c alembic.ini upgrade head
uvicorn app.main:app --reload
```

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

## API overview

| Group | Count | Endpoint | Purpose |
|---|---:|---|---|
| Health | 1 | `GET /health` | API health response |
| Documents | 2 | `POST /documents` | Upload, extract, chunk, embed, persist |
| Documents | 3 | `GET /documents` | List documents and chunk counts |
| RAG | 4 | `POST /chat` | Retrieve context and return grounded answer with sources |

Example request:

```json
{
  "question": "What does the document say about refunds?",
  "top_k": 5
}
```

## Verification commands

CI uses PostgreSQL + pgvector and runs Alembic before the backend import and full pytest suite. Locally, with a reachable PostgreSQL + pgvector database:

```bash
cd backend
alembic -c alembic.ini upgrade head
python -c "from app.main import app; print(app.title)"
pytest

cd ../frontend
npm install
npm run build
```

## Scope boundary

Phase 4 (agents and tool calling) has not started. Authentication/authorization, multi-tenancy, complex memory, analytics tools, and production deployment are also not implemented.
