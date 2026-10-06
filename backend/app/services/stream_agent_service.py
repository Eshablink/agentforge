"""Bounded agent SSE events; native provider deltas are final-answer only."""
from __future__ import annotations

import time
from collections.abc import Iterator

from app.core.telemetry import record
from app.services.agent_provider import DecisionRequest, FakeDecisionProvider
from app.services.agent_service import AgentOrchestrationService
from app.services.native_stream import NativeStreamFailure, NativeStreamUnavailable, native_deltas
from app.services.tool_registry import MAX_AGENT_STEPS, MAX_TOOLS_PER_REQUEST, ToolError


class StreamAgentService(AgentOrchestrationService):
    def stream(self, question: str, *, context: str = "", user_id=None) -> Iterator[tuple[str, dict]]:
        started = time.monotonic()
        results: list[dict] = []
        names: list[str] = []
        sources: dict[str, dict] = {}
        output_chars = 0
        delta_count = 0
        first_ms = None
        mode = "fallback"
        outcome = "error"
        record("stream_start")

        def check_time():
            if time.monotonic() - started >= self.settings.max_stream_duration_seconds:
                raise ToolError("Stream duration limit reached")

        def tokens(deltas):
            nonlocal output_chars, delta_count, first_ms
            for delta in deltas:
                check_time()
                if not isinstance(delta, str):
                    raise NativeStreamFailure("Invalid AI provider delta")
                if not delta:
                    continue
                if first_ms is None:
                    first_ms = round((time.monotonic() - started) * 1000, 3)
                remaining = self.settings.max_stream_output_chars - output_chars
                if remaining <= 0:
                    raise ToolError("Stream output limit reached")
                for offset in range(0, len(delta), 120):
                    part = delta[offset:offset + 120]
                    if len(part) > remaining:
                        raise ToolError("Stream output limit reached")
                    remaining -= len(part)
                    output_chars += len(part)
                    delta_count += 1
                    yield "token", {"text": part}

        try:
            for step in range(min(self.settings.max_agent_steps, MAX_AGENT_STEPS)):
                check_time()
                request = DecisionRequest(question=question[:5000], conversation_context=context[:8000], prior_tool_results=results[-3:], step=step)
                decision = self.provider.decide(request)
                check_time()
                if decision.action in {"answer", "finish"}:
                    answer = decision.final_response or "I could not find enough information to answer that."
                    kind = "DIRECT" if not results else ("RAG_GROUNDED" if "document_search" in names and sources else "TOOL_DERIVED" if "document_search" not in names else "INSUFFICIENT_EVIDENCE")
                    if kind == "INSUFFICIENT_EVIDENCE":
                        yield from tokens((answer,))
                    else:
                        try:
                            deltas = native_deltas(self.provider, request)
                            # Iterator creation is lazy; availability is detected on first next().
                            first = next(deltas)
                        except NativeStreamUnavailable:
                            yield from tokens((answer,))
                        except StopIteration:
                            raise NativeStreamFailure("Empty AI provider stream")
                        else:
                            mode = "native"
                            def ordered():
                                yield first
                                yield from deltas
                            yield from tokens(ordered())
                    check_time()
                    outcome = "success"
                    yield "message_end", {"answer_kind": kind, "tools_used": names[:MAX_TOOLS_PER_REQUEST], "sources": list(sources.values())[:20], "stream_mode": mode}
                    return
                if decision.action != "tool" or not decision.tool_name or decision.tool_name not in self.tools.names:
                    raise ToolError("Requested tool is not available")
                if len(names) >= min(self.settings.max_tool_calls, MAX_TOOLS_PER_REQUEST):
                    raise ToolError("Tool-call limit reached")
                yield "tool_start", {"tool": decision.tool_name}
                result = self.tools.execute(decision.tool_name, decision.arguments, user_id=user_id)
                check_time()
                results.append(result)
                names.append(decision.tool_name)
                if decision.tool_name == "document_search":
                    matches = result.get("results", [])
                    yield "retrieval", {"count": len(matches[:20])}
                    for item in matches[:20]:
                        sources[str(item["chunk_id"])] = {key: item[key] for key in ("document_id", "filename", "chunk_id", "chunk_index", "similarity")}
                yield "tool_result", {"tool": decision.tool_name, "status": "success"}
                if isinstance(self.provider, FakeDecisionProvider):
                    if decision.tool_name == "document_search":
                        matches = result.get("results", [])
                        answer = "Retrieved document evidence: " + matches[0]["content"][:2000] if matches else "I could not find enough information in the uploaded documents to answer that."
                        kind = "RAG_GROUNDED" if matches else "INSUFFICIENT_EVIDENCE"
                    elif decision.tool_name == "calculator":
                        answer, kind = f"The result is {result['result']}.", "TOOL_DERIVED"
                    else:
                        answer, kind = f"The date is {result['date']}.", "TOOL_DERIVED"
                    yield from tokens((answer,))
                    check_time()
                    outcome = "success"
                    yield "message_end", {"answer_kind": kind, "tools_used": names[:MAX_TOOLS_PER_REQUEST], "sources": list(sources.values())[:20], "stream_mode": "simulated"}
                    return
            raise ToolError("Agent step limit reached")
        except GeneratorExit:
            outcome = "cancelled"
            raise
        except (ToolError, NativeStreamFailure) as exc:
            record("stream_failure", error_category="limit" if isinstance(exc, ToolError) else "provider")
            yield "error", {"code": "agent_limit" if isinstance(exc, ToolError) else "agent_error", "message": str(exc)[:160] if isinstance(exc, ToolError) else "AI stream unavailable"}
        except Exception:
            record("stream_failure", error_category="provider")
            yield "error", {"code": "agent_error", "message": "The agent could not complete the request safely. Please try again."}
        finally:
            record("stream_finish", mode=mode, outcome=outcome, first_token_ms=first_ms, duration_ms=round((time.monotonic() - started) * 1000, 3), delta_count=delta_count, output_chars=output_chars)
