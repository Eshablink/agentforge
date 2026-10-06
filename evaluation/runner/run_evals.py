#!/usr/bin/env python3
"""Deterministic offline RAG, tool, agent and streaming regression runner."""
from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
from app.services.agent_provider import AgentDecision, DecisionRequest, FakeDecisionProvider, LLMDecisionProvider
from app.services.agent_service import AgentOrchestrationService
from app.services.tool_registry import ToolError, ToolRegistry
from quality import report_metrics, run_ranking, run_stream


class InMemoryRetrieval:
    def __init__(self, results):
        self.results = results

    def search(self, query, top_k=None, *, user_id=None):
        from app.services.retrieval_service import RetrievedChunk
        rows = []
        for index, item in enumerate(self.results):
            def as_uuid(value, fallback):
                try:
                    return str(uuid.UUID(value))
                except (ValueError, TypeError):
                    return fallback
            rows.append(RetrievedChunk(
                chunk_id=as_uuid(item.get("chunk_id"), f"00000000-0000-0000-0000-{index+1:012d}"),
                document_id=as_uuid(item.get("document_id"), f"00000000-0000-0000-0000-{index+101:012d}"),
                filename=item.get("filename", "f.txt"), chunk_index=index,
                content=item.get("content", ""), similarity=0.9))
        return rows


class RepeatToolProvider(LLMDecisionProvider):
    def decide(self, request):
        return AgentDecision(action="tool", tool_name="date_offset", arguments={"days": 0})


class RaisingProvider(LLMDecisionProvider):
    def decide(self, request):
        raise RuntimeError("sensitive provider detail")


def run_rag(case):
    result = AgentOrchestrationService(FakeDecisionProvider(), ToolRegistry(InMemoryRetrieval(case.get("retrieval", [])))).run(case["question"])
    expect = case["expect"]
    if expect.get("retrieved") and not result.sources:
        return False, "expected source missing"
    if expect.get("has_source") and not result.sources:
        return False, "source missing"
    if expect.get("answer_kind") and result.answer_kind != expect["answer_kind"]:
        return False, "wrong answer classification"
    if expect.get("has_filename") and (not result.sources or not result.sources[0].filename):
        return False, "missing provenance filename"
    if expect.get("answer_contains") and expect["answer_contains"] not in result.answer:
        return False, "answer missing supplied evidence"
    return True, ""


def run_tool(case):
    registry = ToolRegistry(InMemoryRetrieval([]))
    expect = case["expect"]
    if case["kind"] == "tool_invalid":
        try:
            registry.execute("python", {"code": "print(1)"})
        except ToolError:
            return True, ""
        return False, "invalid tool accepted"
    result = AgentOrchestrationService(FakeDecisionProvider(), registry).run(case["question"])
    if expect.get("tool") and expect["tool"] not in result.tools_used:
        return False, "wrong tool selected"
    if expect.get("answer_contains") and expect["answer_contains"] not in result.answer:
        return False, "wrong derived answer"
    if expect.get("safe_failure") and result.answer_kind != "INSUFFICIENT_EVIDENCE":
        return False, "unsafe tool failure"
    return True, ""


def run_agent(case):
    provider = RepeatToolProvider() if case.get("provider") == "repeat_tool" else RaisingProvider() if case.get("provider") == "raising" else FakeDecisionProvider()
    result = AgentOrchestrationService(provider, ToolRegistry(InMemoryRetrieval([]))).run(case["question"])
    expect = case["expect"]
    if expect.get("answer_kind") and result.answer_kind != expect["answer_kind"]:
        return False, "wrong agent answer classification"
    if expect.get("tools_used") and result.tools_used != expect["tools_used"]:
        return False, "wrong agent tool use"
    if expect.get("answer_contains") and expect["answer_contains"] not in result.answer:
        return False, "wrong agent answer"
    if expect.get("safe_failure") and (result.answer_kind != "INSUFFICIENT_EVIDENCE" or "sensitive provider detail" in result.answer + str(result.events)):
        return False, "unsafe provider failure"
    if expect.get("bounded") and len(result.tools_used) > 4:
        return False, "unbounded tool loop"
    return True, ""


RUNNERS = {"rag": run_rag, "ranking": run_ranking, "tool": run_tool, "tool_invalid": run_tool, "agent": run_agent, "stream": run_stream}


def main():
    datasets = ["rag_cases.json", "tool_cases.json", "agent_cases.json", "stream_cases.json"]
    successes = []
    for name in datasets:
        for case in json.loads((ROOT / "evaluation" / "datasets" / name).read_text(encoding="utf-8")):
            runner = RUNNERS.get(case["kind"])
            ok, message = runner(case) if runner else (False, "unknown evaluation kind")
            successes.append((case["kind"], ok))
            print(f"{'PASS' if ok else 'FAIL'} {case['id']}" + (f": {message}" if not ok else ""))
    metrics = report_metrics(successes)
    for name, value in sorted(metrics.items()):
        print(f"METRIC {name}={value:.3f}")
    passed = sum(ok for _, ok in successes)
    failed = len(successes) - passed
    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
