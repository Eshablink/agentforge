# AgentForge Progress

## Current status

Phases 0–6 are implemented and CI-verified on `main`. Phase 7 (production AI reliability, streaming, and evaluation) is implemented on the `feat/agentforge-phase-7` branch and is additive to the Phase 0–6 foundation. This is a production-oriented foundation, not a deployed service.

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
| Complete | 8 | Phase 7 — Reliability, streaming, evaluation | Implemented; CI on PR branch |
| Deferred | 9 | SSO/MFA, deployed cloud ops, billing, advanced analytics | Not implemented |

## Phase 7 implementation

- Provider reliability: bounded timeouts (`llm_timeout_seconds`) and finite retries (`llm_max_retries`); normalized provider error taxonomy (`app/services/provider_errors.py`, `provider_utils.py`) mapped to safe category codes; fake provider remains the CI default; provider selection stays configuration-driven; secrets never logged.
- Streaming: authenticated SSE endpoint `POST /agent/chat/stream` with a typed event contract (`message_start`, `tool_start`, `tool_result`, `retrieval`, `token`, `message_end`, `error`) in `app/schemas/stream.py`; ownership checks and bounded output preserved; no chain-of-thought or secrets; `/agent/chat` remains backward compatible.
- Frontend streaming: typed SSE contract in `frontend/src/types/app.ts`, an authenticated fetch-based SSE parser in `client.ts`, and incremental rendering with tool activity, a Cancel control, and graceful error handling in `HomePage.tsx`.
- Observability: request-ID propagation (`app/core/telemetry.py`, middleware in `app/main.py`) with bounded/sanitized operational metadata only.
- Rate/resource protection: process-local sliding-window limiter (`app/core/rate_limit.py`) and additional bounds (prompt/stream/output) in settings; deployment limitation documented below.
- Evaluation: version-controlled datasets under `evaluation/datasets/` and a deterministic runner `evaluation/runner/run_evals.py` (RAG, tool, agent regression) with clear PASS/FAIL and non-zero exit on failure; no paid API calls.

## Verification record

The Phase 7 PR-head CI is verified by GitHub Actions (PostgreSQL + pgvector, Alembic upgrade, import smoke test, full pytest, frontend TypeScript/Vite build, and the Phase 7 evaluation suite). Fake providers require no paid credentials.

## Known limitations

The in-process rate limiter and request-ID context are single-process only; a gateway or shared store is required for multi-worker/replica deployments. Streaming persists the full exchange after the stream completes; disconnect/cancellation before completion does not persist a partial assistant message. See `ARCHITECTURE.md` for the full security/architecture detail.
