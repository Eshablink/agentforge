# AgentForge deployment runbook

## Current state

AgentForge is production-ready at the application and deployment-definition level, but **no cloud production rollout is claimed by this repository**. The repository defines a low-cost deployment pattern using Render for the app services, Supabase Postgres + pgvector for durable data, and a TLS Redis-compatible service such as Upstash for shared rate limiting.

## Recommended portfolio deployment

Use the same two Render application services already defined in `render.yaml`:

- `agentforge-api`: Dockerized FastAPI service.
- `agentforge-web`: React static site.

Keep durable Postgres outside the Render Blueprint:

- **Supabase Postgres + pgvector** for documents, embeddings, accounts and conversations.
- Use the **Supabase Session Pooler** connection string for a hosted backend. The application accepts the standard `postgresql://` URL and normalizes it to SQLAlchemy's `postgresql+psycopg://` form.
- Keep `sslmode=require` in the production connection string.

Keep shared Redis outside the Render Blueprint:

- **Upstash Redis over TLS** is a compatible choice for `RATE_LIMIT_BACKEND=redis`.
- Set `REDIS_URL` to the TCP/TLS URL beginning with `rediss://`; AgentForge intentionally rejects non-TLS shared Redis in production.

The repository does not vendor or provision either external service. That keeps credentials out of Git and avoids coupling the application schema to one cloud vendor.

## Required production secrets

Add these in the `agentforge-api` service before the first production deploy:

    DATABASE_URL=postgresql://postgres.<project-ref>:<password>@<pooler-host>:5432/postgres?sslmode=require
    OPENAI_API_KEY=<real provider credential>
    REDIS_URL=rediss://default:<password>@<external-redis-host>:6379

Do not commit these values.

Use the Supabase **Session Pooler** endpoint for the database rather than the transaction pooler. The application uses normal SQLAlchemy sessions and Alembic migrations, which are a better fit for session semantics.

## First rollout

1. Create a Supabase project and ensure the `vector` extension is available.
2. In Supabase **Connect**, copy the Session Pooler connection string and replace the password. Keep `sslmode=require`.
3. Create a TLS Redis database and copy its `rediss://` TCP connection URL.
4. Connect `Eshablink/agentforge` to Render and create the Blueprint from `render.yaml`.
5. Add `DATABASE_URL` and `OPENAI_API_KEY` to `agentforge-api`; the Blueprint wires the existing Render Key Value service into `REDIS_URL`.
6. Let Render run `alembic -c alembic.ini upgrade head` in the pre-deploy step before traffic.
7. Verify `/health` and `/ready`.
8. Open the frontend and test registration/login.
9. Upload a small non-sensitive document and verify indexed retrieval.
10. Run a tool-assisted prompt and a streaming prompt.
11. Review logs and request-ID metadata, then add a custom domain only after the generated deployment is stable.

## Render service notes

The blueprint uses the free web-service tier to minimize recurring platform cost. Free service instances may sleep when idle, so the first request after inactivity can be slower. For a continuously warm portfolio demo, move only the API service to an appropriate paid tier later; no application architecture change is required.

The static frontend remains a Render static site and therefore does not consume a continuously running server process.

## Managed database notes

Supabase supports PostgreSQL extensions including pgvector. The current migrations enable `vector` and create the cosine-oriented vector index expected by AgentForge.

For hosted IPv4-only environments, prefer Supabase's shared Session Pooler endpoint. Avoid the transaction pooler for this application because ordinary SQLAlchemy/Alembic session behavior is a better fit for session-mode connections.

## Custom domains

The Blueprint automatically wires the platform-generated frontend URL into backend CORS and the backend URL into the frontend build. For a custom frontend domain, update `CORS_ORIGINS` to the exact HTTPS origin before opening the application through that domain.

Review the edge example in `deploy/nginx.edge.example.conf` if placing another reverse proxy in front of the application. Never configure wildcard forwarded proxy trust in production.

## Local production-like validation

The GitHub Deployment Validation workflow proves the artifact boundary without making paid model calls. It provisions PostgreSQL+pgvector and TLS Redis locally, builds the production images, runs the migration once, verifies production provider rejection rules, starts the backend/frontend, checks readiness failure and recovery and runs smoke probes.

The standard AgentForge CI additionally runs the complete pytest suite and frontend production build.

## Rollback

Application rollback should use the hosting platform's previous successful release. Database rollback is not automatic: review migrations and recovery procedures before schema changes. Keep a current database backup for paid production databases and understand the provider's free-tier pause/retention limits before using free tiers for anything important.

## Security checklist

- Real production provider credential stored only in the platform secret manager.
- `DATABASE_URL` uses the managed provider's TLS connection settings.
- TLS Redis endpoint configured.
- Exact HTTPS CORS origin.
- Direct API access restricted when an edge proxy is used.
- Trusted forwarded proxy ranges are explicit.
- Request bodies and stream concurrency remain bounded.
- Bearer credentials are not written to logs.
- Health and readiness probes remain outside AI throttling.
- Demo data contains no personal or secret information.
