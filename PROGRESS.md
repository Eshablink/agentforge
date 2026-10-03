# AgentForge Progress

## Current Phase

Phase 2 + Phase 3 — PostgreSQL/pgvector, Document Ingestion, and RAG Foundation

Status: COMPLETE — verified by GitHub Actions on commit `7f77050e739047bc19d955cdc2498054c228b7d4`.

## Development Roadmap

### Phase 0 — Repository Blueprint
Status: COMPLETE

### Phase 1 — Application Foundation
Status: COMPLETE

- FastAPI backend
- React + TypeScript + Vite frontend
- health endpoint and foundation tests
- merged into `main`

### Phase 2 — PostgreSQL + pgvector
Status: COMPLETE

- PostgreSQL and pgvector schema
- SQLAlchemy 2.x models and sessions
- Alembic migration creates the vector extension and tables
- CI migration verified against PostgreSQL + pgvector

### Phase 3 — Document Ingestion + RAG Foundation
Status: COMPLETE

- PDF, TXT, and Markdown ingestion
- deterministic chunking and embedding abstraction
- vector retrieval and grounded answer generation
- traceable source references and minimal frontend vertical slice

### Phase 4 — Agentic Workflows + Tool Calling
Status: PLANNED

## Phase 2 + 3 Verification

Verified by the GitHub Actions workflow for PR #3:

| Group | Count | Check | Result |
|---|---:|---|---|
| PostgreSQL | 1 | PostgreSQL + pgvector service readiness | PASS |
| Database | 2 | Alembic `upgrade head` against CI database | PASS |
| Backend | 3 | `app.main` import smoke test | PASS |
| Backend | 4 | Full backend pytest suite, including PostgreSQL integration tests | PASS |
| Frontend | 5 | Production TypeScript/Vite build | PASS |
| CI | 6 | Workflow run 37117613154 (PR) and 37117610042 (push) | PASS |

The retrieval integration test uses real PostgreSQL/pgvector cosine search. A function-scoped autouse fixture clears document and chunk rows before and after each test because API tests perform committed writes; the real retrieval test and production retrieval code remain unchanged by the isolation fix.

## Scope Boundaries

Not implemented in this phase:

- autonomous agents or multi-agent workflows
- tool calling
- authentication or authorization
- persistent conversations or complex conversation memory
- production deployment

## Notes

- This file tracks implemented and verified state.
- Phase 4 remains planned and has not been started.
