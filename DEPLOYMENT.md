# AgentForge deployment runbook

## Current state

AgentForge is production-ready at the application and deployment-definition level, but **no cloud production rollout is claimed by this repository**. The repository contains a Render Blueprint and local Deployment Validation so the operator can perform the rollout with real credentials.

## Recommended first deployment: Render

Render Blueprints can define interconnected services and Postgres in a single render.yaml. The repository's blueprint creates:

- agentforge-api: Dockerized FastAPI service.
- agentforge-web: React static site.
- agentforge-db: PostgreSQL 16 database with pgvector available as a supported extension.

The backend runs Alembic in pre-deploy before serving traffic. Both services use checksPass deploy behavior so the connected deployment can be gated by CI.

### Required secrets

Add these in the agentforge-api service before the first production deploy:

    OPENAI_API_KEY=<real provider credential>
    REDIS_URL=rediss://<tls-redis-endpoint>

Do not commit these values. REDIS_URL must use TLS because production settings reject non-TLS shared Redis.

### First rollout

1. Connect Eshablink/agentforge to a Render project and select the Blueprint.
2. Let Render create the API, static site and Postgres resources.
3. Add the real provider credential and TLS Redis endpoint.
4. Confirm the generated DATABASE_URL and CORS_ORIGINS wiring.
5. Verify the pre-deploy migration completes before the API receives traffic.
6. Check API /health and /ready.
7. Open the frontend and test registration/login.
8. Upload a small non-sensitive document and verify indexed retrieval.
9. Run a tool-assisted prompt and a streaming prompt.
10. Review application logs and request-ID metadata, then add a custom domain only after the generated deployment is stable.

### Custom domains

The Blueprint automatically wires the platform-generated frontend URL into backend CORS and the backend URL into the frontend build. For a custom frontend domain, update CORS_ORIGINS to the exact HTTPS origin before opening the application through that domain.

Review the edge example in deploy/nginx.edge.example.conf if placing another reverse proxy in front of the application. Never configure wildcard forwarded proxy trust in production.

## Local production-like validation

The GitHub Deployment Validation workflow proves the artifact boundary without making paid model calls. It provisions PostgreSQL+pgvector and TLS Redis, builds the production images, runs the migration once, verifies production provider rejection rules, starts the backend/frontend, checks readiness failure and recovery and runs smoke probes.

The standard AgentForge CI additionally runs the complete pytest suite and frontend production build.

## Rollback

Application rollback should use the hosting platform's previous successful release. Database rollback is not automatic: review migrations and recovery procedures before schema changes. Keep a current database backup for paid production databases.

## Security checklist

- Real production provider credential stored only in the platform secret manager.
- TLS Redis endpoint configured.
- Exact HTTPS CORS origin.
- Direct API access restricted when an edge proxy is used.
- Trusted forwarded proxy ranges are explicit.
- Request bodies and stream concurrency remain bounded.
- Bearer credentials are not written to logs.
- Health and readiness probes remain outside AI throttling.
- Demo data contains no personal or secret information.
