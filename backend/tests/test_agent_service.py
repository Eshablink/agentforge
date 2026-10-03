from __future__ import annotations

import pytest

from app.services.agent_provider import FakeDecisionProvider
from app.services.agent_service import AgentOrchestrationService
from app.services.tool_registry import ToolError, ToolRegistry


class EmptyRetrieval:
    def search(self, query, top_k=None, *, user_id=None):
        return []


def test_calculator_tool_is_allowlisted_and_deterministic() -> None:
    registry = ToolRegistry(EmptyRetrieval())
    assert registry.execute("calculator", {"operation": "add", "a": "2.5", "b": "3"})["result"] == "5.5"
    assert registry.execute("calculator", {"operation": "multiply", "a": "3", "b": "4"})["result"] == "12"


def test_tool_rejects_unknown_name_and_bad_arguments() -> None:
    registry = ToolRegistry(EmptyRetrieval())
    with pytest.raises(ToolError):
        registry.execute("python", {"code": "print(1)"})
    with pytest.raises(ToolError):
        registry.execute("calculator", {"operation": "eval", "a": "1", "b": "2"})


def test_agent_returns_tool_derived_classification_and_trace() -> None:
    service = AgentOrchestrationService(FakeDecisionProvider(), ToolRegistry(EmptyRetrieval()))
    result = service.run("7 * 8")
    assert result.answer == "The result is 56."
    assert result.answer_kind == "TOOL_DERIVED"
    assert result.tools_used == ["calculator"]
    assert any(event.event == "tool_executed" for event in result.events)


def test_agent_document_search_returns_insufficient_evidence_when_empty() -> None:
    service = AgentOrchestrationService(FakeDecisionProvider(), ToolRegistry(EmptyRetrieval()))
    result = service.run("What does the uploaded document say?")
    assert result.answer_kind == "INSUFFICIENT_EVIDENCE"
    assert result.sources == []
