# AgentForge Architecture

## Current verified platform architecture

Phases 0–3 provide the document-RAG data foundation. Phases 4–6 add a safe agent path, persistent conversation state and user ownership/authentication. The latest full green application run and audit references are tracked in `PROGRESS.md` and PR #6; this is not a deployed production service.

```text
React + TypeScript + Vite
        ↓ HTTP / bearer session
FastAPI routes and schemas
        ↓
Authentication + owner authorization
        ↓
Conversation service (bounded recent context)
        ↓
Agent orchestration (typed decisions, bounded steps)
        ↓
Registered tool registry
  ├── document_search → existing owner-filtered pgvector retrieval
  ├── calculator → explicit Decimal operations
  └── date_offset → deterministic date utility
        ↓
PostgreSQL + pgvector (Alembic-managed schema)
```

## Phase 3 ingestion and retrieval (preserved)

```text
PDF/TXT/Markdown upload → validation/extraction → deterministic chunks
  → embedding provider abstraction → transactional PostgreSQL persistence
Question → query embedding → pgvector cosine distance → retrieved sources
  → existing grounded LLM answer service → answer and citations
```

Authenticated retrieval always includes owner filtering. Legacy Phase 3 routes query only unowned legacy documents; authenticated owned records are handled by `/documents/me`, `/me/chat`, and the authenticated agent/conversation routes. Document search invokes the shared `RetrievalService`; no duplicate vector implementation exists.

## Agent safety

| Group | Count | Control |
|---|---:|---|
| Safety | 1 | Structured typed decision schema; provider output is untrusted and validated |
| Safety | 2 | Registry allowlist; unknown tools are rejected |
| Safety | 3 | Strict per-tool input validation; calculator supports explicit arithmetic only |
| Safety | 4 | Limits on agent steps, tool calls, retrieved chunks, content, output and trace events |
| Safety | 5 | No arbitrary Python, shell, filesystem, generated SQL, or unrestricted network tools |
| Safety | 6 | Trace records operational events only; no hidden reasoning or credentials |

Providers are abstractions; CI uses the deterministic fake provider. Optional external provider configuration is environment-driven.

## Identity, ownership and memory

Passwords are salted PBKDF2-SHA256 hashes, never stored plaintext. The client receives an opaque random bearer credential; PostgreSQL stores only its hash with expiry and revocation state. Conversation/document queries enforce `user_id` from authenticated identity, not client-provided owner IDs. Conversations and messages cascade by foreign key. Context selects recent messages with deterministic ordering, then applies message-count and character bounds. Messages from unrelated conversations are never included.

Browser token storage is in-memory, so page reload requires sign-in. Configure explicit production CORS origins and credentials when selecting an external LLM provider. Before external deployment, provision HTTPS/reverse proxy, rate limiting, monitoring, and operational secret management.

## Database and migrations

| Group | Count | Table/component | Responsibility |
|---|---:|---|---|
| Data | 1 | `users` | Account identity and password hash |
| Data | 2 | `auth_sessions` | Token hash, expiry and revocation |
| Data | 3 | `documents` | Document metadata and nullable owner for legacy rows |
| Data | 4 | `document_chunks` | Chunk text/order and pgvector embedding |
| Data | 5 | `conversations` | User-owned conversation metadata |
| Data | 6 | `messages` | Ordered role/content and bounded operational metadata |
| Schema | 7 | Alembic | Deterministic schema revisions, preserving Phase 3 pgvector |

`app.db.base` owns the standalone declarative base. Alembic imports all model modules to register metadata without circular imports. PostgreSQL + pgvector is mandatory for integration verification; SQLite is not substituted.

## Verification and boundaries

The audited Phase 4–6 suite uses PostgreSQL + pgvector, migrations, an import smoke test, backend pytest and TypeScript/Vite build. The specific run/commit pairs are maintained in `PROGRESS.md` and the PR description.

Not implemented: SSO/MFA, rate limiting, billing, multi-tenant administration, cloud/Kubernetes deployment, analytics platform, arbitrary code execution, or Phase 7+ work.
