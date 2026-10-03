# AgentForge

Production-style full-stack agentic AI platform for source-grounded conversational intelligence.

## Current Status

| Group | Count | Item | Status |
|---|---:|---|---|
| Project Status | 1 | Repository setup and foundational documentation | Complete |
| Project Status | 2 | Application runtime features | Planned |

## Planned Capabilities

| Group | Count | Capability |
|---|---:|---|
| Knowledge Workflows | 1 | Document upload and ingestion |
| Knowledge Workflows | 2 | Q&A over uploaded information |
| Knowledge Workflows | 3 | Retrieval-Augmented Generation (RAG) |
| Agentic AI | 4 | AI agent interaction with conversational context |
| Agentic AI | 5 | Dynamic tool selection and execution |
| Data Access | 6 | Structured SQL/database querying |
| Analytics | 7 | Python-based analysis workflows |
| Integrations | 8 | External web/API data retrieval |
| Visualization | 9 | Chart and visualization generation |
| Response Quality | 10 | Source-grounded answer synthesis |

## Technology Stack (Direction)

### Frontend

| Group | Count | Stack Item |
|---|---:|---|
| Frontend | 1 | React |
| Frontend | 2 | TypeScript |
| Frontend | 3 | Vite |

### Backend

| Group | Count | Stack Item |
|---|---:|---|
| Backend | 1 | Python |
| Backend | 2 | FastAPI |
| Backend | 3 | Pydantic |
| Backend | 4 | REST APIs |

### AI & Data

| Group | Count | Stack Item |
|---|---:|---|
| AI | 1 | OpenAI API |
| AI | 2 | LangChain |
| AI | 3 | Agentic workflows and tool calling |
| AI | 4 | RAG and embeddings |
| Data | 5 | PostgreSQL |
| Data | 6 | pgvector |

### Delivery & Operations

| Group | Count | Stack Item |
|---|---:|---|
| DevOps | 1 | Docker |
| DevOps | 2 | GitHub Actions |
| DevOps | 3 | Cloud deployment |

## High-Level Architecture

```text
React + TypeScript
        ↓
FastAPI REST API
        ↓
Application / Service Layer
        ↓
Agent Orchestration
        ↓
LLM + Tool Selection
        ↓
RAG / SQL / Python / Web APIs / Charts
        ↓
PostgreSQL + pgvector + External APIs
        ↓
Source-grounded Response to React UI
```

See `ARCHITECTURE.md` for full layer responsibilities and boundaries.

## Development Roadmap

| Group | Count | Phase | Status |
|---|---:|---|---|
| Roadmap | 0 | Phase 0 — Repository Setup | COMPLETE |
| Roadmap | 1 | Phase 1 — Application Foundation | NEXT |
| Roadmap | 2 | Phase 2 — PostgreSQL + pgvector | PLANNED |
| Roadmap | 3 | Phase 3 — Document Ingestion | PLANNED |
| Roadmap | 4 | Phase 4 — RAG Pipeline | PLANNED |
| Roadmap | 5 | Phase 5 — LLM Integration | PLANNED |
| Roadmap | 6 | Phase 6 — Agent Orchestration | PLANNED |
| Roadmap | 7 | Phase 7 — Tool Calling | PLANNED |
| Roadmap | 8 | Phase 8 — Analytics + Chart Tools | PLANNED |
| Roadmap | 9 | Phase 9 — React AI Interface | PLANNED |
| Roadmap | 10 | Phase 10 — Authentication + Conversation History | PLANNED |
| Roadmap | 11 | Phase 11 — Dockerization | PLANNED |
| Roadmap | 12 | Phase 12 — Testing + CI/CD | PLANNED |
| Roadmap | 13 | Phase 13 — Cloud Deployment | PLANNED |
| Roadmap | 14 | Phase 14 — Production Polish | PLANNED |

For execution detail, track `PROGRESS.md` and `DECISIONS.md`.
