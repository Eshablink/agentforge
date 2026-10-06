# AgentForge project brief

AgentForge is an authenticated full-stack document-RAG and registered-tool agent designed as a portfolio-grade AI engineering system.

## Completed scope

Phases 0–12 are implemented:

- React + TypeScript + Vite product frontend.
- FastAPI backend.
- PostgreSQL + pgvector storage and retrieval.
- PDF/TXT/Markdown ingestion.
- Multi-user ownership isolation.
- Opaque bearer sessions and PBKDF2 password hashing.
- Typed allowlisted tools.
- Multi-turn conversations.
- OpenAI-compatible provider abstraction.
- Native final-answer streaming.
- Safe stream cancellation and bounded output.
- Deterministic offline evaluation.
- Production Docker images.
- Redis shared rate limiting.
- Edge/security reference configuration.
- Deployment validation workflow.
- Premium responsive UI/UX redesign.
- Render deployment definition with migration-before-traffic and CI-gated deployment.

## Product objective

The project should feel like a serious AI product at first glance and withstand an engineering review immediately afterwards.

Frontend quality is part of the architecture contract. The interface must make AI behavior understandable without exposing hidden reasoning, preserve explicit source provenance and make loading, streaming, tool activity, cancellation, errors and insufficient evidence easy to understand.

## Deployment objective

The repository defines a repeatable first cloud target. Actual provisioning requires the owner's account and secrets, so the codebase does not claim a live production deployment until those external prerequisites have been completed and verified.

## Deliberately deferred

SSO/MFA, enterprise identity, broad multilingual retrieval tuning, live LLM-as-judge benchmarking, arbitrary coding agents and automatic database rollback orchestration remain outside the current scope.
