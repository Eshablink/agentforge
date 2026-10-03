# AgentForge — AI Engineering Instructions

## Project Identity

Project: AgentForge

Repository: Eshablink/agentforge

AgentForge is a production-style full-stack agentic AI platform designed to demonstrate modern AI engineering and full-stack development.

The long-term system will combine:

- React
- TypeScript
- Python
- FastAPI
- LangChain
- OpenAI APIs
- LLM integrations
- Agentic workflows
- Tool calling
- RAG
- Embeddings
- Vector search
- PostgreSQL
- pgvector
- Data analysis
- Docker
- GitHub Actions
- Cloud deployment

---

## PRIMARY ENGINEERING RULE

Work as a senior software engineer.

Do not blindly implement instructions.

Before making significant changes:

1. Inspect the existing repository.
2. Understand the current architecture.
3. Check existing documentation.
4. Check PROGRESS.md.
5. Check DECISIONS.md.
6. Identify dependencies and potential conflicts.
7. Choose the simplest maintainable solution.

If a requested implementation conflicts with the existing architecture, explain the conflict and choose the safer design.

---

## DEVELOPMENT METHOD

Build AgentForge incrementally.

Never attempt to implement the entire platform in one step.

Work phase-by-phase.

Each phase must:

1. Inspect the current state.
2. Implement only the requested scope.
3. Write or update tests.
4. Run tests.
5. Verify the application.
6. Update documentation.
7. Update PROGRESS.md.
8. Record important architectural decisions in DECISIONS.md.
9. Review the changes for regressions.
10. Commit the completed work.

Do not start future phases unless explicitly instructed.

---

## CURRENT DEVELOPMENT PHASE

The project is currently at the repository foundation stage.

The next implementation phase will establish:

- FastAPI backend
- React + TypeScript frontend
- Basic project structure
- Health endpoint
- Initial automated tests

Do not implement RAG, agents, tool calling, authentication, or deployment until their respective phases are explicitly requested.

---

## CODE QUALITY

Write production-quality code.

Prefer:

- clear naming
- small modules
- separation of concerns
- type safety
- validation
- reusable services
- explicit interfaces
- meaningful error handling
- testable functions

Avoid:

- unnecessary abstractions
- duplicated code
- magic values
- hard-coded secrets
- dead code
- speculative features
- unnecessary dependencies

Do not add a library when the functionality can reasonably be implemented with the existing stack.

---

## SECURITY

Never commit:

- API keys
- passwords
- access tokens
- private credentials
- production secrets
- personal secrets

Use environment variables.

Maintain `.env.example` with safe placeholders.

---

## AI ENGINEERING PRINCIPLES

When implementing AI functionality:

- Make model interactions explicit.
- Keep prompts version-controlled where appropriate.
- Validate model outputs.
- Prefer structured outputs when useful.
- Handle model/API failures gracefully.
- Do not assume LLM responses are always correct.
- Keep provider-specific code isolated where practical.
- Design the system so model providers can be changed later.
- Log useful metadata without exposing sensitive information.

For agentic workflows:

- Tools must have clear schemas.
- Tool inputs must be validated.
- Tool execution must be observable.
- Dangerous or destructive operations must not be executed automatically.
- The agent should use the minimum number of tools necessary.

---

## TESTING

Every meaningful feature must have tests.

At minimum:

- unit tests for core logic
- API tests for backend endpoints
- integration tests where appropriate

Before declaring a phase complete:

- run the complete relevant test suite
- fix failures
- verify imports
- verify application startup
- verify the changed functionality

Never claim a test passed unless it was actually executed.

---

## DOCUMENTATION

Keep these files accurate:

- README.md
- PROJECT_BRIEF.md
- ARCHITECTURE.md
- PROGRESS.md
- DECISIONS.md

Documentation must describe what is actually implemented.

Do not document planned functionality as completed functionality.

Use clear technical language suitable for engineers and recruiters.

---

## GIT RULES

Use meaningful conventional commits.

Examples:

feat: add FastAPI foundation
feat: implement document ingestion
feat: add agent tool calling
fix: handle vector search failure
test: add RAG integration tests
docs: update architecture

Do not make huge unrelated commits.

Before committing:

- inspect changed files
- run tests
- review the diff
- ensure no secrets are included

---

## ARCHITECTURE PRINCIPLE

Prefer this long-term separation:

Frontend
↓
API layer
↓
Application/services layer
↓
Agent orchestration
↓
Tools
↓
Data/AI infrastructure

Keep frontend, backend, AI orchestration, tools, database and infrastructure independently understandable.

---

## TOKEN / CONTEXT EFFICIENCY

Do not repeatedly restate the entire project specification.

Use repository documentation as the source of truth.

Before each task:

1. Read AGENTS.md.
2. Read the relevant sections of PROJECT_BRIEF.md.
3. Read ARCHITECTURE.md when architecture is involved.
4. Read PROGRESS.md to determine current state.
5. Read DECISIONS.md when previous technical decisions affect the task.

Only inspect files relevant to the current task.

Do not unnecessarily dump entire files into context.

When reporting results, be concise and provide:

- what changed
- tests executed
- test results
- files changed
- commit hash
- remaining issues

---

## IMPORTANT

Do not fabricate completed functionality.

Do not skip tests.

Do not silently change architecture.

Do not rewrite working code without a reason.

Do not introduce future-phase functionality early.

Always leave the repository in a working state after completing a phase.
