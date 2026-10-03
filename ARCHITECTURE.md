# AgentForge Architecture

## Current verified architecture — Phases 0–6

Phases 0–3 provide the document-RAG foundation. Phases 4–6 add registered safe tools, persistent user-owned conversations, and authentication/authorization. The implementation is CI-verified on PR #6; this is a production-oriented foundation, not a deployed service.

```text
React + TypeScript + Vite
        ↓ HTTP + bearer token
FastAPI routes and typed schemas
        ↓
Authentication / owner authorization
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

## Preserved Phase 3 data paths

PDF/TXT/Markdown upload → validation/extraction → deterministic chunks → embedding abstraction → transactional PostgreSQL persistence. Query → embedding → the existing pgvector cosine retrieval service → context → grounded LLM answer and source references.

For authenticated requests, `user_id` flows through agent → document-search tool → retrieval query, which filters on owner. Legacy `/documents` and `/chat` paths are retained for compatibility with unowned legacy rows only. The agent does not duplicate vector search.

## Agent controls

| Group | Count | Control |
|---|---:|---|
| Agent | 1 | Structured validated provider decision; model output is untrusted |
| Tools | 2 | Allowlist: document search, calculator, date offset |
| Validation | 3 | Typed per-tool arguments; unknown tools and extra/invalid arguments rejected |
| Limits | 4 | Bounded iterations, calls, `top_k`, chunks, text, tool results and trace events |
| Execution | 5 | No arbitrary Python, shell, filesystem, generated SQL or unrestricted network |
| Trace | 6 | Operational events only; no chain-of-thought or secrets |

The RAG tool calls the existing `RetrievalService`. Provider abstractions permit external integrations; deterministic fakes are used in CI.

## Authentication, ownership and conversation memory

Passwords use salted PBKDF2-SHA256 hashes. Random bearer credentials are returned to the browser while only their hashes are stored; server-side expiry and revocation are checked per request. Protected document, chat, agent and conversation APIs derive user identity from the auth dependency and scope records by `user_id`; foreign conversation IDs return not found.

Messages are stored in PostgreSQL. Memory includes only a bounded recent window from the requested owned conversation, ordered by timestamp and ID and limited by message count/character count. User/assistant turns persist in one transaction. The browser stores tokens in memory, so a reload requires sign-in.

## Database and migrations

| Group | Count | Table/component | Role |
|---|---:|---|---|
| Data | 1 | `users`, `auth_sessions` | User account, password hash, hashed bearer token, expiry/revocation |
| Data | 2 | `documents`, `document_chunks` | Nullable owner for legacy rows; text, metadata and pgvector embeddings |
| Data | 3 | `conversations`, `messages` | Per-user history and bounded operational metadata |
| Data | 4 | SQLAlchemy 2.x + PostgreSQL/pgvector | ORM and vector queries |
| Schema | 5 | Alembic | Deterministic incremental migrations; existing pgvector schema preserved |

Alembic imports registered models using the standalone `app.db.base`; integration checks use PostgreSQL + pgvector, not SQLite. Docker waits for DB health and applies migrations before API startup.

## Verification and deferred scope

The latest code and docs CI result should be taken from the current PR #6 head. CI provisions PostgreSQL + pgvector, applies Alembic, checks import, runs full pytest and builds the frontend. This project is not externally deployed. SSO/MFA, formal rate limiting, HTTPS/reverse proxy operations, monitoring, cloud/Kubernetes, billing, analytics and Phase 7+ remain deferred.
