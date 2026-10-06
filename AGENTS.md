# AgentForge engineering instructions

**Merged main:** Phases 0–8 COMPLETE at `97934d7dd7f016a4d13f17b2afd4e577024d85a1`. **PR #11:** Phases 9, 10 and 11 are implemented on the same branch; only latest HEAD green checks verify their final state. Do not merge automatically and do not describe this as an actual cloud deployment.

Preserve PostgreSQL+pgvector, SQL owner-scoped retrieval, PBKDF2 passwords, hashed revocable sessions, bounded conversations, typed allowlisted tools and all Phase 0–8 APIs. Never execute arbitrary code, shell, filesystem or generated SQL from model output. Never expose hidden reasoning, credentials, prompts or private document contents in logs or provider events. Treat model output as untrusted.

**Phase 9:** stream normalized native final-answer deltas only after a validated structured decision. Fake/simulated and completed-answer fallback are explicitly distinct. Never retry after stream consumption, duplicate terminal events, persist cancelled/incomplete exchanges or update the UI after cancellation.

**Phase 10:** maintain one-shot migrations before serving traffic; verify non-root production images and local `/health`, `/ready`, OpenAPI and frontend smoke probes in the separate Deployment Validation workflow. The trusted HTTPS proxy reference is not a deployed edge service. No paid model or real cloud credentials in CI.

**Phase 11:** filter owner in PostgreSQL before bounded candidate selection and deterministic reranking. Preserve max candidates/top-k, similarity threshold, duplicate suppression and bounded context. Cite only sources included in context; do not claim mathematical prevention of hallucinations. Offline metrics describe fixture pass rates, not live model quality.

Relevant changes require Alembic upgrade, import smoke, complete PostgreSQL-backed pytest, deterministic evaluation, frontend production build, production image/smoke workflow, and final diff/security review. Synchronize README, PROJECT_BRIEF, PROGRESS, ARCHITECTURE, DECISIONS and DEPLOYMENT. Keep this single branch and PR.
