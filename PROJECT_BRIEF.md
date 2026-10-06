# AgentForge project brief

AgentForge is an authenticated full-stack document-RAG and registered-tool agent. Phases 0–8 are **complete and merged** into main at `97934d7dd7f016a4d13f17b2afd4e577024d85a1`. Phases 9, 10 and 11 are **implemented and CI-verifiable on the existing draft PR #11**, not yet merged or deployed.

| Phase | Implemented capability | What verification establishes |
|---|---|---|
| 9 — Native AI streaming | OpenAI-compatible final-answer deltas, offline fake simulation, bounded fallback, controlled single-terminal SSE, cancellation-safe frontend | Mocked provider and stream lifecycle tests; no paid CI |
| 10 — Deployment automation + edge security | Non-root API/static frontend images, one-shot migration before local traffic, HTTPS edge reference limits and safe smoke probes | Deployment Validation builds both images and checks local migration, health, readiness, OpenAPI and frontend; **not** a cloud rollout |
| 11 — Advanced RAG + AI quality | Owner-filtered pgvector candidate cap, deterministic reranking/dedup/threshold, context-budget-based citation selection | PostgreSQL owner-isolation tests, context/source tests and small fixture scoring; **not** a guarantee of external-model factual accuracy |

Stable hashed sessions, PBKDF2 passwords, typed allowlisted tools, bounded requests, PostgreSQL+pgvector and Phase 0–8 APIs remain. The offline runner reports per-category deterministic fixture pass rates with no paid calls or LLM judge. Current Phase 9–11 completion status must be judged against **both green workflows at the final PR HEAD**, not older run numbers. SSO/MFA, real cloud deployment, multilingual lexical tuning and broad live model-quality scoring are deferred.
