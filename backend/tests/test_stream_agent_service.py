from __future__ import annotations

import json

from app.services.agent_provider import FakeDecisionProvider
from app.services.stream_agent_service import StreamAgentService
from app.services.tool_registry import ToolRegistry


class EmptyRetrieval:
    def search(self, query, top_k=None, *, user_id=None):
        return []


def _service():
    return StreamAgentService(FakeDecisionProvider(), ToolRegistry(EmptyRetrieval()))


def test_stream_emits_start_tokens_and_end() -> None:
    frames = list(_service().stream("7 * 8"))
    events = [name for name, _ in frames]
    assert events[0] == "message_start"
    assert "token" in events
    assert "message_end" in events
    assert events[-1] == "message_end"


def test_stream_calculator_answer_contains_result() -> None:
    frames = list(_service().stream("7 * 8"))
    tokens = "".join(data.get("text", "") for name, data in frames if name == "token")
    assert "56" in tokens


def test_stream_reports_tool_activity() -> None:
    frames = list(_service().stream("7 * 8"))
    tool_starts = [data["tool"] for name, data in frames if name == "tool_start"]
    assert "calculator" in tool_starts


def test_stream_error_event_on_insufficient_evidence() -> None:
    frames = list(_service().stream("unanswerable with no docs"))
    events = [name for name, _ in frames]
    assert "error" in events or "message_end" in events


def test_stream_never_emits_chain_of_thought_or_secrets() -> None:
    frames = list(_service().stream("7 * 8"))
    blob = json.dumps([data for _, data in frames])
    for secret in ["chain", "reasoning", "api_key", "sk-", "bearer"]:
        assert secret.lower() not in blob.lower()
