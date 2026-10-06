# AgentForge decisions

Phases 0–8 remain the accepted foundation: PostgreSQL+pgvector, migrations, hashed auth, owner isolation, typed registered tools and bounded resource policies.

## ADR-023 — Native final-answer text deltas

After a structured, validated tool decision, normalize OpenAI-compatible final-answer text deltas. Never expose raw frames or retry after stream consumption. Fake/simulated and completed-answer fallback modes remain explicit. The tool decision itself is not provider-native streamed.

## ADR-024 — Local deployment validation without a cloud rollout

Deployment Validation builds non-root production images, applies Alembic before local serving and probes health, readiness, OpenAPI and frontend behavior. The workflow does not provision or deploy a cloud service.

## ADR-025 — Bounded owner-filtered evidence selection

PostgreSQL applies the owner predicate before a bounded pgvector candidate limit. Deterministic reranking, optional thresholding and normalized duplicate suppression happen within fixed resource bounds. RAG cites only context actually supplied to the provider.

## ADR-026 — Product experience without a heavy UI framework

Phase 12 keeps the frontend dependency-light instead of adding a component library solely for visual polish. Custom CSS and small reusable SVG icons provide the product surface while preserving predictable bundle size, accessibility control and the existing API contract.

The UI is treated as a product boundary: loading, streaming, cancellation, evidence, tool activity, insufficient evidence, errors, responsive navigation and reduced-motion behavior are explicit states.

## ADR-027 — Render Blueprint as a deployment target

Render was selected as the first infrastructure-as-code target because its Blueprint format can define the web service, static site and Postgres resources together, supports pre-deploy commands for migrations and can gate auto-deploys on passing checks.

The blueprint does not store provider credentials. Production application settings continue to require a real OpenAI-compatible key and a TLS Redis endpoint. This preserves the application's fail-closed security contract rather than weakening it for a particular platform.

## ADR-028 — Platform-provided HTTP port

The backend entrypoint reads PORT from the runtime environment with an 8000 default for local development. This keeps local behavior stable while allowing hosted platforms to choose their service port without changing the image.
