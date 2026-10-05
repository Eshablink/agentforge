# AgentForge Progress

## Current status

Phases 0–6 are implemented and CI-verified on `main`. Phase 7 (production AI reliability, SSE delivery, and deterministic regression evaluation) is implemented on `feat/agentforge-phase-7` and is additive to the Phase 0–6 foundation. This is a production-oriented foundation, not a deployed service.

## Roadmap

| Group | Count | Phase | Status |
|---|---:|---|---|
| Complete | 1 | Phase 0 — Repository blueprint | Implemented and verified |
| Complete | 2 | Phase 1 — Application foundation | Implemented and merged |
| Complete | 3 | Phase 2 — PostgreSQL + pgvector | Implemented and verified |
| Complete | 4 | Phase 3 — Document ingestion and RAG | Implemented and verified |
| Complete | 5 | Phase 4 — Agent orchestration and safe registered tools | Implemented and verified by CI |
| Complete | 6 | Phase 5 — Persistent conversations and bounded recent memory | Implemented and verified by CI |
| Complete | 7 | Phase 6 — Authentication and ownership foundation | Implemented and verified by CI |
| Complete | 8 | Phase 7 — Reliability, SSE delivery, deterministic regression suite | Implemented; current PR-head CI verification required |
| Deferred | 9 | SSO/MFA, deployed cloud ops, billing, advanced analytics | Not implemented |

## Phase 7 implementation

- Provider reliability: explicit per-attempt client timeouts (`llm_timeout_seconds`) and finite retries (`llm_max_retries`) with bounded backoff; normalized provider error taxonomy; fake provider remains the CI default; provider selection remains configuration-driven; secrets are not logged. The timeout is **per attempt**, not a total-operation deadline.
- Streaming: authenticated SSE endpoint `POST /agent/chat/stream` with typed event contract (`message_start`, `tool_start`, `tool_result`, `retrieval`, `token`, `message_end`, `error`). The route emits exactly one `message_start` using the canonical middleware request ID. The agent returns generated answer text which is delivered incrementally in bounded SSE chunks; this is not provider-native token streaming. `/agent/chat` remains backward compatible.
- Frontend SSE: typed event contract, authenticated fetch-based parser, incremental chunk rendering, tool activity, cancel action, source visibility, and graceful error handling.
- Observability: one request ID per HTTP request, correlated across `X-Request-Id`, SSE `message_start`, and telemetry; bounded operational metadata only.
- Rate/resource protection: process-local sliding-window limiter shared by agent endpoints plus prompt, request-body, output, duration, tool, and trace bounds.
- Evaluation: version-controlled RAG/tool/agent datasets with deterministic fake-provider regression cases. Covers source/retrieval behavior, answer grounding against retrieved text, tool selection/allowlisting, invalid-tool rejection, bounded execution, and safe provider failures. It is a regression suite, not a broad generative-quality benchmark.

## Verification record

The latest PR-head GitHub Actions run is authoritative for this branch. CI uses PostgreSQL + pgvector, applies Alembic, performs import smoke, runs full backend pytest (including the evaluation-runner test), and builds the frontend. See the PR checks for current verification.

## Known limitations

The in-process limiter and request-ID context are single-process only; multi-worker/replica deployments need a gateway or shared store. Provider timeout is per attempt, so an operation with retries may take longer than one timeout period. SSE chunks deliver completed generated output rather than native provider token deltas. A disconnected stream does not persist a partial assistant message.
