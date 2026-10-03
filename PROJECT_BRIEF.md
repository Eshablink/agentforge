# AgentForge Project Brief

## Project Summary

AgentForge is a production-style full-stack agentic AI platform intended to demonstrate modern AI application engineering as one coherent product.

The platform is designed to let users upload information, ask grounded questions, retrieve and analyze data with AI-assisted workflows, and receive source-backed responses through a conversational interface.

## Product Objective

The primary objective is to build one integrated application that demonstrates end-to-end AI full-stack engineering, rather than a collection of disconnected demos.

## User Capabilities (Target Scope)

| Group | Count | Capability |
|---|---:|---|
| Document & Knowledge | 1 | Upload documents |
| Document & Knowledge | 2 | Ask questions about uploaded information |
| Document & Knowledge | 3 | Retrieve information using RAG |
| AI Interaction | 4 | Interact with an AI agent |
| AI Interaction | 5 | Allow the agent to dynamically select tools |
| Data & Analysis | 6 | Query structured data |
| Data & Analysis | 7 | Perform Python-based analysis |
| External Intelligence | 8 | Retrieve external information through APIs |
| Visualization | 9 | Generate charts and visualizations |
| Reliability & UX | 10 | Receive source-grounded answers |
| Reliability & UX | 11 | Maintain conversational context |

## Technology Direction

### Frontend

| Group | Count | Technology |
|---|---:|---|
| Frontend | 1 | React |
| Frontend | 2 | TypeScript |
| Frontend | 3 | Vite |

### Backend

| Group | Count | Technology |
|---|---:|---|
| Backend | 1 | Python |
| Backend | 2 | FastAPI |
| Backend | 3 | Pydantic |
| Backend | 4 | REST APIs |

### AI

| Group | Count | Technology |
|---|---:|---|
| AI | 1 | OpenAI API |
| AI | 2 | LangChain |
| AI | 3 | LLM integration |
| AI | 4 | Agentic workflows |
| AI | 5 | Tool calling |
| AI | 6 | RAG |
| AI | 7 | Embeddings |

### Data

| Group | Count | Technology |
|---|---:|---|
| Data | 1 | PostgreSQL |
| Data | 2 | pgvector |

### Planned Agent Tooling

| Group | Count | Tool |
|---|---:|---|
| Agent Tools | 1 | Document search |
| Agent Tools | 2 | SQL and database querying |
| Agent Tools | 3 | Python data analysis |
| Agent Tools | 4 | External web and API retrieval |
| Agent Tools | 5 | Chart generation |

### Engineering & Delivery

| Group | Count | Practice / Tooling |
|---|---:|---|
| Engineering | 1 | Git and GitHub |
| Engineering | 2 | Docker |
| Engineering | 3 | GitHub Actions |
| Engineering | 4 | Cloud deployment |

## Current Implementation vs Planned Scope

### Currently Implemented

| Group | Count | Item | Status Notes |
|---|---:|---|---|
| Repository Foundation | 1 | Repository initialized | Present |
| Repository Foundation | 2 | Engineering and architecture documentation | Present |
| Application Foundation | 3 | FastAPI backend scaffold | Implemented in Phase 1 |
| Application Foundation | 4 | `GET /health` endpoint | Implemented in Phase 1 |
| Application Foundation | 5 | Backend tests for startup and health route | Implemented in Phase 1 |
| Application Foundation | 6 | React + TypeScript + Vite frontend scaffold | Implemented in Phase 1 |
| Application Foundation | 7 | Frontend/backend local environment wiring | Implemented in Phase 1 |

### Planned

| Group | Count | Item | Status Notes |
|---|---:|---|---|
| Data Layer | 1 | PostgreSQL + pgvector integration | Planned (Phase 2) |
| AI Pipeline | 2 | Document ingestion + embeddings + retrieval | Planned |
| AI Pipeline | 3 | LLM response generation | Planned |
| Agent System | 4 | Agent orchestration and tool selection | Planned |
| Agent System | 5 | Tool execution modules (RAG/SQL/Python/Web/Charts) | Planned |
| Product UX | 6 | Source-grounded conversational interface | Planned |
| Product UX | 7 | Conversation context and history | Planned |
| Delivery | 8 | Extended CI/CD and cloud deployment hardening | Planned |

## Non-Goals at Current Completion Level

| Group | Count | Non-Goal |
|---|---:|---|
| Scope Boundaries | 1 | No production RAG pipeline yet |
| Scope Boundaries | 2 | No agent orchestration or dynamic tool-calling runtime yet |
| Scope Boundaries | 3 | No authentication or multi-user conversation history yet |
| Scope Boundaries | 4 | No PostgreSQL/pgvector runtime integration yet |
