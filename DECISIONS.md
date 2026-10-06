# AgentForge decisions

Phases 0–8 are merged into main (`97934d7dd7f016a4d13f17b2afd4e577024d85a1`). Prior ADR-001–022 remain accepted; Phase 9–11 add narrow extensions, not a replacement for authentication, PostgreSQL+pgvector, or the typed tool registry.

## ADR-023 — Native final-answer deltas only

After structured typed tool selection, the OpenAI-compatible adapter emits normalized text deltas; it never exposes provider frames. No retry occurs after stream consumption. Fake simulation and fallback are explicitly distinguished, with one terminal event and no incomplete-message persistence. This does not stream tool decisions, and CI tests the provider with mocked frames rather than paid calls.

## ADR-024 — Deployment artifact validation without real deployment

The separate Deployment Validation workflow builds both images, runs Alembic before serving, and probes safe local health, readiness, API and frontend endpoints. The production static image is separate from development Vite. A trusted HTTPS edge example enforces IP/request/stream limits and no SSE buffering or caching. The workflow does not provision cloud resources, inject production credentials or perform automatic rollback.

## ADR-025 — Bounded owner-filtered RAG relevance

Select up to 30 vector candidates by default (hard cap 40) with the SQL owner predicate applied first. Apply deterministic cosine-plus-small lexical reranking, optional threshold and normalized-text duplicate suppression, then pack only evidence that fits a bounded context. Cite only those used chunks; insufficient evidence stays explicit. Default threshold -1 preserves existing matching behavior. Deterministic fixture pass rates demonstrate regression behavior only; they are not external-model factual accuracy or human relevance measurements.

SSO/MFA, real cloud deployment, distributed traces, non-English lexical tuning and live quality scoring are deferred.
