# AgentForge progress

**Merged baseline:** Phases 0–8 are complete on main at `97934d7dd7f016a4d13f17b2afd4e577024d85a1` (Phase 8 PR #10). Phases 9, 10 and 11 are implemented and phase-specifically verified on the existing PR #11 branch. They are **not merged or deployed**; final merge remains a human decision.

## Phase acceptance gates

| Phase | Branch implementation | Verification |
|---|---|---|
| 9 — Native AI streaming | OpenAI-compatible final-answer deltas, deterministic fake and bounded fallback; one terminal event, cancellation-safe frontend | Offline provider-frame and lifecycle tests; full backend/frontend CI passed on the Phase 9 head |
| 10 — Deployment automation and edge security | Non-root static image, trusted proxy example, migration-before-traffic validation and safe smoke probes | Deployment Validation run 37430440521 and AgentForge CI run 37430440494 passed at `84ce290b1544bd50cae17b62d6fd0998304aad41` |
| 11 — Advanced RAG + AI quality | SQL owner filtering precedes at-most-40 candidate selection; deterministic relevance/duplicate filtering; bounded context and accurate included-source references | AgentForge CI run 37432213090 and Deployment Validation run 37432213091 passed at `d9eb42eada094bb3fe639288a29e155b3a0667e4`, including owner query-shape fixtures and PostgreSQL owner-isolation tests |

The current branch documentation may advance the HEAD past those runs. **Only checks for the final PR head verify the final artifact.** CI applies Alembic, smoke-imports the app, runs full PostgreSQL-backed pytest and deterministic evaluation, and builds the frontend. Deployment Validation builds both production images and probes local `/health`, `/ready`, API availability and frontend health without paid calls or real cloud credentials.

## Evaluation and limits

The runner reports deterministic fixture pass rates for RAG, tool, agent and stream groups; these metrics are **not** live retrieval accuracy, external-model factuality, or human judgments. The owner-scope fixture compiles a bounded SQL predicate; PostgreSQL integration tests independently verify cross-user isolation. Context provenance does not guarantee every generated claim is true. No production environment has been deployed. Redis, managed PostgreSQL and TLS must be supplied by an operator; SSO/MFA and cloud-account automation remain deferred.
