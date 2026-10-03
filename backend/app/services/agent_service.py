from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.settings import get_settings
from app.models.document import DocumentChunk
from app.schemas.platform import AgentChatResponse, AgentEvent, AgentSource
from app.services.agent_provider import DecisionRequest, FakeDecisionProvider, LLMDecisionProvider
from app.services.retrieval_service import RetrievalService
from app.services.tool_registry import MAX_AGENT_STEPS, MAX_TRACE_EVENTS, MAX_TOOLS_PER_REQUEST, ToolError, ToolRegistry


@dataclass
class AgentResult:
    answer: str
    answer_kind: str
    sources: list[AgentSource]
    tools_used: list[str]
    events: list[AgentEvent]
    conversation_id: UUID | None = None

    def response(self) -> AgentChatResponse:
        return AgentChatResponse(answer=self.answer, answer_kind=self.answer_kind, sources=self.sources, tools_used=self.tools_used, events=self.events, conversation_id=self.conversation_id)


class AgentOrchestrationService:
    def __init__(self, provider: LLMDecisionProvider, tools: ToolRegistry) -> None:
        self.provider = provider
        self.tools = tools
        self.settings = get_settings()

    def run(self, question: str, *, context: str = "", user_id: UUID | None = None) -> AgentResult:
        events: list[AgentEvent] = [AgentEvent(event="request_received")]
        results: list[dict] = []
        tool_names: list[str] = []
        sources: dict[str, AgentSource] = {}
        answer = "I could not complete the request safely."
        answer_kind = "INSUFFICIENT_EVIDENCE"

        try:
            for step in range(min(self.settings.max_agent_steps, MAX_AGENT_STEPS)):
                decision = self.provider.decide(DecisionRequest(question=question[:5000], conversation_context=context[:self.settings.max_conversation_context_chars], prior_tool_results=results[-3:], step=step))
                events.append(AgentEvent(event="agent_decision", detail=decision.action))

                if decision.action in {"answer", "finish"}:
                    answer = (decision.final_response or "I could not find enough information to answer that.")[:4000]
                    answer_kind = "DIRECT" if not results else ("RAG_GROUNDED" if any(t == "document_search" for t in tool_names) else "TOOL_DERIVED")
                    break

                if decision.action != "tool" or not decision.tool_name:
                    raise ToolError("Invalid agent decision")
                if len(tool_names) >= min(self.settings.max_tool_calls, MAX_TOOLS_PER_REQUEST):
                    raise ToolError("Tool-call limit reached")

                events.append(AgentEvent(event="tool_selected", tool=decision.tool_name))
                result = self.tools.execute(decision.tool_name, decision.arguments)
                events.append(AgentEvent(event="tool_executed", tool=decision.tool_name, detail="success"))
                results.append(result)
                tool_names.append(decision.tool_name)

                if decision.tool_name == "document_search":
                    for item in result.get("results", []):
                        source = AgentSource(document_id=item["document_id"], filename=item["filename"], chunk_id=item["chunk_id"], chunk_index=item["chunk_index"], similarity=item["similarity"])
                        sources[source.chunk_id.hex if isinstance(source.chunk_id, UUID) else str(source.chunk_id)] = source

            else:
                raise ToolError("Agent step limit reached")

            if results and answer_kind == "INSUFFICIENT_EVIDENCE":
                last = results[-1]
                if last.get("tool") == "document_search" and last.get("results"):
                    # Fake provider completes in the next bounded decision step; fallback is cited retrieved text.
                    answer = "Retrieved document evidence: " + last["results"][0]["content"][:2000]
                    answer_kind = "RAG_GROUNDED"
                elif last.get("tool") == "calculator":
                    answer = f"The result is {last['result']}."
                    answer_kind = "TOOL_DERIVED"
                elif last.get("tool") == "date_offset":
                    answer = f"The date is {last['date']}."
                    answer_kind = "TOOL_DERIVED"
        except ToolError as exc:
            events.append(AgentEvent(event="safe_error", detail=str(exc)))
            answer = str(exc)
            answer_kind = "INSUFFICIENT_EVIDENCE"

        return AgentResult(answer=answer, answer_kind=answer_kind, sources=list(sources.values())[:20], tools_used=tool_names[:MAX_TOOLS_PER_REQUEST], events=events[:MAX_TRACE_EVENTS])
