from __future__ import annotations

import time
import uuid
from dataclasses import dataclass

from app.core.observability import record
from app.core.settings import get_settings
from app.schemas.platform import AgentChatResponse, AgentEvent, AgentSource
from app.services.agent_provider import DecisionRequest, FakeDecisionProvider, LLMDecisionProvider
from app.services.tool_registry import MAX_AGENT_STEPS, MAX_TRACE_EVENTS, MAX_TOOLS_PER_REQUEST, ToolError, ToolRegistry


@dataclass
class AgentResult:
    answer: str
    answer_kind: str
    sources: list[AgentSource]
    tools_used: list[str]
    events: list[AgentEvent]
    conversation_id: uuid.UUID | None = None

    def response(self) -> AgentChatResponse:
        return AgentChatResponse(answer=self.answer, answer_kind=self.answer_kind, sources=self.sources, tools_used=self.tools_used, events=self.events, conversation_id=self.conversation_id)


class AgentOrchestrationService:
    def __init__(self, provider: LLMDecisionProvider, tools: ToolRegistry) -> None:
        self.provider = provider
        self.tools = tools
        self.settings = get_settings()

    def run(self, question: str, *, context: str = "", user_id: uuid.UUID | None = None) -> AgentResult:
        started = time.perf_counter()
        events: list[AgentEvent] = [AgentEvent(event="request_received")]
        results: list[dict] = []
        tool_names: list[str] = []
        source_map: dict[str, AgentSource] = {}
        answer = "The agent could not complete the request safely. Please try again."
        answer_kind = "INSUFFICIENT_EVIDENCE"
        finished = False
        try:
            for step in range(min(self.settings.max_agent_steps, MAX_AGENT_STEPS)):
                provider_started = time.perf_counter()
                decision = self.provider.decide(DecisionRequest(question=question[:self.settings.max_prompt_chars], conversation_context=context[:self.settings.max_conversation_context_chars], prior_tool_results=results[-3:], step=step))
                record("provider_call", latency_ms=round((time.perf_counter() - provider_started) * 1000, 3), provider=type(self.provider).__name__, success=True)
                events.append(AgentEvent(event="agent_decision", detail=decision.action))
                if decision.action in {"answer", "finish"}:
                    answer = (decision.final_response or "I could not find enough information to answer that.")[:4000]
                    answer_kind = "DIRECT" if not results else ("RAG_GROUNDED" if "document_search" in tool_names else "TOOL_DERIVED")
                    finished = True
                    break
                if decision.action != "tool" or not decision.tool_name:
                    raise ToolError("Invalid agent decision")
                if len(tool_names) >= min(self.settings.max_tool_calls, MAX_TOOLS_PER_REQUEST):
                    raise ToolError("Tool-call limit reached")
                if decision.tool_name not in self.tools.names:
                    raise ToolError("Requested tool is not available")
                events.extend([AgentEvent(event="tool_selected", tool=decision.tool_name), AgentEvent(event="arguments_validated", tool=decision.tool_name)])
                tool_started = time.perf_counter()
                result = self.tools.execute(decision.tool_name, decision.arguments, user_id=user_id)
                record("tool_call", tool=decision.tool_name, latency_ms=round((time.perf_counter() - tool_started) * 1000, 3), success=True)
                events.append(AgentEvent(event="tool_executed", tool=decision.tool_name, detail="success"))
                results.append(result); tool_names.append(decision.tool_name)
                if decision.tool_name == "document_search":
                    record("retrieval", count=min(len(result.get("results", [])), 100))
                    for item in result.get("results", []):
                        src = AgentSource(document_id=item["document_id"], filename=item["filename"], chunk_id=item["chunk_id"], chunk_index=item["chunk_index"], similarity=item["similarity"])
                        source_map[str(src.chunk_id)] = src
                if isinstance(self.provider, FakeDecisionProvider):
                    if decision.tool_name == "document_search":
                        matches = result.get("results", [])
                        answer = ("Retrieved document evidence: " + matches[0]["content"][:2000]) if matches else "I could not find enough information in the uploaded documents to answer that."
                        answer_kind = "RAG_GROUNDED" if matches else "INSUFFICIENT_EVIDENCE"
                    elif decision.tool_name == "calculator":
                        answer, answer_kind = f"The result is {result['result']}.", "TOOL_DERIVED"
                    else:
                        answer, answer_kind = f"The date is {result['date']}.", "TOOL_DERIVED"
                    finished = True
                    break
            if not finished:
                raise ToolError("Agent step limit reached")
        except ToolError as exc:
            events.append(AgentEvent(event="safe_error", detail=str(exc))); answer = str(exc); answer_kind = "INSUFFICIENT_EVIDENCE"
        except Exception:
            record("provider_call", provider=type(self.provider).__name__, success=False, error_category="provider_failure")
            events.append(AgentEvent(event="safe_error", detail="Agent provider unavailable or returned an invalid decision"))
            answer = "The agent could not complete the request safely. Please try again."; answer_kind = "INSUFFICIENT_EVIDENCE"
        record("agent_request", latency_ms=round((time.perf_counter() - started) * 1000, 3), success=finished, error_category=None if finished else "agent_failure", tool_count=len(tool_names))
        return AgentResult(answer=answer, answer_kind=answer_kind, sources=list(source_map.values())[:20], tools_used=tool_names[:MAX_TOOLS_PER_REQUEST], events=events[:MAX_TRACE_EVENTS])
