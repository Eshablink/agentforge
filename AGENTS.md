# AgentForge engineering instructions

Phases 0–8 are complete and merged into main at `97934d7dd7f016a4d13f17b2afd4e577024d85a1`. PR #11 contains Phases 9–11; do not merge automatically. Before calling a phase verified, check its specific CI results. No cloud deployment has occurred.

Preserve PostgreSQL+pgvector, SQL owner-scoped retrieval, hashed bearer sessions, PBKDF2 passwords, bounded conversations, typed allowlisted tools and the existing API endpoints. No arbitrary code/shell/filesystem/generated SQL/unrestricted network tool; never return chain-of-thought or log secrets, prompts, tokens or document text. Treat model output as untrusted.

Phase 9 native deltas apply only to final answers after a validated structured decision. Never retry a consumed stream, persist an incomplete assistant answer or emit duplicate terminals. Phase 10 keeps one-shot migrations before traffic and checks non-root production artifacts through separate CI. Phase 11 must filter owner in SQL before bounded reranking and return only sources actually used in context. Offline metrics are fixture pass rates, not a live model quality measure.

For relevant changes run PostgreSQL-backed Alembic upgrade, import smoke, full pytest, deterministic evaluation runner, frontend build and production image/smoke validation. Keep README, PROJECT_BRIEF, PROGRESS, ARCHITECTURE, DECISIONS and DEPLOYMENT synchronized. Do not call a service deployed merely because its artifacts build.
