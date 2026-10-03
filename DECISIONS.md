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

## ADR-009 — Backend configuration via pydantic-settings

- **Decision:** Use `pydantic-settings` for backend runtime configuration.
- **Reason:** Typed environment loading keeps config explicit and test-friendly.
- **Alternatives considered:** Direct `os.getenv` across modules (rejected due to weaker structure and maintainability).
- **Status:** Accepted

## ADR-010 — Minimal frontend API client abstraction

- **Decision:** Add a lightweight frontend API client module exposing `baseUrl` from `VITE_API_BASE_URL`.
- **Reason:** Keeps UI components decoupled from raw environment access and prepares clean service growth.
- **Alternatives considered:** Reading `import.meta.env` directly in each component (rejected for duplication and weaker boundaries).
- **Status:** Accepted

## ADR-011 — Preserve future boundary packages without feature logic

- **Decision:** Create empty package seams for `agents`, `tools`, `services`, `db`, and `models` in backend.
- **Reason:** Supports target architecture while keeping Phase 1 scope limited to foundation.
- **Alternatives considered:** Omitting package seams entirely (deferred to reduce future restructuring overhead).
- **Status:** Accepted

## Notes

- Decisions are expected to evolve as implementation proceeds.
- If a decision changes, add a new ADR entry that supersedes the previous one.
