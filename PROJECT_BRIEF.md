# AgentForge Project Brief

## Product summary

AgentForge is a full-stack application for document ingestion, grounded RAG, safe registered-tool orchestration, persistent conversations, authenticated user-owned resources, reliable AI provider calls, SSE delivery of generated answers, safe observability, and deterministic regression evaluation.

## Phase status

| Group | Count | Phase | Status |
|---|---:|---|---|
| Complete | 1 | Phase 0 — Repository blueprint | Implemented and verified |
| Complete | 2 | Phase 1 — FastAPI and React foundation | Implemented and verified |
| Complete | 3 | Phase 2 — PostgreSQL + pgvector + SQLAlchemy + Alembic | Implemented and verified |
| Complete | 4 | Phase 3 — Document ingestion, retrieval and grounded RAG | Implemented and verified |
| Complete | 5 | Phase 4 — Agent orchestration and safe registered tools | Implemented and verified |
| Complete | 6 | Phase 5 — Persistent conversations and bounded memory | Implemented and verified |
| Complete | 7 | Phase 6 — Authentication and ownership foundation | Implemented and verified |
| Complete | 8 | Phase 7 — Production AI reliability, SSE delivery, deterministic regression suite | Implemented; verification tied to PR CI |
| Deferred | 9 | SSO/MFA, cloud deployment, distributed rate limiting, billing/analytics | Deferred |

## Implemented capabilities

| Group | Count | Capability | Implementation |
|---|---:|---|---|
| Agent | 1 | Structured orchestration | Typed decisions; bounded execution loop and operational trace |
| Agent | 2 | Safe tool registry | Owner-aware document search, Decimal calculator, date offset; strict schemas and bounded outputs |
| Conversation | 3 | Persistent sessions | PostgreSQL conversations/messages; ownership checks; bounded recent context |
| Authentication | 4 | Account/session foundation | PBKDF2-SHA256 hashes; opaque random bearer tokens stored as hashes; expiry/revocation |
| Ownership | 5 | Private user data | Owned document routes and per-user pgvector filtering; conversation queries scoped to user |
| Reliability | 6 | Provider controls | Config-driven fake/OpenAI selection; per-attempt timeout and bounded retries; normalized safe errors |
| Streaming | 7 | SSE endpoint/UI | Authenticated `/agent/chat/stream`; typed events; generated answer delivered in bounded chunks; single canonical request ID |
| Observability | 8 | Correlated operations | One request ID across header, SSE start event, and telemetry; safe bounded values only |
| Evaluation | 9 | Deterministic regression suite | Git datasets for RAG/tools/agent with fake providers; PASS/FAIL; nonzero on failure; no paid calls |
| UI/CI | 10 | Full-stack flow | React auth/conversation/agent UI; PostgreSQL + pgvector, backend pytest, frontend build |

## Phase 7 architecture

Provider interfaces remain orchestration-independent. Provider calls use per-attempt timeouts plus finite retries, and exceptions are normalized. SSE uses a typed, safe operational event vocabulary where the route owns the single request-level `message_start` and the service emits operational events; `/agent/chat` remains backward compatible. The evaluation suite is a deterministic regression suite (not a generative-model quality benchmark) and runs without paid credentials. Details and event schema are in `ARCHITECTURE.md`.

## Security boundaries and limitations

Only registered typed tools execute. No arbitrary Python, shell, filesystem, generated SQL, or unrestricted network tool. Model output is untrusted; chain-of-thought and secrets are never returned/logged. Ownership isolation remains enforced. Rate limiter and request-ID context are process-local; multiple workers require a gateway/shared store. Provider timeout is per attempt, so retries may extend total duration. This is a production-oriented foundation, not a deployed production service.
