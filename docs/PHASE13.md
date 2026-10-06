# Phase 13: low-cost managed deployment path

Phase 13 makes the cloud deployment definition portable and inexpensive without weakening production security.

## Target architecture

    Browser
      |
      v
    Render static frontend
      |
      v
    Render FastAPI service
      |                 |
      v                 v
    Supabase Postgres   TLS Redis
      |                 |
      +-- pgvector      +-- shared rate limiting
      |
      v
    OpenAI-compatible LLM + embeddings

Render remains the application host. Postgres and Redis are external managed dependencies.

## Why the database moved out of Render

The previous Blueprint created a hosted Postgres resource alongside the application. Phase 13 replaces that with an operator-supplied `DATABASE_URL`.

Benefits:

- Durable data is no longer coupled to the application host.
- A managed Postgres provider can be replaced without changing SQLAlchemy models or migrations.
- Supabase can provide PostgreSQL + pgvector in one service.
- The Render Blueprint stays focused on the API and static frontend.

## Connection handling

AgentForge's settings layer accepts:

- `postgres://...`
- `postgresql://...`
- `postgresql+psycopg://...`

The first two are normalized to `postgresql+psycopg://...` before SQLAlchemy/Alembic use them.

For Supabase, use the **Session Pooler** connection string from the project's Connect screen. Keep SSL enabled in the production connection string, for example:

    postgresql://postgres.<project-ref>:<password>@<pooler-host>:5432/postgres?sslmode=require

Do not use the transaction-pooler form for this application. AgentForge uses regular SQLAlchemy sessions and Alembic migrations.

The existing migration still runs:

    alembic -c alembic.ini upgrade head

It creates the `vector` extension and the AgentForge schema in the managed database.

## Redis

AgentForge production requires:

    RATE_LIMIT_BACKEND=redis
    REDIS_URL=rediss://...

The Redis service must support TLS. An Upstash TCP connection URL is compatible with the existing `redis-py` implementation; no new Redis client library is required.

## Render Blueprint

`render.yaml` now defines only:

- `agentforge-api` Docker web service.
- `agentforge-web` static site.
- External `DATABASE_URL` and `REDIS_URL` secrets.

The API keeps:

    APP_ENV=production
    LLM_PROVIDER=openai
    EMBEDDING_PROVIDER=openai
    RATE_LIMIT_BACKEND=redis

The blueprint uses the free application service tier to minimize hosting cost. A warm paid instance can be selected later without an application code change.

## Operator setup

1. Create Supabase Postgres.
2. Enable/confirm the `vector` extension.
3. Copy the Session Pooler URL and configure `DATABASE_URL`.
4. Create a TLS Redis database and configure `REDIS_URL`.
5. Create/connect the Render Blueprint.
6. Add `OPENAI_API_KEY`.
7. Let the pre-deploy migration run.
8. Verify `/ready`, auth, document ingestion, RAG, tools and streaming.

Never commit credentials. The repository only contains examples and validation rules.

## Verification

Phase 13 adds a regression test for managed PostgreSQL URL normalization. Deployment Validation also asserts that `render.yaml` contains an operator-supplied `DATABASE_URL` and no bundled Postgres resource.

No cloud account is accessed by CI and no paid model calls are made by CI.
