# Phase 12: production experience and deployment

Phase 12 turns the validated application into a portfolio-ready product surface and adds a repeatable cloud deployment definition.

## Frontend experience

The React client now uses a responsive product shell instead of the original utility layout:

- Premium split authentication experience with capability storytelling.
- Persistent conversation sidebar with create/open/delete flows.
- Knowledge-base panel with document upload, status and chunk counts.
- Streaming chat composer with keyboard submit, stop controls and character budget.
- Live agent activity states for retrieval and registered tools.
- Evidence cards that expose filename, chunk index and similarity without exposing hidden reasoning.
- Light/dark theme toggle with local persistence.
- Responsive mobile navigation and touch-sized controls.
- Reduced-motion support and visible focus states.
- Explicit insufficient-evidence UI and a reminder to verify important information.

The frontend remains dependency-light: React, ReactDOM, TypeScript and Vite. No UI framework is required.

## Production deployment definition

render.yaml defines:

- A Dockerized FastAPI web service.
- A Render Postgres database using PostgreSQL 16.
- A static React site served from the global CDN.
- Automatic database migration in the backend service's pre-deploy command.
- checksPass deploy triggers so the linked branch can deploy only after CI checks pass.
- Internal environment wiring for the backend/database and backend/frontend public URLs.
- Static-site security headers and SPA rewrite behavior.
- Explicit production OpenAI provider configuration.
- TLS Redis endpoint supplied as a secret environment variable.

The blueprint intentionally does not contain an API credential. Add the provider credential manually in the Render Dashboard before the first production deploy. The strict production settings also require REDIS_URL to be a rediss:// endpoint; use a TLS-capable Redis-compatible provider rather than weakening the application's production security contract.

## Deployment sequence

1. Connect the repository to Render and create the Blueprint from render.yaml.
2. Provide the required production provider credential and REDIS_URL secret in the agentforge-api service.
3. Confirm the generated database connection is populated and the frontend receives the backend public URL.
4. Let the backend run alembic -c alembic.ini upgrade head before serving traffic.
5. Verify /health, /ready, OpenAPI and frontend availability.
6. Exercise registration, login, document upload, RAG retrieval, tool execution and streaming with non-sensitive demo data.
7. For a custom domain, update CORS and any edge security policy to the real frontend origin before opening the application broadly.

## Boundaries

Phase 12 does not claim that a cloud deployment has already occurred. Cloud provisioning requires the owner's Render account and provider credentials. The repository now contains the infrastructure definition and operator runbook required to perform that deployment without changing application architecture.

SSO/MFA, enterprise identity, automatic rollback orchestration and full external observability vendors remain outside this phase.
