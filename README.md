# AgentForge

Production-style full-stack agentic AI platform for source-grounded conversational intelligence.

## Current Status

| Group | Count | Item | Status |
|---|---:|---|---|
| Project Status | 1 | Phase 0 — Repository Setup | Complete |
| Project Status | 2 | Phase 1 — Application Foundation | Complete |
| Project Status | 3 | Advanced AI capabilities (RAG/agents/tool-calling) | Planned |

## Implemented in Phase 1

| Group | Count | Capability |
|---|---:|---|
| Backend Foundation | 1 | FastAPI application scaffold under `backend/app` |
| Backend Foundation | 2 | `GET /health` endpoint |
| Backend Foundation | 3 | Backend test suite for startup and health response |
| Frontend Foundation | 4 | React + TypeScript + Vite scaffold under `frontend/` |
| Frontend Foundation | 5 | Frontend API base URL configuration via `VITE_API_BASE_URL` |
| Project Setup | 6 | Root `.env.example` and Docker Compose wiring for frontend/backend |
| Project Setup | 7 | Container build files for backend and frontend |

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

## Technology Stack

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

### AI & Data (Planned beyond Phase 1)

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

## Local Setup

### 1) Environment

```bash
cp .env.example .env
```

### 2) Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend URL: `http://localhost:8000`
Health endpoint: `http://localhost:8000/health`

### 3) Backend tests

```bash
cd backend
pytest
```

### 4) Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend URL: `http://localhost:5173`

### 5) Frontend build

```bash
cd frontend
npm run build
```

### 6) Docker Compose

```bash
docker compose up --build
```

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

See `ARCHITECTURE.md` for detailed boundaries and layer responsibilities.

## Development Roadmap

| Group | Count | Phase | Status |
|---|---:|---|---|
| Roadmap | 0 | Phase 0 — Repository Setup | COMPLETE |
| Roadmap | 1 | Phase 1 — Application Foundation | COMPLETE |
| Roadmap | 2 | Phase 2 — PostgreSQL + pgvector | NEXT |
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
