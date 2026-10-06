# AgentForge decisions

Phases 0–8 are merged into main (`97934d7dd7f016a4d13f17b2afd4e577024d85a1`). ADR-001–022 remain accepted: PostgreSQL+pgvector, migrations, hashed auth, owner isolation and typed registered tools are unchanged.

## ADR-023 — Native final-answer text deltas

After a structured, validated tool decision, normalize OpenAI-compatible final-answer text deltas. Never expose raw frames or retry after stream consumption. Fake/simulated and completed-answer fallback modes remain explicit; exactly one request start and one safe terminal, and only complete owned exchanges persist. The tool decision itself is not provider-native streamed. CI mocks provider frames without paid calls.

## ADR-024 — Local deployment validation without a cloud rollout

The separate Deployment Validation workflow builds both non-root production images, applies Alembic before local serving and probes `/health`, `/ready`, OpenAPI and frontend health. An operator must configure the trusted HTTPS edge; the included example limits IP auth/AI requests, concurrent streams, request size, buffering and cache. The workflow does not provision accounts, deploy, or guarantee an automated rollback.

## ADR-025 — Bounded owner-filtered evidence selection

PostgreSQL applies the owner predicate before a bounded pgvector candidate limit. Up to 30 candidates by default (maximum 40) undergo a small deterministic cosine-plus-lexical rerank, optional similarity threshold and normalized-text duplicate suppression, with stable tie-breaks. RAG cites only chunks included in a bounded context; no evidence or blank answer yields insufficient evidence. Threshold defaults to -1 for backward compatibility. Tests and deterministic fixture pass rates verify these contracts, not real-world factual accuracy or hallucination prevention.

These three phases are implemented on PR #11 and are **CI-verified only if both workflows pass on its final HEAD**. They are not merged or actually deployed. SSO/MFA, automatic real-cloud rollout, multilingual lexical tuning and live LLM-as-judge scoring are intentionally deferred.
