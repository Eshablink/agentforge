# AgentForge

Phases 0–8 are complete and merged into `main` (`97934d7dd7f016a4d13f17b2afd4e577024d85a1`). This branch implements Phases 9–11 on [PR #11](https://github.com/Eshablink/agentforge/pull/11). Phase 9 streams native OpenAI-compatible **final-answer deltas** where supported, with bounded fake/fallback modes. Phase 10 adds a non-root static frontend image, edge proxy example and a deployment-validation workflow. Phase 11 improves owner-filtered pgvector retrieval with bounded candidate reranking and evidence context.

## Capabilities and verification

The existing authenticated RAG, conversations, tools, health/readiness and `/agent/chat` remain. The expanded deterministic evaluation covers evidence/source behavior, duplicate and threshold ranking, tools/agent failures and stream lifecycle. Printed pass rates count fixture cases, not live model quality. No paid provider or LLM-as-judge runs in CI. GitHub Actions tests PostgreSQL+pgvector migration/import/pytest (including evaluation) and frontend build; deployment validation builds production images and probes `/health`, `/ready`, API schema and frontend. See current PR-head checks for results, not older green runs.

## Run locally

```bash
cp .env.example .env
docker compose up --build
```

Local compose is development-only. For an operator-managed deployment, inject secrets and follow [DEPLOYMENT.md](DEPLOYMENT.md); TLS terminates at the trusted edge. Production is **not** actually deployed by this repository. Native final-answer streaming starts after the validated decision; tools remain allowlisted and owner-scoped. RAG citations refer to evidence included in the bounded context, not proof that a live model cannot hallucinate.

## Documentation

[Phase 9](docs/PHASE9.md) · [Phase 10](docs/PHASE10.md) · [Phase 11](docs/PHASE11.md) · [Architecture](ARCHITECTURE.md) · [Decisions](DECISIONS.md) · [Progress](PROGRESS.md).
