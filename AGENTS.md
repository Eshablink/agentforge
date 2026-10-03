# AgentForge — Engineering Instructions

## Project identity and verified state

Repository: `Eshablink/agentforge`.

AgentForge is a full-stack document question-answering application. The repository currently contains completed Phase 0–3 work:

- **Phase 0 — Repository setup and project blueprint:** complete.
- **Phase 1 — Application foundation:** complete and merged into `main`.
- **Phase 2 — PostgreSQL + pgvector foundation:** implemented and verified.
- **Phase 3 — Document ingestion + RAG foundation:** implemented and verified.

Phase 2–3 verification was performed by GitHub Actions on PR #3 before its merge: PostgreSQL + pgvector service, Alembic migration, application import smoke test, backend pytest suite, and frontend production build passed. The documented CI runs are PR run 37117613154 and push run 37117610042 on commit `7f77050e739047bc19d955cdc2498054c228b7d4`; subsequent documentation commit `9099462e914c40d843f6080f96efd016802bdd80` also had successful push and PR checks. Treat verification claims as tied to reported run/commit; rerun CI for later code changes.

### Current scope

Implemented: FastAPI APIs; React/TypeScript/Vite frontend; PostgreSQL with pgvector; SQLAlchemy 2.x; Alembic; PDF/TXT/Markdown extraction; deterministic chunking; embedding and LLM abstractions with fake providers for automated tests; vector retrieval; grounded RAG answers with source references; Docker Compose support; PostgreSQL-backed integration tests and GitHub Actions CI.

Not implemented: autonomous agents, tool-calling workflows, authentication/authorization, complex conversation history, multi-tenancy, billing, or production deployment. These remain future work; do not begin a future phase unless explicitly requested.

## Engineering method

Work as a disciplined software engineer. Before changes:

1. Inspect the current branch, relevant code, tests, workflows, and documentation.
2. Understand existing behavior and boundaries before editing.
3. Make the smallest focused change that addresses the requested issue.
4. Preserve public interfaces unless a change is explicitly required.
5. Add or update tests that demonstrate changed behavior.
6. Run relevant tests, builds, and checks; do not claim success without actual results.
7. Update documentation only to match implemented and verified state.
8. Review the diff for unrelated changes, secrets, and regressions.

Do not restart completed phases, refactor unrelated code, introduce speculative features, or describe future functionality as implemented.

## Architecture and data boundaries

Keep UI, API, services, models, database, and provider integrations independently understandable. PostgreSQL + pgvector is the supported runtime/test database; do not substitute SQLite for database or vector integration tests. Runtime embedding dimension and migration schema must remain aligned; migrations must not depend on arbitrary runtime dimension environment values. Alembic imports mapped model modules explicitly while the declarative base remains independently defined.

Tests that write committed PostgreSQL document data must be isolated from other tests. Preserve real pgvector cosine-similarity coverage. Automated tests use fake providers and must not require a paid LLM/embedding API.

Use a deterministic migration path for fresh Docker startup. Handle ingestion failures with rollback and controlled service/API errors. Never expose raw internal exceptions unnecessarily.

## Code quality and security

Prefer clear naming, small modules, explicit interfaces, validation, type safety, focused error handling, and testable code. Avoid unnecessary dependencies, dead code, duplicated logic, hard-coded secrets, broad exception leakage, and import hacks that hide architectural problems.

Never commit API keys, passwords, access tokens, private credentials, or production secrets. Use environment variables and safe `.env.example` placeholders.

## Testing requirements

Meaningful behavior requires tests. Before declaring a change complete, run all relevant checks, including PostgreSQL + pgvector integration when database behavior changes. Verify application imports, Alembic migrations, backend pytest, and frontend production build as appropriate. Never infer tests passed from code inspection or a workflow definition; use actual run results.

## Documentation

Keep `README.md`, `PROJECT_BRIEF.md`, `ARCHITECTURE.md`, `PROGRESS.md`, and `DECISIONS.md` consistent with the repository. Clearly distinguish implemented/verified behavior from planned work. Record significant architecture choices in `DECISIONS.md`.

## Git and delivery

Use conventional, focused commits. Before committing, review changed files, run relevant checks, and ensure no secrets are included. Keep to the requested branch/PR; do not merge a PR unless explicitly asked. For documentation-only work, confirm no application behavior changed.

## Reporting

Summarize files changed, actual checks and results, commit/PR status, and remaining deferred work. Keep claims precise and report blockers honestly.
