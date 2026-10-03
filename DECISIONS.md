# AgentForge Decisions

This file is a lightweight Architecture Decision Record (ADR) log for key project choices.

## ADR-001 — React + TypeScript for Frontend

- **Decision:** Use React with TypeScript for the frontend application.
- **Reason:** Strong ecosystem, component-driven UI model, and TypeScript safety for maintainable UI/API integration.
- **Alternatives considered:** Vanilla JavaScript SPA (rejected for weaker typing/maintainability).
- **Status:** Accepted

## ADR-002 — FastAPI + Python for Backend

- **Decision:** Use Python with FastAPI for backend APIs and service orchestration.
- **Reason:** FastAPI provides strong performance, clear REST development flow, and excellent typing/validation support via Pydantic.
- **Alternatives considered:** Flask (rejected due to less built-in typing/validation ergonomics).
- **Status:** Accepted

## ADR-003 — PostgreSQL for Relational Data

- **Decision:** Use PostgreSQL as the primary relational datastore.
- **Reason:** Reliable ACID relational storage, mature tooling, and compatibility with extension ecosystem.
- **Alternatives considered:** SQLite for production runtime (rejected for scalability/production constraints).
- **Status:** Accepted

## ADR-004 — pgvector for Vector Search

- **Decision:** Use pgvector extension on PostgreSQL for embedding/vector similarity search.
- **Reason:** Keeps relational and vector data close in one operational datastore for a small cohesive project.
- **Alternatives considered:** Separate vector-only store (deferred to avoid early operational complexity).
- **Status:** Accepted

## ADR-005 — LangChain for AI Orchestration

- **Decision:** Use LangChain for agentic workflow orchestration and tool-routing scaffolding.
- **Reason:** Provides established abstractions for chains, agents, tools, and retrieval-oriented workflows.
- **Alternatives considered:** Fully custom orchestration from day one (deferred for faster early iteration).
- **Status:** Accepted

## ADR-006 — OpenAI API for Initial LLM Integration

- **Decision:** Use OpenAI API as the initial LLM provider.
- **Reason:** Mature API surface and strong ecosystem fit for rapid implementation of chat, tool-calling, and synthesis flows.
- **Alternatives considered:** Multi-provider support immediately (deferred to a later phase).
- **Status:** Accepted

## ADR-007 — Docker for Reproducible Environments

- **Decision:** Use Docker for local and deployment environment consistency.
- **Reason:** Reproducible builds/runs across developer machines and deployment targets.
- **Alternatives considered:** Host-native dependency setup only (rejected for reproducibility concerns).
- **Status:** Accepted

## ADR-008 — GitHub Actions for CI/CD

- **Decision:** Use GitHub Actions for CI/CD automation.
- **Reason:** Native integration with repository workflows and straightforward automation for lint/tests/build/deploy gates.
- **Alternatives considered:** External CI service from project start (deferred as unnecessary complexity).
- **Status:** Accepted

## Notes

- Decisions are expected to evolve as implementation proceeds.
- If a decision changes, add a new ADR entry that supersedes the previous one.
