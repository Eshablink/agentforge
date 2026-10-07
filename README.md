# ⚒️ AgentForge

[![CI](https://github.com/Eshablink/agentforge/actions/workflows/ci.yml/badge.svg)](https://github.com/Eshablink/agentforge/actions/workflows/ci.yml)
[![Security](https://github.com/Eshablink/agentforge/actions/workflows/security.yml/badge.svg)](https://github.com/Eshablink/agentforge/actions/workflows/security.yml)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-009688.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-%2B%20pgvector-4169E1.svg)](https://www.postgresql.org/)

> **A production-oriented full-stack agentic AI workspace for grounded answers, validated tools, durable memory, and live streaming.**

AgentForge is an end-to-end AI engineering project built around a simple idea: **agentic behavior should be useful, inspectable, constrained, and deployable**.

It combines a React + TypeScript frontend with a FastAPI backend, PostgreSQL + pgvector retrieval, authenticated multi-user conversations, typed allowlisted tools, OpenAI-compatible providers, Server-Sent Events, deterministic offline evaluation, and production-focused security controls.

> **Important:** AgentForge is currently a **full-stack application/workspace**, not a published Python SDK. The README therefore documents the real product architecture and API rather than inventing a library interface.

---

## 🎯 Founding problem

AgentForge is part of a broader direction toward an **AI employee / autonomous company operator**: turning company requests into completed work across information sources, procedures, permitted actions, and verification.

The full founding problem statement is documented in [PROBLEM_STATEMENT.md](PROBLEM_STATEMENT.md). The current implementation deliberately represents a bounded foundation rather than claiming the broader autonomous surface is already complete.

## ✨ Why AgentForge stands out

| Capability | What it demonstrates |
| --- | --- |
| 🤖 **Agent orchestration** | Explicit structured decisions, bounded steps, validated tool calls |
| 🧰 **Safe tools** | Typed, registered, allowlisted operations instead of arbitrary execution |
| 📚 **Grounded RAG** | PostgreSQL/pgvector retrieval, owner-first filtering, reranking and deduplication |
| 🧠 **Durable conversations** | Authenticated, owner-scoped conversation and message persistence |
| ⚡ **Live streaming** | Normalized provider deltas delivered through SSE with cancellation-safe handling |
| 🔐 **Production security** | PBKDF2-SHA256 password hashing, opaque sessions, fail-closed production config |
| 🧪 **Engineering discipline** | pytest, deterministic evaluation, CI, deployment validation, CodeQL and Dependabot |
| 🎨 **Product UX** | Responsive workspace, evidence cards, activity states, themes, accessibility-minded interactions |

---

## 🧩 Product surface

AgentForge is designed as an **AI workspace**, not a single chat screen.

### Workspace
- Persistent conversation sidebar
- Create, open, and delete conversations
- Authenticated multi-user isolation
- Streaming composer with stop/cancellation controls
- Keyboard-first interactions
- Light and dark themes
- Responsive mobile navigation

### Knowledge
- PDF, TXT, and Markdown ingestion
- Deterministic chunking
- PostgreSQL + pgvector storage
- Bounded candidate retrieval
- Owner-aware reranking and deduplication
- Evidence cards with filename, chunk, and similarity metadata
- Explicit insufficient-evidence states

### Agent execution
- Structured agent decisions
- Typed and allowlisted tools
- Bounded agent steps and tool calls
- Date-offset and Decimal calculation tools
- Retrieval-backed answers
- Provider abstraction for OpenAI-compatible LLMs and embeddings

---

## 🏗️ Architecture

~~~mermaid
flowchart LR
    U[User] --> FE[React + TypeScript + Vite]
    FE -->|HTTPS / REST / SSE| API[FastAPI API]

    API --> AUTH[Auth + Opaque Sessions]
    API --> CHAT[Conversations + Memory]
    API --> AGENT[Agent Orchestrator]
    API --> INGEST[Document Ingestion]
    API --> LIMIT[Shared Rate Limiter]

    INGEST --> PG[(PostgreSQL)]
    AGENT --> RETRIEVE[RAG Retrieval]
    RETRIEVE --> PG
    PG --> VEC[(pgvector)]

    AGENT --> TOOLS[Typed Allowlisted Tools]
    AGENT --> LLM[OpenAI-compatible LLM]
    AGENT --> EMB[Embedding Provider]

    LIMIT --> REDIS[(Redis / Key Value)]

    LLM --> STREAM[SSE Stream]
    STREAM --> FE
~~~

### Request lifecycle

~~~mermaid
sequenceDiagram
    participant User
    participant UI
    participant API
    participant Agent
    participant Tools
    participant RAG
    participant Provider

    User->>UI: Submit prompt
    UI->>API: Authenticated request
    API->>Agent: Bounded task
    Agent->>RAG: Search when evidence is needed
    RAG-->>Agent: Owner-scoped evidence
    Agent->>Tools: Execute validated tool (when needed)
    Tools-->>Agent: Tool result
    Agent->>Provider: Generate final answer
    Provider-->>API: Final-answer deltas
    API-->>UI: SSE events
    UI-->>User: Streamed response + evidence
~~~

**Design rule:** raw provider frames and hidden reasoning are never exposed through the product UI.

---

## 🔁 AI workflow

1. The user submits a bounded prompt.
2. AgentForge resolves an explicit structured decision.
3. The agent may retrieve document evidence and/or execute an allowlisted tool.
4. Retrieval stays owner-scoped and candidate-bounded.
5. Evidence is deterministically reranked and deduplicated.
6. RAG context is capped before provider execution.
7. Final-answer provider deltas are normalized into SSE events.
8. The completed owned exchange is persisted.

This keeps the system **deterministic where it should be, model-driven where it is useful, and constrained where it is risky**.

---

## 🛠️ Technology stack

**Frontend**
- React 18
- TypeScript
- Vite
- Custom responsive CSS

**Backend**
- Python 3.11+
- FastAPI
- SQLAlchemy
- Alembic
- Uvicorn

**Data**
- PostgreSQL
- pgvector
- Redis-compatible shared rate limiting

**AI**
- OpenAI-compatible chat providers
- OpenAI-compatible embedding providers
- Structured agent decisions
- Retrieval-augmented generation

**Platform**
- REST + Server-Sent Events
- Docker
- Render deployment
- Supabase PostgreSQL
- GitHub Actions

**Quality & security**
- pytest
- Deterministic offline evaluation
- CodeQL
- Dependabot
- Production configuration validation

---

## 🚀 Quick start

### Prerequisites

- Docker + Docker Compose
- Git
- Python 3.11+ for backend-only development
- Node.js + npm for frontend-only development

### Run the full local stack

~~~bash
git clone https://github.com/Eshablink/agentforge.git
cd agentforge

cp .env.example .env

docker compose up --build
~~~

The local stack is intended for development. Production configuration deliberately rejects fake providers, development database credentials, wildcard CORS, and non-TLS shared Redis.

### Run the backend locally

~~~bash
cd backend
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows
# .venv\\Scripts\\activate

pip install -r requirements.txt
python serve.py
~~~

### Run the frontend locally

~~~bash
cd frontend
npm ci
npm run dev
~~~

---

## 🔌 API surface

The backend exposes a FastAPI application with:

- Health/readiness probes
- Authentication and opaque sessions
- Conversation management
- Document ingestion
- Retrieval-backed agent chat
- Streaming responses over SSE
- Request-ID telemetry

The exact routes and contracts live in the backend source and are covered by the automated tests.

---

## 🧪 Verification

Run the backend tests:

~~~bash
cd backend
pytest
~~~

The repository CI validates:

- PostgreSQL + pgvector migration behavior
- Backend import smoke tests
- Full backend pytest coverage
- Deterministic evaluation fixtures
- TypeScript/Vite production build
- Production image and non-root runtime checks

Deployment Validation additionally exercises:

- Managed-Postgres URL compatibility
- Migration-before-traffic behavior
- Production configuration boundaries
- Redis TLS readiness and fail-closed behavior
- Health/readiness and application smoke probes
- Nginx syntax validation

**No paid model calls are required by CI.**

---

## ☁️ Deployment architecture

The production path keeps the application host stateless and moves durable/shared infrastructure into managed services:

~~~text
Render
├── agentforge-web     → React static site
└── agentforge-api     → FastAPI Docker service
        │
        ├── Supabase PostgreSQL + pgvector
        └── Render Key Value / TLS Redis
                 │
                 └── OpenAI-compatible providers
~~~

The Render Blueprint intentionally does **not** create a second application database. This keeps durable data independent from the API host and makes the infrastructure replaceable.

Production secrets such as **DATABASE_URL**, **REDIS_URL**, and **OPENAI_API_KEY** belong in the platform secret manager, not in Git.

See:
- [DEPLOYMENT.md](DEPLOYMENT.md)
- [docs/PHASE13.md](docs/PHASE13.md)
- [docs/PHASE14.md](docs/PHASE14.md)
- [SECURITY.md](SECURITY.md)

---

## 📈 Engineering milestones

| Phase | Status | Outcome |
| --- | --- | --- |
| 0 | ✅ Complete | Engineering contract and architecture |
| 1 | ✅ Complete | FastAPI + React foundation |
| 2–3 | ✅ Complete | PostgreSQL + pgvector RAG and ingestion |
| 4–6 | ✅ Complete | Agent tools, conversations, auth and tenant isolation |
| 7 | ✅ Complete | Streaming, request IDs and deterministic evaluation |
| 8 | ✅ Complete | Production configuration and shared rate limiting |
| 9–11 | ✅ Complete | Native streaming and advanced bounded RAG quality |
| 12 | ✅ Complete | Product UI/UX overhaul |
| 13 | ✅ Complete | Low-cost managed deployment path |
| 14 | ✅ Complete | CodeQL, Dependabot and repository security policy |
| 15 | 🚧 In progress | Production cloud launch and live validation |

---

## 🔐 Security boundaries

AgentForge intentionally does **not** provide:

- Arbitrary shell execution
- Arbitrary Python execution
- Unrestricted SQL generation
- Unrestricted filesystem automation
- Unrestricted outbound network access
- Hidden chain-of-thought exposure

The system is designed to expose **useful activity and evidence**, without exposing private model reasoning.

---

## 🗺️ Repository map

~~~text
agentforge/
├── backend/                    # FastAPI application
├── frontend/                   # React + TypeScript client
├── evaluation/                 # Deterministic offline evaluation
├── deploy/                     # Deployment checks and edge configuration
├── docs/                       # Phase-specific engineering notes
├── .github/workflows/          # CI, deployment validation and security
├── render.yaml                 # Render infrastructure definition
├── Dockerfile                  # Render-compatible API image entrypoint
├── AGENTS.md                   # Permanent engineering contract
├── ARCHITECTURE.md             # System architecture
├── DECISIONS.md                # Accepted design decisions
├── PROGRESS.md                 # Milestone status
└── SECURITY.md                 # Security policy
~~~

---

## 🤝 Contributing

Contributions, issues, and improvement ideas are welcome.

Before opening a pull request:

~~~bash
# backend
cd backend
pytest

# frontend
cd frontend
npm ci
npm run build
~~~

Please keep changes aligned with the engineering contract in [AGENTS.md](AGENTS.md).

---

## 📜 License

See the repository's license file for the authoritative licensing terms.

---

<div align="center">

**AgentForge** · Build agents that are grounded, constrained, observable, and deployable.

</div>
