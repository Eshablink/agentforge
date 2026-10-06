# AgentForge progress

**Current branch:** Phase 13 deployment path is implemented on `feat/low-cost-cloud-deployment`. The branch keeps the production application architecture intact while replacing the bundled Render Postgres resource with external managed Postgres + Redis services.

## Phase acceptance gates

| Phase | Implementation | Verification |
| --- | --- | --- |
| 0 | Engineering contract, security boundaries and architecture | Repository-level instructions |
| 1 | FastAPI + React/Vite foundation | Backend tests and frontend build |
| 2–3 | PostgreSQL + pgvector RAG, ingestion and sources | Alembic + PostgreSQL integration tests |
| 4–6 | Agent tools, conversations, auth and multi-user isolation | Backend unit/integration coverage |
| 7 | SSE streaming, request IDs and deterministic evaluation | Streaming lifecycle tests + evaluation runner |
| 8 | Production configuration, Redis limiter and operational hardening | Production configuration and deployment validation |
| 9 | Native final-answer provider deltas | Mocked provider lifecycle tests |
| 10 | Production images, edge limits and deployment smoke validation | Backend/frontend image build + smoke workflow |
| 11 | Owner-first retrieval, deterministic reranking and bounded RAG context | PostgreSQL isolation + fixture evaluation |
| 12 | Premium responsive frontend, deployment IaC and platform-ready port binding | Frontend TypeScript/Vite build + deployment validation |
| 13 | External managed Postgres/Redis deployment path | URL normalization tests + deployment-contract validation |
| 14 | Security and supply-chain hardening | CodeQL + Dependabot + security policy |

## Phase 13 acceptance

Phase 13 keeps Render responsible only for the application services and moves durable infrastructure to managed providers:

- `DATABASE_URL` may use the standard `postgres://` or `postgresql://` format returned by managed Postgres providers.
- AgentForge normalizes those URLs to `postgresql+psycopg://` for SQLAlchemy.
- Render no longer provisions the application database in `render.yaml`.
- The API service uses a Render-safe secret `DATABASE_URL` supplied by the operator.
- Shared Redis remains an explicit TLS `rediss://` secret.
- The Render Blueprint uses the free API service tier to minimize recurring hosting cost.

## Verification protocol

Final verification must check the exact branch head used by GitHub Actions. AgentForge CI covers PostgreSQL+pgvector migrations, import smoke, full pytest, deterministic evaluation and the TypeScript/Vite production build. Deployment Validation covers production image construction, non-root checks, managed-Postgres URL normalization, migration-before-traffic, production configuration boundaries, Redis TLS readiness/fail-closed behavior, health/readiness, smoke probes and Nginx syntax.

## Quality limitations

The offline evaluation reports deterministic fixture pass fractions rather than live retrieval hit rate, model factual accuracy or an LLM-as-judge score. RAG provenance is the provenance of supplied context, not proof of every generated claim.

A real cloud rollout still requires the owner's Render, managed-Postgres, Redis and model-provider accounts. Platform free-tier sleep/pause/retention limits can change; verify current provider limits before treating a free deployment as a permanent hosted service.

SSO/MFA, broad multilingual retrieval tuning and automatic rollback orchestration remain deferred.

## Phase 14 acceptance

Repository-level CodeQL, dependency review and Dependabot controls now complement the application security boundary. No production credentials are used by the security workflow.
