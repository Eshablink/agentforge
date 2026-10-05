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

`app/services/provider_errors.py` defines a normalized error taxonomy (`provider_timeout`, `provider_rate_limited`, `provider_auth`, `provider_unavailable`, `provider_invalid_response`, `provider_config`). `app/services/provider_utils.py` provides finite retry with classification.

The `llm_timeout_seconds` setting is a **per-attempt timeout**, not a total operation budget: it is applied to the OpenAI HTTP client (`timeout=`), and the provider is allowed `llm_max_retries` additional attempts with bounded exponential backoff. The maximum operation duration is therefore approximately `(max_retries + 1) × timeout_seconds + bounded_backoff`. The retry helper does not run arbitrary callables in threads/processes to interrupt them.

### Streaming (SSE)

`POST /agent/chat/stream` (in `app/api/routes/stream.py`) emits a typed event stream via `app/schemas/stream.py`:

| Event | Payload | Layer | Notes |
|---|---|---|---|
| `message_start` | request_id, conversation_id | route | exactly one per stream; `request_id` equals the response `X-Request-Id` |
| `tool_start` | tool | service | allowlisted tool name |
| `tool_result` | tool, status | service | safe status only |
| `retrieval` | count | service | bounded count |
| `token` | text | service | bounded incremental text chunk |
| `message_end` | answer_kind, tools_used, sources | service | final state |
| `error` | message, code | service | safe, bounded error |

The stream is **transport-level SSE delivery of generated output**: the agent produces bounded answer text, and the service emits it incrementally in bounded chunks. It is **not** provider-native token streaming; the provider returns structured decisions whose final text is then chunked and delivered. No chain-of-thought, no secrets, no prompt text. The non-streaming `/agent/chat` endpoint remains unchanged.

### Request ID correlation

A single canonical request ID is created once per HTTP request in the `main.py` middleware. It is exposed through the response `X-Request-Id` header, through `request.state.request_id` (which the streaming route reuses inside its body generator), and through `telemetry.get_request_id()` for log correlation. `message_start.request_id`, the header, and all telemetry therefore refer to the same ID.

### Observability

`app/core/telemetry.py` provides request-ID context and a sanitized `record()` helper. Only bounded, non-sensitive operational metadata is logged, including endpoint, method, request/provider/tool/retrieval latency, and status.

### Rate/resource protection

`app/core/rate_limit.py` provides a process-local sliding-window limiter (per-user) shared by the chat and streaming endpoints; settings add `ai_requests_per_minute`, `max_prompt_chars`, `max_request_body_bytes`, `max_stream_duration_seconds`, and `max_stream_output_chars`. This is single-process only; a gateway/shared store is required for multiple workers.

### Evaluation

`evaluation/datasets/*.json` hold version-controlled RAG/tool/agent regression cases; `evaluation/runner/run_evals.py` runs them deterministically with fake providers and prints PASS/FAIL, exiting non-zero on failure. This is a **deterministic regression suite**, not a generative model-quality benchmark. It checks retrieval/source presence, grounding-related answer behavior, tool selection and argument validation, invalid-tool rejection, bounded agent execution, and provider-failure safety — without paid API calls.

## Preserved Phase 3–6 data paths

Document ingestion, owner-filtered retrieval, conversations, auth, and security boundaries remain as documented in PR #6; Phase 7 does not alter them.

## Security boundaries

No arbitrary Python, shell, filesystem, generated SQL, or unrestricted network tools. Model output is untrusted; only typed, allowlisted tools execute. Operational traces and SSE frames exclude chain-of-thought and secrets. User-owned documents and conversations stay isolated by authenticated user ID.

## Known limitations

Single-process rate limiting and request-ID context; streaming is transport-level SSE chunking of generated output (not provider token streaming); streaming persists the full exchange only after the stream completes. HTTPS/reverse proxy, SSO/MFA, cloud/Kubernetes, billing, and advanced analytics remain deferred.
