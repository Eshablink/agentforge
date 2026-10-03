# AgentForge Engineering Instructions

## Project identity and verified state

Repository: `Eshablink/agentforge`.

AgentForge is a full-stack document question-answering application. Phases 0–3 are complete and merged: application foundation; PostgreSQL + pgvector; PDF/TXT/Markdown ingestion; deterministic chunking and embeddings; vector retrieval; grounded RAG with source references; and a minimal React frontend.

Post-merge CI for merge commit `67e983772257dc575475e86ebecbe6548c968eb9` passed in run [37117875205](https://github.com/Eshablink/agentforge/actions/runs/37117875205). Documentation cleanup merge commit `cded4a9bf39d267200f1de072600d1648b19182f` passed in run [37119471555](https://github.com/Eshablink/agentforge/actions/runs/37119471555). These runs covered PostgreSQL + pgvector, Alembic migration, import smoke test, backend pytest, and frontend production build. Historical verification applies to those commits; rerun CI for later code changes.

### Current scope

Implemented: FastAPI routes/services; React/TypeScript/Vite UI; PostgreSQL + pgvector; SQLAlchemy 2.x; Alembic; document ingestion; embedding and LLM abstractions; retrieval; grounded answers with citations; Docker Compose; PostgreSQL-backed CI.

Not implemented: agents, tool calling, authentication/authorization, conversation memory, multi-tenancy, billing, or production deployment. Do not treat proposed future work as shipped or begin a new phase unless explicitly requested.

## Engineering method

Before significant changes, inspect repository guidance, current architecture, code, tests, migrations, workflows, and documentation. Preserve existing behavior and interfaces unless a scoped change requires otherwise. Make minimal focused changes, add characterization/regression tests, run relevant checks, inspect the diff, and update docs to verified state. Do not refactor unrelated systems, introduce speculative dependencies/features, or rewrite working code without cause.

## Data and architecture boundaries

Keep UI, API, services, models, database, and provider integrations distinct. PostgreSQL + pgvector is the supported runtime and integration-test database; do not replace DB tests with SQLite. Reuse the existing retrieval service for RAG. Keep schema dimensions and runtime embeddings aligned. Migrations must be deterministic. Alembic must load ORM model metadata without circular imports.

Treat uploaded content and model output as untrusted. Never execute model-produced code. Avoid unrestricted shell, filesystem, SQL, or network operations. Keep errors controlled, enforce ownership for private records, bound requests and outputs, and never log secrets or hidden chain-of-thought.

## Testing requirements

Automated tests should be deterministic and must not require paid API calls. Preserve PostgreSQL + pgvector integration coverage and isolate committed test data. For relevant changes, run import smoke tests, migrations, backend tests, and frontend build. Never claim a check passed without its actual result.

## Security and configuration

Never commit credentials or secrets. Use environment variables and safe `.env.example` placeholders. Validate production configuration explicitly. Avoid wildcard CORS with credentialed access in deployed environments.

## Documentation and delivery

Keep README.md, PROJECT_BRIEF.md, ARCHITECTURE.md, DECISIONS.md, and PROGRESS.md consistent. Separate implemented/verified capabilities from deferred plans. Use focused conventional commits. Do not merge PRs without explicit instruction. Report tests, CI, changed files, commits, and remaining limitations accurately.

## Phase boundary

The currently verified repository state is Phase 0–3. Any later phase remains unimplemented until separately scoped, implemented, tested, and documented. Do not begin Phase 4 or later without explicit user direction.
