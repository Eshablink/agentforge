# AgentForge project brief

AgentForge is a full-stack authenticated document-RAG and safe-tool agent. **Phases 0–8 are complete and merged** into main at `97934d7dd7f016a4d13f17b2afd4e577024d85a1`. PR #11 contains the three separately tracked next phases on `feat/agentforge-phases-9-11`:

| Phase | Implementation | Verification boundary |
|---|---|---|
| 9 — Native AI streaming | OpenAI-compatible final-answer deltas, deterministic fake and completed-answer fallback, bounded lifecycle | Provider stream and regression tests; no paid CI |
| 10 — Deployment automation and edge security | Production image builds, validation workflow, safe probes and edge reference config | GitHub deployment validation builds and probes locally; no real cloud rollout |
| 11 — Advanced RAG and AI quality | Owner-filtered bounded candidate reranking, context/source bounds, offline quality cases | PostgreSQL ownership regressions and deterministic case pass rates |

Only Phase 8 and earlier are merged; Phases 9–11 become CI-verified on this branch when both workflows are green on its final HEAD. The evaluation uses fake providers and deterministic fixtures, not a live LLM as judge. Source references represent context provenance, not an external factual guarantee. Stable auth, hashed sessions, allowlisted typed tools and owner isolation remain required; no real deployment, SSO/MFA or cloud automation is claimed.
