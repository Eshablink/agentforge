# AgentForge Architecture

## Architecture Goal

AgentForge is intended to be a small, production-style full-stack AI system with clear boundaries between UI, API, orchestration, tools, and data layers.

## Conceptual Flow

```text
React + TypeScript
        ↓
FastAPI REST API
        ↓
Application / Service Layer
        ↓
Agent Orchestration
        ↓
LLM
        ↓
Tool Selection
   ┌────┼────┬────┬────┐
   ↓    ↓    ↓    ↓    ↓
 RAG   SQL  Python Web  Charts
   ↓    ↓    ↓    ↓    ↓
pgvector PostgreSQL External APIs
        ↓
    Final Response
        ↓
React UI
```

## Layer Responsibilities

### 1) React + TypeScript Frontend

| Group | Count | Responsibility |
|---|---:|---|
| Frontend | 1 | Provide user interface for chat, uploads, and result exploration |
| Frontend | 2 | Send typed API requests to backend REST endpoints |
| Frontend | 3 | Render responses, citations/sources, and visual outputs |
| Frontend | 4 | Manage local UI state and request lifecycle |

### 2) FastAPI REST API

| Group | Count | Responsibility |
|---|---:|---|
| API Layer | 1 | Expose stable HTTP endpoints for frontend |
| API Layer | 2 | Validate request/response contracts with Pydantic schemas |
| API Layer | 3 | Route requests into application services |
| API Layer | 4 | Enforce API-level auth, rate-limits, and error mapping (future) |

### 3) Application / Service Layer

| Group | Count | Responsibility |
|---|---:|---|
| Service Layer | 1 | Implement business workflows independent of transport/UI |
| Service Layer | 2 | Coordinate persistence, AI orchestration, and response formatting |
| Service Layer | 3 | Apply input validation, policy checks, and guardrails |
| Service Layer | 4 | Keep domain logic testable and framework-light |

### 4) Agent Orchestration

| Group | Count | Responsibility |
|---|---:|---|
| Agent Layer | 1 | Build runtime context from user query, conversation state, and retrieved knowledge |
| Agent Layer | 2 | Decide when to answer directly vs invoke tools |
| Agent Layer | 3 | Manage tool execution sequence and consolidate outputs |
| Agent Layer | 4 | Preserve source-grounding and traceability |

### 5) LLM Integration

| Group | Count | Responsibility |
|---|---:|---|
| LLM Layer | 1 | Provide model inference via OpenAI API (initial provider) |
| LLM Layer | 2 | Generate structured plans/tool-call intents |
| LLM Layer | 3 | Produce final natural-language responses |
| LLM Layer | 4 | Handle provider failures, retries, and fallback strategy (future) |

### 6) Tool Selection & Execution

| Group | Count | Responsibility |
|---|---:|---|
| Tool Router | 1 | Select minimal required tools for a query |
| Tool Router | 2 | Validate tool inputs against strict schemas |
| Tool Router | 3 | Execute tools in controlled runtime |
| Tool Router | 4 | Return structured outputs for synthesis |

### 7) Tool Modules

| Group | Count | Tool | Primary Backend Dependency |
|---|---:|---|---|
| Tools | 1 | RAG document search | pgvector + embeddings |
| Tools | 2 | SQL/database querying | PostgreSQL |
| Tools | 3 | Python analysis | Python execution environment |
| Tools | 4 | External web/API retrieval | External APIs and web sources |
| Tools | 5 | Chart generation | Plot/visualization service |

### 8) Data & Infrastructure

| Group | Count | Component | Responsibility |
|---|---:|---|---|
| Data Layer | 1 | PostgreSQL | Relational storage (users, chats, metadata, documents) |
| Data Layer | 2 | pgvector | Embedding storage and nearest-neighbor retrieval |
| Integration | 3 | External APIs | Fresh external knowledge and domain data |

## Frontend/Backend Separation

| Group | Count | Boundary Rule |
|---|---:|---|
| Separation | 1 | Frontend never directly queries database or vector index |
| Separation | 2 | Backend owns all AI orchestration and tool execution |
| Separation | 3 | Frontend communicates only through versioned REST endpoints |

## API Boundaries

| Group | Count | Boundary |
|---|---:|---|
| API Contracts | 1 | Typed request/response models via Pydantic |
| API Contracts | 2 | Stable endpoint surface to shield frontend from internal changes |
| API Contracts | 3 | Consistent error envelope for user-safe failures |

## AI Orchestration Boundaries

| Group | Count | Boundary |
|---|---:|---|
| AI Boundaries | 1 | Service layer requests orchestration; orchestration does not own HTTP concerns |
| AI Boundaries | 2 | Tool modules are isolated and replaceable |
| AI Boundaries | 3 | Provider-specific LLM code remains behind adapter interfaces |

## Database & Vector Search Approach

| Group | Count | Direction |
|---|---:|---|
| Database | 1 | PostgreSQL as single primary datastore |
| Database | 2 | pgvector extension for embedding similarity search |
| Retrieval | 3 | RAG pipeline retrieves candidate chunks, then LLM synthesizes grounded answer |

## Future Authentication (Planned)

| Group | Count | Direction |
|---|---:|---|
| Auth | 1 | User authentication at API boundary |
| Auth | 2 | Session/token handling for conversation ownership |
| Auth | 3 | Authorization checks for document/chat access |

## Observability (Planned)

| Group | Count | Direction |
|---|---:|---|
| Observability | 1 | Structured application logs across API/services/tools |
| Observability | 2 | Request tracing for tool calls and retrieval paths |
| Observability | 3 | Basic metrics: latency, tool error rate, retrieval usage |

## Error Handling

| Group | Count | Policy |
|---|---:|---|
| Error Handling | 1 | Validate all external and tool inputs |
| Error Handling | 2 | Map internal exceptions to stable API errors |
| Error Handling | 3 | Return user-safe messages while preserving diagnostic logs |
| Error Handling | 4 | Degrade gracefully when non-critical tools fail |

## Security

| Group | Count | Policy |
|---|---:|---|
| Security | 1 | Secrets only via environment variables |
| Security | 2 | Strict input validation at API/tool boundaries |
| Security | 3 | Least-privilege external API access |
| Security | 4 | No automatic destructive actions by agent tools |

## Deployment Architecture (Planned)

| Group | Count | Direction |
|---|---:|---|
| Deployment | 1 | Containerized frontend and backend with Docker |
| Deployment | 2 | Managed PostgreSQL with pgvector support |
| Deployment | 3 | CI/CD via GitHub Actions |
| Deployment | 4 | Cloud-hosted services with environment-based configuration |

## Phase 1 Clarification

| Group | Count | Clarification |
|---|---:|---|
| Implementation State | 1 | FastAPI API boundary now exists with an implemented health route. |
| Implementation State | 2 | Frontend foundation now exists as React + TypeScript + Vite shell with environment-based API configuration. |
| Implementation State | 3 | Service/agent/tool/database packages are structural seams only; business features remain future-phase scope. |

## Current Reality vs Intended End State

| Group | Count | Item | State |
|---|---:|---|---|
| Current State | 1 | Architecture definition | Documented |
| Current State | 2 | Backend foundation + health endpoint + tests | Implemented |
| Current State | 3 | Frontend foundation scaffold | Implemented |
| Current State | 4 | AI orchestration, RAG, tool-calling, and data platform features | Not implemented yet |
