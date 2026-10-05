# AgentForge Project Brief

AgentForge is an authenticated full-stack document-RAG and registered-tool agent. Phases 0–7 are **complete on main**. Phase 7 PR #9 was **merged** at `63d7d3f0d417d06b2e57fa63874824de4306450d`, and main CI run 37320957004 passed. Its SSE transport provides bounded incremental chunks of completed generated text, not provider-native token streaming. Its deterministic RAG/tool/agent suite is not a general model-quality benchmark.

Phase 8, on `feat/agentforge-phase-8`, provides production deployment and operational hardening: production-only explicit config, managed PostgreSQL + pgvector, one-shot Alembic migration, cheap liveness and dependency readiness, shared Redis fixed-window rate limiting with fail-closed behavior, auth attempt throttling, bounded ingestion and session cleanup, correct browser API origin, and vendor-neutral deployment guidance. This repository does not claim a live deployment.

The security model remains unchanged: salted PBKDF2-SHA256 passwords, hashed opaque bearer tokens, expiry and revocation, owned conversations and documents, owner-filtered retrieval, validated registered tools, no arbitrary code/shell/filesystem/SQL/network execution, and no hidden reasoning or credential logging.

To run locally use `.env.example` and `docker compose up --build` (development-only credentials and local one-shot migration). For production configure environment/secret injection and follow [DEPLOYMENT.md](DEPLOYMENT.md). The mandatory production limiter needs a provisioned Redis-compatible service; use a proxy for HTTPS, trusted forwarding, SSE buffering and edge/IP auth protection. SSO/MFA, cloud automation and native provider token streaming remain deferred.
