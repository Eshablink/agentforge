# AgentForge architecture

Phases 0–8 are merged on main (`97934d7dd7f016a4d13f17b2afd4e577024d85a1`). Phases 9–11 live in PR #11; they are implemented on a branch and must be verified on its final HEAD before merging. No production cloud deployment is claimed.

## AI delivery and safety

Authenticated `/agent/chat/stream` preserves a single `message_start` with request-ID correlation, typed operational tool events and exactly one successful `message_end` or controlled `error`. OpenAI-compatible final-answer text can be consumed as provider-native deltas after a validated decision; fake decisions emit simulated output, and providers without native support use bounded completed-answer fallback. After meaningful consumption a stream is never retried. Cancelled/error streams do not persist successful messages. Provider payloads and hidden reasoning are never exposed; only registered typed allowlisted tools execute.

## Deployment architecture

Separate one-shot Alembic migrations precede API replicas; PostgreSQL+pgvector and shared Redis are mandatory for production. `/health` is liveness; `/ready` checks serving dependencies without calling models. The production frontend image serves a built static artifact as non-root; the API image is non-root. Deployment validation CI builds both artifacts and probes API/frontend using local fake providers, never deploys to a cloud account. A trusted HTTPS reverse proxy implements IP authentication/AI limits, stream concurrency, SSE no-buffer/no-store and forwarded header trust; see DEPLOYMENT.md.

## Retrieval and evaluation

The database owner predicate applies **before** vector candidate selection. At most `rag_candidate_max` candidates are scored with small lexical overlap and cosine relevance, then deterministically tie-broken, similarity-filtered and duplicate-suppressed. RAG caps context size and sources to the chunks actually included. Empty evidence remains explicit insufficient evidence. Deterministic datasets test source presence, ranking thresholds/duplicates, tools, agent failures and stream lifecycle; reported metrics are case pass rates, not estimates of external-model factual accuracy. Real-world relevance and hallucination risk need separately curated human review.

## Limits

No generated SQL, shell, filesystem or arbitrary code tools; no cross-user retrieval. Deployment requires external TLS/managed services and is not automatic. Native deltas are only final-answer deltas, not tool-decision streaming. No LLM-as-judge or paid CI calls.
