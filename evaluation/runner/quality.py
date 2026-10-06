"""Deterministic offline evidence, owner-query and streaming checks."""
from __future__ import annotations

import uuid
from sqlalchemy.dialects import postgresql
from app.services.evidence_ranker import select_evidence
from app.services.retrieval_service import RetrievedChunk, _candidate_statement
from app.services.agent_provider import AgentDecision, FakeDecisionProvider, LLMDecisionProvider
from app.services.stream_agent_service import StreamAgentService
from app.services.tool_registry import ToolRegistry


def run_ranking(case):
    candidates = [RetrievedChunk(chunk_id=str(index), document_id=item["document_id"], filename=item["filename"],
                                 chunk_index=index, content=item["content"], similarity=item["similarity"])
                  for index, item in enumerate(case["retrieval"])]
    results = select_evidence(case["question"], candidates, limit=10, minimum_similarity=case.get("minimum_similarity", -1.0))
    expected = case["expect"]
    return (len(results) == expected["count"] and (not results or results[0].filename == expected["first_filename"]),
            "ranked evidence count or first provenance did not match")


def run_owner_scope(case):
    owner = uuid.UUID(case["expected_owner"]) if case["expected_owner"] else None
    sql = str(_candidate_statement([0.0] * 1536, owner, 5).compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))
    if owner is None:
        valid = "documents.user_id IS NULL" in sql
    else:
        valid = "documents.user_id =" in sql and str(owner) in sql
    return valid and " LIMIT 5" in sql, "owner predicate or candidate cap missing from SQL"


def run_stream(case):
    class Empty:
        def search(self, query, top_k=None, *, user_id=None):
            return []
    class Broken(LLMDecisionProvider):
        def decide(self, request):
            raise RuntimeError("private provider credentials")
    class Direct(LLMDecisionProvider):
        def decide(self, request):
            return AgentDecision(action="answer", final_response="abcdefghij")
    provider_name = case.get("provider", "fake")
    provider = Broken() if provider_name == "broken" else Direct() if provider_name == "direct" else FakeDecisionProvider()
    service = StreamAgentService(provider, ToolRegistry(Empty()))
    if "max_output_chars" in case:
        service.settings.max_stream_output_chars = case["max_output_chars"]
    frames = list(service.stream(case["question"]))
    names = [name for name, _ in frames]
    expect = case["expect"]
    tokens = "".join(item["text"] for name, item in frames if name == "token")
    valid = ("message_start" not in names and names.count("message_end") + names.count("error") == 1
             and names[-1] == expect["terminal"]
             and (not expect.get("tool") or any(name == "tool_start" and data["tool"] == expect["tool"] for name, data in frames))
             and (not expect.get("answer_contains") or expect["answer_contains"] in tokens)
             and (not expect.get("answer_kind") or frames[-1][1].get("answer_kind") == expect["answer_kind"])
             and (not expect.get("mode") or frames[-1][1].get("stream_mode") == expect["mode"])
             and (not expect.get("max_chars") or len(tokens) <= expect["max_chars"])
             and (not expect.get("no_private") or "private provider credentials" not in str(frames))
             and all(names.index("token") < names.index("message_end") for _ in [0] if "token" in names and "message_end" in names))
    return valid, "stream event order, bounds or terminal contract failed"


def report_metrics(results):
    groups = {"rag": ("rag", "ranking", "owner_scope"), "tool": ("tool", "tool_invalid"), "agent": ("agent",), "stream": ("stream",)}
    metrics = {}
    for label, kinds in groups.items():
        selected = [success for kind, success in results if kind in kinds]
        if selected:
            metrics[label + "_pass_rate"] = round(sum(selected) / len(selected), 3)
    return metrics
