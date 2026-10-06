# AgentForge

Phases 0–8 are COMPLETE and MERGED into main (`97934d7dd7f016a4d13f17b2afd4e577024d85a1`). PR #11 implements Phases 9, 10 and 11 on `feat/agentforge-phases-9-11`; these phases are CI-verifiable on the branch but remain **unmerged and not deployed**.

## Capabilities

- **Phase 9 — native final-answer deltas:** OpenAI-compatible provider streams normalized answer text after a validated structured decision. The fake is offline/simulated; unsupported providers use bounded fallback. `/agent/chat` remains backward compatible. Exactly one request-level start and one successful end or safe error; cancelled/incomplete streams do not persist successful assistant messages.
- **Phase 10 — deployment validation and edge safety:** non-root backend and static frontend images; separate one-shot migrations; CI locally builds images, migrates PostgreSQL+pgvector and probes `/health`, `/ready`, OpenAPI and frontend. A reference HTTPS edge config includes IP throttling, stream connection limits, request size and SSE no-buffer/no-cache. No cloud rollout occurs.
- **Phase 11 — bounded RAG quality:** owner scope is enforced in the SQL candidate query before a small pgvector candidate pool; deterministic lexical/cosine reranking, threshold and duplicate suppression select up to 10 chunks. RAG only lists sources whose content fits the bounded context. Insufficient evidence remains explicit.

The offline version-controlled evaluation reports deterministic fixture pass rates for RAG, tools, agents and streaming, not live factual accuracy. It runs without paid calls or an LLM judge. PostgreSQL integration tests separately verify owner isolation. Source provenance and prompt constraints do **not** prove an external model cannot hallucinate.

## Local development and verification

```bash
cp .env.example .env
docker compose up --build
```

Compose is development-only. For CI, see `.github/workflows/ci.yml` and `.github/workflows/deployment-validation.yml`; the exact **final PR HEAD** must have green results in both. AgentForge CI runs Alembic, import smoke, PostgreSQL-backed full pytest (including the evaluation runner) and frontend production build. Deployment Validation builds both images and performs local migration, readiness and smoke validation. See [DEPLOYMENT.md](DEPLOYMENT.md) for operator rollout; **nothing has been deployed to a production account**.

Phase detail: [Phase 9](docs/PHASE9.md), [Phase 10](docs/PHASE10.md), [Phase 11](docs/PHASE11.md). Security boundaries and deferred scope: [AGENTS.md](AGENTS.md), [ARCHITECTURE.md](ARCHITECTURE.md), [DECISIONS.md](DECISIONS.md), [PROGRESS.md](PROGRESS.md).
