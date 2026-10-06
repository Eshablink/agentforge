# AgentForge

**A production-style full-stack agentic AI workspace for grounded answers, validated tools, and live streaming.**

AgentForge combines a React + TypeScript product UI with a FastAPI service, PostgreSQL + pgvector retrieval, authenticated multi-user conversations, typed registered tools, OpenAI-compatible model integration, native final-answer streaming, bounded evaluation, and deployment automation.

## Why this project stands out

AgentForge is designed as an **AI engineering system**, not just a chatbot demo.

It demonstrates:

- **Agent orchestration** with explicit, typed decisions and allowlisted tools.
- **Grounded RAG** with PostgreSQL/pgvector, owner-first filtering, deterministic reranking and bounded evidence.
- **Production security** with opaque bearer sessions, PBKDF2 password hashing, ownership enforcement and fail-closed production configuration.
- **Live streaming** with normalized provider deltas, cancellation-safe lifecycle handling and bounded output.
- **Deployment engineering** with non-root images, migration-before-traffic checks, production smoke validation and infrastructure-as-code.
- **Product-quality frontend** with responsive navigation, source-aware answers, tool activity, theme support and intentional loading/error states.

## Product surface

The first screen is a polished authentication experience that explains the product before sign-in. After authentication, the workspace provides:

- Conversation sidebar with create, open and delete.
- Document knowledge base with upload status and chunk counts.
- Streaming agent chat with Stop and keyboard-submit controls.
- Retrieval and tool activity states.
- Evidence cards showing the actual filename, chunk and similarity used by the response.
- Explicit insufficient-evidence states.
- Light and dark themes with persisted preference.
- Responsive mobile navigation and reduced-motion support.

## Architecture

    Browser
      │
      ├── React + TypeScript + Vite
      │       │
      │       └── authenticated workspace + SSE streaming UI
      │
      ▼
    HTTPS edge / platform proxy
      │
      ▼
    FastAPI
      │
      ├── Auth + opaque sessions
      ├── Conversations
      ├── Document ingestion
      ├── Agent orchestration
      ├── Registered tools
      └── Streaming endpoint
      │
      ├───────────────┐
      ▼               ▼
    PostgreSQL      Redis
      │               │
      └── pgvector    └── shared rate limiting
      │
      ▼
    OpenAI-compatible LLM + embeddings

## AI workflow

1. The user submits a bounded prompt.
2. AgentForge resolves an explicit structured decision.
3. If needed, it executes only typed, allowlisted tools.
4. Document search is owner-scoped and candidate-bounded.
5. Evidence is deterministically reranked and deduplicated.
6. RAG context is capped before provider execution.
7. OpenAI-compatible final-answer deltas are normalized into SSE events.
8. Only the completed owned exchange is persisted.

Raw provider frames and hidden reasoning are never exposed through the UI.

## Engineering milestones

| Phase | Status | Result |
| --- | --- | --- |
| 0 | Complete | Engineering contract and architecture |
| 1 | Complete | FastAPI + React foundation |
| 2–3 | Complete | PostgreSQL + pgvector RAG and ingestion |
| 4–6 | Complete | Agent tools, conversations, auth and multi-user isolation |
| 7 | Complete | Streaming, request IDs and deterministic evaluation |
| 8 | Complete | Production configuration and shared rate limiting |
| 9 | Complete | Native final-answer streaming |
| 10 | Complete | Deployment validation and edge hardening |
| 11 | Complete | Advanced bounded RAG quality and offline evaluation |
| 12 | Complete | Product UI/UX overhaul and initial cloud deployment definition |
| 13 | Complete | Low-cost managed Postgres/Redis deployment path |
| 14 | Complete | CodeQL, Dependabot and repository security policy |

Phases 0–13 are implemented on the current branch; merge only after the new deployment checks are green. **A real cloud rollout still requires the owner's cloud accounts and production provider credentials.**

## Technology

**Frontend:** React, TypeScript, Vite, CSS  
**Backend:** Python, FastAPI, SQLAlchemy, Alembic  
**Data:** PostgreSQL, pgvector  
**AI:** OpenAI-compatible chat and embedding providers  
**Streaming:** Server-Sent Events  
**Security:** PBKDF2-SHA256, opaque sessions, owner-scoped data access, bounded resources  
**Deployment:** Docker, Nginx reference edge, Render Blueprint  
**Quality:** pytest, deterministic offline evaluation, GitHub Actions

## Local development

Create a local environment file from the example and run:

    cp .env.example .env
    docker compose up --build

The local stack is intended for development. Production settings deliberately reject fake providers, development database credentials, wildcard CORS and non-TLS shared Redis.

## Verification

AgentForge CI covers:

- PostgreSQL + pgvector migration.
- Backend import smoke test.
- Full backend pytest suite.
- Deterministic evaluation runner.
- TypeScript/Vite production build.

Deployment Validation additionally covers:

- Production backend image build.
- Non-root image checks.
- Frontend production image build and lockfile validation.
- Managed-Postgres URL compatibility checks.
- Migration-before-traffic.
- Production configuration boundaries.
- Redis TLS readiness and fail-closed behavior.
- Health/readiness and application smoke probes.
- Nginx syntax validation.

No paid model calls are required by CI.

## Deployment

The repository uses a **low-cost managed deployment path**:

- **Render:** FastAPI Docker service + React static site.
- **Supabase:** PostgreSQL + pgvector, supplied through `DATABASE_URL`.
- **Upstash or another TLS Redis-compatible service:** shared rate limiting through `REDIS_URL=rediss://...`.
- **OpenAI:** real chat and embedding credentials supplied only through the platform secret manager.

The Render Blueprint intentionally does **not** provision a second Postgres database. This avoids tying durable application data to the application host and makes the database easy to replace later without changing the application architecture.

See [docs/PHASE13.md](docs/PHASE13.md), [docs/PHASE14.md](docs/PHASE14.md), [DEPLOYMENT.md](DEPLOYMENT.md), and [SECURITY.md](SECURITY.md).

## Quality and safety boundaries

The evaluation suite reports deterministic fixture pass rates. It does not claim live retrieval hit rate, external-model factual accuracy or hallucination elimination.

Agent execution is intentionally constrained. The system does not provide arbitrary shell execution, arbitrary Python, unrestricted SQL generation, filesystem automation or unrestricted network access.

## Repository map

    backend/                 FastAPI application
    frontend/                React + TypeScript client
    evaluation/              deterministic offline evaluation
    deploy/                  smoke checks and edge configuration
    docs/                    phase-specific engineering notes
    render.yaml              Render application deployment definition
    AGENTS.md                permanent engineering contract
    ARCHITECTURE.md          system architecture
    DECISIONS.md             accepted design decisions
    PROGRESS.md              milestone status

---

Built as an end-to-end AI engineering portfolio project with a focus on **correctness, security, observability, deployment discipline and product experience**.
