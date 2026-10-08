from __future__ import annotations

import uuid

from app.schemas.platform import AgentDecision
from app.services.agent_provider import LLMDecisionProvider
from app.services.agent_service import AgentOrchestrationService
from app.services.tool_registry import ToolRegistry


class SearchProvider(LLMDecisionProvider):
    def decide(self, request):
        if request.prior_tool_results:
            return AgentDecision(
                action="finish",
                final_response="Private evidence",
            )
        return AgentDecision(
            action="tool",
            tool_name="document_search",
            arguments={"query": request.question, "top_k": 1},
        )


class RecordingRetrieval:
    def __init__(self):
        self.calls = []

    def search(self, query, top_k=None, *, user_id=None):
        self.calls.append((query, top_k, user_id))
        return []


def test_agent_propagates_authenticated_user_to_document_search():
    retrieval = RecordingRetrieval()
    user_id = uuid.uuid4()
    service = AgentOrchestrationService(
        SearchProvider(),
        ToolRegistry(retrieval),
    )

    result = service.run(
        "Find my private document",
        user_id=user_id,
    )

    assert result.answer_kind == "INSUFFICIENT_EVIDENCE"
    assert retrieval.calls == [("Find my private document", 1, user_id)]
