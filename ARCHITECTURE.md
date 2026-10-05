# AgentForge Architecture

## Current verified architecture — Phases 0–7

Phases 0–3 provide the document-RAG foundation. Phases 4–6 add registered safe tools, persistent user-owned conversations, and authentication/authorization. Phase 7 adds provider reliability, authenticated SSE streaming, lightweight observability, and a deterministic evaluation suite — all additive.

```text
React + TypeScript + Vite
        ↓ HTTP + bearer token (SSE for streaming)
FastAPI routes and typed schemas
        ↓
Request-ID middleware / authentication / owner authorization
        ↓
Conversation service (bounded recent context)
        ↓
Agent orchestration (typed decisions, bounded steps)
        ↓
Allowlisted tool registry
  ├─ document_search → existing owner-scoped pgvector retrieval
  ├─ calculator → explicit Decimal operations
  └─ date_offset → deterministic utility
        ↓
PostgreSQL + pgvector (Alembic-managed schema)
```

## Phase 7 additions

### Provider reliability

`app/services/provider_errors.py` defines a normalized error taxonomy (`provider_timeout`, `provider_rate_limited`, `provider_auth`, `provider_unavailable`, `provider_invalid_response`, `provider_config`). `app/services/provider_utils.py` provides bounded retry with classification. `LLMService` and `OpenAIDecisionProvider` apply explicit `llm_timeout_seconds` / `llm_max_retries` and convert failures to safe messages; secrets never appear in logs or responses.

### Streaming (SSE)

`POST /agent/chat/stream` (in `app/api/routes/stream.py`) emits a typed event stream via `app/schemas/stream.py`:

| Event | Payload | Notes |
|---|---|---|
| `message_start` | request_id, conversation_id | |
| `tool_start` | tool | allowlisted tool name |
| `tool_result` | tool, status | safe status only |
| `retrieval` | count | bounded count |
| `token` | text | incremental assistant output |
| `message_end` | answer_kind, tools_used, sources | final state |
| `error` | message, code | safe, bounded error |

No chain-of-thought, no secrets, no prompt text. The non-streaming `/agent/chat` endpoint remains unchanged. Ownership checks and bounded output are preserved for streaming.

### Observability

`app/core/telemetry.py` provides request-ID context and a sanitized `record()` helper; `app/main.py` adds request-ID middleware so every response carries `X-Request-Id`. Only bounded, non-sensitive operational metadata is logged.

### Rate/resource protection

`app/core/rate_limit.py` provides a process-local sliding-window limiter (per-user) used by the streaming endpoint; settings add `ai_requests_per_minute`, `max_prompt_chars`, `max_stream_duration_seconds`, and `max_stream_output_chars`. This is single-process only; a gateway/shared store is required for multiple workers.

### Evaluation

`evaluation/datasets/*.json` hold version-controlled RAG/tool/agent regression cases; `evaluation/runner/run_evals.py` runs them deterministically with fake providers, prints PASS/FAIL, and exits non-zero on failure.

## Preserved Phase 3–6 data paths

Document ingestion, owner-filtered retrieval, conversations, auth, and security boundaries remain as documented in PR #6; Phase 7 does not alter them.

## Security boundaries

No arbitrary Python, shell, filesystem, generated SQL, or unrestricted network tools. Model output is untrusted; only typed, allowlisted tools execute. Operational traces and SSE frames exclude chain-of-thought and secrets. User-owned documents and conversations stay isolated by authenticated user ID.

## Known limitations

Single-process rate limiting and request-ID context; streaming persists the full exchange only after the stream completes. HTTPS/reverse proxy, SSO/MFA, cloud/Kubernetes, billing, and advanced analytics remain deferred.
