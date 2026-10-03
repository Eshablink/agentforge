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
| Repository Foundation | 2 | AGENTS.md engineering instructions | Present |
| Repository Foundation | 3 | Minimal README baseline | Present |
| Application Features | 4 | Runtime application features | Not implemented yet |

### Planned

| Group | Count | Item | Status Notes |
|---|---:|---|---|
| Application Foundation | 1 | FastAPI service foundation | Planned |
| Application Foundation | 2 | React + TypeScript frontend foundation | Planned |
| Data Layer | 3 | PostgreSQL + pgvector integration | Planned |
| AI Pipeline | 4 | Document ingestion + embeddings + retrieval | Planned |
| AI Pipeline | 5 | LLM response generation | Planned |
| Agent System | 6 | Agent orchestration and tool selection | Planned |
| Agent System | 7 | Tool execution modules (RAG/SQL/Python/Web/Charts) | Planned |
| Product UX | 8 | Source-grounded conversational interface | Planned |
| Product UX | 9 | Conversation context and history | Planned |
| Delivery | 10 | Dockerization, CI/CD, and cloud deployment | Planned |

## Non-Goals for the Current Stage

| Group | Count | Non-Goal |
|---|---:|---|
| Current Stage Constraints | 1 | No implementation of FastAPI application features yet |
| Current Stage Constraints | 2 | No implementation of React application features yet |
| Current Stage Constraints | 3 | No implementation of RAG, agents, or tool calling yet |
| Current Stage Constraints | 4 | No installation of new dependencies yet |
