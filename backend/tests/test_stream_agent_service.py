from __future__ import annotations

import json

from app.services.agent_provider import AgentDecision, DecisionRequest, FakeDecisionProvider, LLMDecisionProvider
from app.services.stream_agent_service import StreamAgentService
from app.services.tool_registry import ToolRegistry


class EmptyRetrieval:
    def search(self, query, top_k=None, *, user_id=None):
        return []


class RaisingProvider(LLMDecisionProvider):
    def decide(self, request: DecisionRequest) -> AgentDecision:
        raise RuntimeError("secret provider details must not leak")


def _service(provider=None):
    return StreamAgentService(provider or FakeDecisionProvider(), ToolRegistry(EmptyRetrieval()))


def test_stream_service_emits_operational_events_without_message_start() -> None:
    frames = list(_service().stream("7 * 8"))
    events = [name for name, _ in frames]
    assert "message_start" not in events
    assert "token" in events
    assert "message_end" in events


def test_stream_calculator_answer_contains_result() -> None:
    frames = list(_service().stream("7 * 8"))
    tokens = "".join(data.get("text", "") for name, data in frames if name == "token")
    assert "56" in tokens


def test_stream_reports_tool_activity() -> None:
    frames = list(_service().stream("7 * 8"))
    tool_starts = [data["tool"] for name, data in frames if name == "tool_start"]
    assert "calculator" in tool_starts


def test_stream_provider_failure_is_a_controlled_safe_error() -> None:
    frames = list(_service(RaisingProvider()).stream("anything"))
    errors = [data for name, data in frames if name == "error"]
    assert len(errors) == 1
    assert errors[0]["code"] == "agent_error"
    assert "secret provider details" not in json.dumps(errors)
    assert "secret provider details" not in json.dumps(frames)


def test_stream_never_emits_chain_of_thought_or_secrets() -> None:
    frames = list(_service().stream("7 * 8"))
    blob = json.dumps([data for _, data in frames])
    for secret in ["chain", "reasoning", "api_key", "sk-", "bearer"]:
        assert secret.lower() not in blob.lower()
