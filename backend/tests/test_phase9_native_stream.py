from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from app.services.agent_provider import AgentDecision, DecisionRequest, FakeDecisionProvider, LLMDecisionProvider, OpenAIDecisionProvider
from app.services.native_stream import NativeStreamFailure, native_deltas
from app.services.stream_agent_service import StreamAgentService
from app.services.tool_registry import ToolRegistry


class EmptyRetrieval:
    def search(self, query, top_k=None, *, user_id=None):
        return []


class DirectProvider(LLMDecisionProvider):
    def decide(self, request):
        return AgentDecision(action="answer", final_response="fallback answer")


class RaisingProvider(LLMDecisionProvider):
    def decide(self, request):
        raise RuntimeError("private provider detail")


def _service(provider=None):
    return StreamAgentService(provider or FakeDecisionProvider(), ToolRegistry(EmptyRetrieval()))


def test_fake_deltas_are_simulated_and_terminal_once():
    frames = list(_service().stream("7 * 8"))
    names = [name for name, _ in frames]
    assert "message_start" not in names
    assert names.count("message_end") == 1 and "error" not in names
    assert "56" in "".join(data["text"] for name, data in frames if name == "token")
    assert frames[-1][1]["stream_mode"] == "simulated"


def test_fallback_is_explicit_for_non_native_provider():
    assert list(_service(DirectProvider()).stream("anything")) == [
        ("token", {"text": "fallback answer"}),
        ("message_end", {"answer_kind": "DIRECT", "tools_used": [], "sources": [], "stream_mode": "fallback"}),
    ]


def test_failure_one_terminal_and_no_secret():
    frames = list(_service(RaisingProvider()).stream("anything"))
    assert [name for name, _ in frames].count("error") == 1
    assert "message_end" not in [name for name, _ in frames]
    assert "private provider detail" not in json.dumps(frames)


def test_native_delta_adapter_order_and_closes():
    class Frames:
        closed = False
        def __iter__(self):
            for text in ("alpha", "beta"):
                yield SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content=text))])
        def close(self):
            self.closed = True
    frames = Frames()
    provider = object.__new__(OpenAIDecisionProvider)
    provider.model = "offline-test"
    provider.settings = SimpleNamespace(llm_timeout_seconds=5, llm_max_retries=0)
    provider.client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=lambda **kw: frames)))
    assert list(native_deltas(provider, DecisionRequest(question="test", step=0))) == ["alpha", "beta"]
    assert frames.closed


def test_native_failure_after_first_delta_never_retries():
    calls = []
    def create(**kw):
        calls.append(1)
        def frames():
            yield SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content="start"))])
            raise RuntimeError("private key")
        return frames()
    provider = object.__new__(OpenAIDecisionProvider)
    provider.model = "offline-test"
    provider.settings = SimpleNamespace(llm_timeout_seconds=5, llm_max_retries=2)
    provider.client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    stream = native_deltas(provider, DecisionRequest(question="test", step=0))
    assert next(stream) == "start"
    with pytest.raises(NativeStreamFailure):
        next(stream)
    assert len(calls) == 1
