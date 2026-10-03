# AgentForge Project Brief

## Project Summary

AgentForge is a full-stack document question-answering application. Its completed Phase 0–3 vertical slice lets users upload supported documents, persist document chunks and embeddings in PostgreSQL/pgvector, retrieve relevant context, and produce grounded answers with source references through a minimal web interface.

## Project Status

| Group | Count | Phase / capability | Status |
|---|---:|---|---|
| Complete | 1 | Phase 0 — Repository setup and blueprint | Complete |
| Complete | 2 | Phase 1 — FastAPI and React application foundation | Complete; merged |
| Complete | 3 | Phase 2 — PostgreSQL + pgvector, SQLAlchemy 2.x, Alembic | Implemented and verified |
| Complete | 4 | Phase 3 — Ingestion, retrieval, grounded RAG, sources, minimal UI | Implemented and verified |
| Deferred | 5 | Agent orchestration and tool calling | Not implemented |
| Deferred | 6 | Authentication, authorization, multi-tenancy, complex conversation history, billing, deployment | Not implemented |

## Implemented and Verified Capabilities

| Group | Count | Capability | Details |
|---|---:|---|---|
| Application | 1 | FastAPI + React/TypeScript/Vite | Health, document and chat APIs with minimal RAG UI |
| Database | 2 | PostgreSQL + pgvector | SQLAlchemy 2.x models/sessions and Alembic schema migration |
| Ingestion | 3 | PDF, TXT, Markdown | Validation, extraction, deterministic chunking, embedding abstraction, transactional persistence |
| Retrieval | 4 | Vector search | pgvector cosine distance, bounded `top_k`, source document/chunk provenance |
| RAG | 5 | Grounded answers | Retrieved context, provider abstraction, insufficient-evidence handling, citations |
| Verification | 6 | GitHub Actions | PostgreSQL + pgvector service; migration, import smoke test, backend pytest, frontend production build |

## Verification Record

Post-merge GitHub Actions run [37117875205](https://github.com/Eshablink/agentforge/actions/runs/37117875205) passed for merge commit `67e983772257dc575475e86ebecbe6548c968eb9`. Documentation cleanup merge commit `cded4a9bf39d267200f1de072600d1648b19182f` also passed in run [37119471555](https://github.com/Eshablink/agentforge/actions/runs/37119471555). Both runs validate the PostgreSQL/pgvector-backed Phase 0–3 baseline. These are historical results; later application changes require fresh verification.

## Technology Direction

| Group | Count | Technology | Current status |
|---|---:|---|---|
| Frontend | 1 | React, TypeScript, Vite | Implemented |
| Backend | 2 | Python, FastAPI, Pydantic, SQLAlchemy 2.x | Implemented |
| Data | 3 | PostgreSQL, pgvector, Alembic | Implemented |
| AI | 4 | Embedding and LLM provider abstractions | Implemented; fake providers support deterministic tests |
| Future | 5 | Agents and tool execution | Deferred; not present in Phases 0–3 |

## Explicit Scope Boundaries

Autonomous or multi-agent workflows, dynamic tool calling, SQL/Python/web/chart tools, authentication, authorization, conversation memory, multi-tenancy, billing, and production deployment are **not implemented**. Keep deferred work separate from the shipped Phase 0–3 scope.

Tests use PostgreSQL + pgvector and deterministic fake providers; they do not require paid API credentials or substitute SQLite for database integration tests.
