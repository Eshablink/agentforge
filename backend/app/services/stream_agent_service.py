from __future__ import annotations

from collections.abc import Iterator

from app.services.agent_provider import DecisionRequest, FakeDecisionProvider, LLMDecisionProvider
from app.services.agent_service import AgentOrchestrationService
from app.services.tool_registry import MAX_AGENT_STEPS, MAX_TOOLS_PER_REQUEST, ToolError, ToolRegistry


class StreamAgentService(AgentOrchestrationService):
    """Streaming variant of the bounded agent loop.

    Yields safe SSE frames (``(event_name, data_dict)``) incrementally while
    preserving the same ownership, allowlist, and bounding guarantees as the
    non-streaming :meth:`AgentOrchestrationService.run`.
    """

    def stream(
        self,
        question: str,
        *,
        context: str = "",
        user_id=None,
    ) -> Iterator[tuple[str, dict]]:
        results: list[dict] = []
        tool_names: list[str] = []
        source_map: dict = {}

        yield "message_start", {}

        finished = False
        try:
            for step in range(min(self.settings.max_agent_steps, MAX_AGENT_STEPS)):
                decision = self.provider.decide(
                    DecisionRequest(
                        question=question[:5000],
                        conversation_context=context[: self.settings.max_conversation_context_chars],
                        prior_tool_results=results[-3:],
                        step=step,
                    )
                )

                if decision.action in {"answer", "finish"}:
                    answer = (decision.final_response or "I could not find enough information to answer that.")[:4000]
                    yield "token", {"text": answer}
                    answer_kind = "DIRECT" if not results else ("RAG_GROUNDED" if "document_search" in tool_names else "TOOL_DERIVED")
                    yield "message_end", {
                        "answer_kind": answer_kind,
                        "tools_used": tool_names[:MAX_TOOLS_PER_REQUEST],
                        "sources": [dict(src) for src in source_map.values()][:20],
                    }
                    finished = True
                    break

                if decision.action != "tool" or not decision.tool_name:
                    raise ToolError("Invalid agent decision")
                if len(tool_names) >= min(self.settings.max_tool_calls, MAX_TOOLS_PER_REQUEST):
                    raise ToolError("Tool-call limit reached")
                if decision.tool_name not in self.tools.names:
                    raise ToolError("Requested tool is not available")

                yield "tool_start", {"tool": decision.tool_name}
                result = self.tools.execute(decision.tool_name, decision.arguments, user_id=user_id)
                results.append(result)
                tool_names.append(decision.tool_name)

                if decision.tool_name == "document_search":
                    matches = result.get("results", [])
                    yield "retrieval", {"count": len(matches)}
                    for item in matches:
                        source_map[str(item["chunk_id"])] = {
                            "document_id": item["document_id"],
                            "filename": item["filename"],
                            "chunk_id": item["chunk_id"],
                            "chunk_index": item["chunk_index"],
                            "similarity": item["similarity"],
                        }
                yield "tool_result", {"tool": decision.tool_name, "status": "success"}

                if isinstance(self.provider, FakeDecisionProvider):
                    if decision.tool_name == "document_search":
                        matches = result.get("results", [])
                        answer = ("Retrieved document evidence: " + matches[0]["content"][:2000]) if matches else "I could not find enough information in the uploaded documents to answer that."
                        answer_kind = "RAG_GROUNDED" if matches else "INSUFFICIENT_EVIDENCE"
                    elif decision.tool_name == "calculator":
                        answer = f"The result is {result['result']}."
                        answer_kind = "TOOL_DERIVED"
                    else:
                        answer = f"The date is {result['date']}."
                        answer_kind = "TOOL_DERIVED"
                    yield "token", {"text": answer}
                    yield "message_end", {"answer_kind": answer_kind, "tools_used": tool_names[:MAX_TOOLS_PER_REQUEST], "sources": [dict(s) for s in source_map.values()][:20]}
                    finished = True
                    break

            if not finished:
                raise ToolError("Agent step limit reached")
        except ToolError as exc:
            yield "error", {"message": str(exc)[:500], "code": "tool_error"}
        except Exception:
            yield "error", {"message": "The agent could not complete the request safely. Please try again.", "code": "agent_error"}
