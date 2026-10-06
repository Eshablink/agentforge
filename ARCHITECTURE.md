# AgentForge architecture

Phases 0–8 are COMPLETE and MERGED on main at `97934d7dd7f016a4d13f17b2afd4e577024d85a1`. Phases 9–11 are implemented in PR #11 and require green results for the final branch HEAD before merge. They are not deployed to a production cloud environment.

## Stream delivery (Phase 9)

Authenticated `/agent/chat/stream` owns exactly one request-ID-correlated `message_start`. The structured decision/provider-independent typed allowlisted tool loop remains intact. OpenAI-compatible native final-answer text deltas are normalized into bounded `token` events; fake simulated deltas and completed-answer fallback have explicit mode labels. The route emits one terminal `message_end` or safe `error`, persists only successful owned conversations and closes streams on disconnect. Native deltas are for final answers, not tool decisions. Telemetry contains duration, first-token latency, counts and categories—never answer text, raw provider frames or hidden reasoning.

## Deployment validation (Phase 10)

One-shot Alembic migrations precede serving; PostgreSQL+pgvector and Redis are required for an external production deployment. `/health` has no paid or database calls; `/ready` checks serving dependencies. The separate Deployment Validation workflow builds non-root backend/static frontend production images, exercises PostgreSQL+pgvector and TLS Redis in production mode, rejects fake providers, runs one-shot migration before traffic, and probes health/readiness and smoke endpoints. The reference HTTPS proxy keeps health/readiness outside AI throttling and enforces bounded bodies, trusted forwarding and SSE no-buffer/no-store behavior.

## Evidence retrieval (Phase 11)

The database `Document.user_id` filter applies **before** pgvector candidate ordering and limit. The candidate pool defaults to 30 and cannot exceed 40. Deterministic reranking combines cosine similarity with a small lexical-overlap bonus; non-finite/low similarities are filtered, normalized duplicate text is suppressed, and ties break by similarity, document ID, chunk index and chunk ID. At most 10 chunks become results. RAG packs only text fitting the bounded context budget and returns only sources actually used there; empty retrieval or blank answer returns explicit insufficient evidence. This bounds provenance, not arbitrary external-model factual correctness.

The offline evaluation includes source/grounding fixtures, relevance and deduplication, threshold, SQL owner-predicate shape, valid/invalid tools, bounded agent/provider failures, simulated stream ordering/terminal/error/output-budget cases. Metric values are deterministic per-fixture pass rates rather than live hit rates or hallucination guarantees. PostgreSQL integration tests independently verify cross-user isolation. No SQLite fallback, LLM-as-judge, paid API CI or model-controlled unsafe execution.

## Remaining limits

English-oriented lexical overlap and the default permissive similarity threshold need deployment-specific evaluation. HTTPS proxy, Redis and managed database are operator-provisioned; SSO/MFA and broader language-aware retrieval remain deferred. See [DEPLOYMENT.md](DEPLOYMENT.md) for operational rollout and [PROGRESS.md](PROGRESS.md) for exact final-HEAD verification.
