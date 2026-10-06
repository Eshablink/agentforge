# AgentForge architecture

AgentForge is an authenticated full-stack document-RAG and registered-tool agent with a React product UI, FastAPI API layer, PostgreSQL+pgvector retrieval, shared Redis rate limiting and OpenAI-compatible model providers.

## Runtime flow

    Browser
      |
      | HTTPS
      v
    Edge / platform proxy
      |
      v
    React + TypeScript + Vite
      |
      | REST + SSE
      v
    FastAPI
      |
      +--> Authentication + opaque sessions
      +--> Conversations + messages
      +--> Document ingestion
      +--> Agent orchestration
      +--> Registered tools
      +--> RAG retrieval
      +--> Stream lifecycle + telemetry
      |
      +------------+-------------+
      |            |             |
      v            v             v
    PostgreSQL   Redis       OpenAI-compatible
    + pgvector   limiter     LLM + embeddings

## Frontend architecture

The frontend intentionally stays dependency-light. React components consume a typed API client and render the authenticated workspace, conversation history, document knowledge base, source provenance and live stream state.

The UI separates:

- Authentication and product positioning.
- Conversation navigation.
- Knowledge-base management.
- Streaming answer rendering.
- Evidence and activity presentation.
- Error and insufficient-evidence states.
- Theme and responsive navigation.

The stream UI exposes normalized lifecycle events only. It never renders raw provider frames or hidden reasoning.

## Retrieval and agent boundaries

Document retrieval applies the owner predicate in SQL before the bounded vector candidate limit. Candidate results receive deterministic relevance scoring, optional thresholding and normalized duplicate suppression. RAG context is capped before provider execution and source references contain only evidence actually included in that context.

Agent execution uses typed allowlisted tools with bounded calls and steps. Arbitrary shell, Python, unrestricted SQL, filesystem operations and unrestricted network access remain outside the platform.

## Production path

Phase 12 adds Render infrastructure-as-code as an operator-friendly deployment target:

- Dockerized API service with platform-provided PORT support.
- Managed PostgreSQL with pgvector.
- React static site with CDN delivery.
- Pre-deploy migration.
- CI-gated deploy trigger.
- Service-to-service public URL wiring.
- Static security headers.

The application still preserves its provider abstraction so a different cloud or compatible OpenAI endpoint can be substituted without changing the product architecture.

## Operational contracts

/health is a cheap liveness endpoint with no database or provider dependency.

/ready validates serving dependencies and fails closed when the production shared limiter is unavailable.

SSE streaming owns a single request-level start, a single terminal event and bounded output. A complete owned exchange is persisted only after successful completion.

Request IDs correlate safe lifecycle telemetry. Telemetry does not contain answer text, raw provider frames or hidden reasoning.

## Remaining limits

The Render Blueprint is a deployment definition, not proof of a completed cloud rollout. Real credentials, DNS/custom domains, TLS Redis and operator verification are required. Enterprise SSO/MFA, broad live quality benchmarking and automatic rollback orchestration remain deferred.
