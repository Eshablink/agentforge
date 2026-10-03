# AgentForge Project Brief

## Project Summary

AgentForge is a full-stack AI application for document ingestion and source-grounded question answering. Its current verified vertical slice lets users upload documents, persist chunks and embeddings in PostgreSQL/pgvector, retrieve relevant context, and return grounded answers with source references.

## Product Objective

Build an integrated AI full-stack application through incremental, independently verified phases. Long-term product ideas below are goals, not claims about current implementation.

## User Capabilities — Target Scope

| Group | Count | Capability | Current state |
|---|---:|---|---|
| Document & Knowledge | 1 | Upload PDF, TXT, and Markdown documents | Implemented |
| Document & Knowledge | 2 | Ask questions over uploaded information | Implemented with RAG pipeline |
| Document & Knowledge | 3 | Retrieve information using vector search | Implemented with PostgreSQL + pgvector |
| AI Interaction | 4 | Interact with an autonomous AI agent | Planned; Phase 4+ |
| AI Interaction | 5 | Allow an agent to dynamically select tools | Planned; Phase 4+ |
| Data & Analysis | 6 | Query structured data | Planned |
| Data & Analysis | 7 | Perform Python-based analysis | Planned |
| External Intelligence | 8 | Retrieve external information through APIs | Planned |
| Visualization | 9 | Generate charts and visualizations | Planned |
| Reliability & UX | 10 | Receive source-grounded answers | Implemented in the RAG vertical slice |
| Reliability & UX | 11 | Maintain conversational context | Not implemented |

## Technology Direction

| Group | Count | Technology | State |
|---|---:|---|---|
| Frontend | 1 | React | Implemented |
| Frontend | 2 | TypeScript | Implemented |
| Frontend | 3 | Vite | Implemented |
| Backend | 4 | Python + FastAPI | Implemented |
| Backend | 5 | Pydantic settings and schemas | Implemented |
| Data | 6 | PostgreSQL | Implemented |
| Data | 7 | pgvector | Implemented |
| AI | 8 | Embedding and LLM provider abstractions | Implemented; fake providers used in automated tests |
| AI | 9 | LangChain/agent workflows/tool calling | Not implemented in Phases 0–3 |

## Implemented Through Phase 3

| Group | Count | Capability |
|---|---:|---|
| Foundation | 1 | Repository and engineering documentation |
| Foundation | 2 | FastAPI app and `GET /health` |
| Foundation | 3 | React/TypeScript/Vite frontend |
| Database | 4 | SQLAlchemy 2.x models, PostgreSQL sessions, Alembic migration, pgvector extension |
| Ingestion | 5 | PDF/TXT/Markdown extraction, type/size validation, deterministic chunking, embeddings, transactional persistence |
| Retrieval/RAG | 6 | Bounded `top_k`, pgvector cosine retrieval, context-grounded answer abstraction, source references |
| UX/CI | 7 | Minimal upload/list/chat frontend vertical slice |
| UX/CI | 8 | GitHub Actions for PostgreSQL + pgvector migration, backend tests/import smoke test, and frontend build |

## Planned Beyond Phase 3

| Group | Count | Item |
|---|---:|---|
| Agent System | 1 | Agent orchestration and tool selection |
| Agent System | 2 | Tool execution modules (SQL/Python/Web/Charts) |
| Product UX | 3 | Conversation context and persistent history |
| Delivery | 4 | Deployment and production hardening |

## Scope Boundaries at Phase 3

No autonomous agent workflows, dynamic tool calling, authentication/authorization, multi-tenant support, conversation memory, or production deployment are implemented. These require separate designs, safeguards, tests, and explicit phase scope.

## Verification Reference

Phase 2+3 passed GitHub Actions after merge. The post-merge `main` workflow run is recorded in `PROGRESS.md`; CI uses PostgreSQL + pgvector, runs Alembic and backend tests, checks the application import, and builds the frontend.
