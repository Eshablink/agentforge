#!/usr/bin/env python3
"""Deterministic AgentForge evaluation runner (no paid API calls).

Runs RAG, tool, and agent regression cases against fake/deterministic providers
and an in-memory retrieval double. Exit code is non-zero on any failure.

Usage:
    python evaluation/runner/run_evals.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from app.services.agent_provider import (  # noqa: E402
    AgentDecision,
    DecisionRequest,
    LLMDecisionProvider,
)
from app.services.agent_service import AgentOrchestrationService  # noqa: E402
from app.services.agent_provider import FakeDecisionProvider  # noqa: E402
from app.services.tool_registry import ToolRegistry  # noqa: E402


class InMemoryRetrieval:
    def __init__(self, results: list[dict]) -> None:
        self.results = results

    def search(self, query, top_k=None, *, user_id=None):
        return [self._to_chunk(item) for item in self.results]

    @staticmethod
    def _to_chunk(item):
        from app.services.retrieval_service import RetrievedChunk

        return RetrievedChunk(
            chunk_id=item.get("chunk_id", "c"),
            document_id=item.get("document_id", "d"),
            filename=item.get("filename", "f.txt"),
            chunk_index=0,
            content=item.get("content", ""),
            similarity=0.9,
        )


class RepeatToolProvider(LLMDecisionProvider):
    def decide(self, request: DecisionRequest) -> AgentDecision:
        return AgentDecision(action="tool", tool_name="date_offset", arguments={"days": 0})


class RaisingProvider(LLMDecisionProvider):
    def decide(self, request: DecisionRequest) -> AgentDecision:
        raise RuntimeError("sensitive provider detail")


def _provider_for(case: dict) -> LLMDecisionProvider:
    kind = case.get("provider")
    if kind == "repeat_tool":
        return RepeatToolProvider()
    if kind == "raising":
        return RaisingProvider()
    return FakeDecisionProvider()


def run_rag(case: dict) -> tuple[bool, str]:
    question = case["question"]
    retrieval = InMemoryRetrieval(case.get("retrieval", []))
    service = AgentOrchestrationService(FakeDecisionProvider(), ToolRegistry(retrieval))
    result = service.run(question, user_id=None)
    expect = case["expect"]
    if expect.get("retrieved"):
        if not result.sources:
            return False, f"expected sources, got none (kind={result.answer_kind})"
    if expect.get("has_source") and not result.sources:
        return False, "expected at least one source"
    if expect.get("answer_kind") and result.answer_kind != expect["answer_kind"]:
        return False, f"answer_kind={result.answer_kind} expected={expect['answer_kind']}"
    if expect.get("has_filename") and (not result.sources or not result.sources[0].filename):
        return False, "expected source filename"
    return True, ""


def run_tool(case: dict) -> tuple[bool, str]:
    question = case["question"]
    retrieval = InMemoryRetrieval([])
    service = AgentOrchestrationService(FakeDecisionProvider(), ToolRegistry(retrieval))
    result = service.run(question, user_id=None)
    expect = case["expect"]
    if expect.get("tool"):
        if expect["tool"] not in result.tools_used:
            return False, f"expected tool {expect['tool']}, used {result.tools_used}"
    if expect.get("answer_contains") and expect["answer_contains"] not in result.answer:
        return False, f"answer missing {expect['answer_contains']!r}: {result.answer!r}"
    if expect.get("has_error"):
        if not any(ev.event == "safe_error" for ev in result.events):
            return False, "expected a safe error event"
    if expect.get("safe_failure"):
        if result.answer_kind != "INSUFFICIENT_EVIDENCE":
            return False, f"expected safe failure, got {result.answer_kind}"
    return True, ""


def run_agent(case: dict) -> tuple[bool, str]:
    question = case["question"]
    retrieval = InMemoryRetrieval([])
    provider = _provider_for(case)
    service = AgentOrchestrationService(provider, ToolRegistry(retrieval))
    result = service.run(question, user_id=None)
    expect = case["expect"]
    if expect.get("answer_kind") and result.answer_kind != expect["answer_kind"]:
        return False, f"answer_kind={result.answer_kind} expected={expect['answer_kind']}"
    if expect.get("tools_used"):
        if result.tools_used != expect["tools_used"]:
            return False, f"tools_used={result.tools_used} expected={expect['tools_used']}"
    if expect.get("answer_contains") and expect["answer_contains"] not in result.answer:
        return False, f"answer missing {expect['answer_contains']!r}"
    if expect.get("safe_failure"):
        if result.answer_kind != "INSUFFICIENT_EVIDENCE":
            return False, f"expected safe failure, got {result.answer_kind}"
        if "sensitive provider detail" in result.answer or "sensitive provider detail" in str(result.events):
            return False, "provider detail leaked"
    if expect.get("bounded"):
        if len(result.tools_used) > 4:
            return False, "tool loop not bounded"
    return True, ""


RUNNERS = {"rag": run_rag, "tool": run_tool, "tool_invalid": run_tool, "agent": run_agent}


def load(relative: str) -> list[dict]:
    path = ROOT / relative
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    datasets = [
        "evaluation/datasets/rag_cases.json",
        "evaluation/datasets/tool_cases.json",
        "evaluation/datasets/agent_cases.json",
    ]
    failed = 0
    passed = 0
    for rel in datasets:
        for case in load(rel):
            kind = case["kind"]
            runner = RUNNERS.get(kind)
            if runner is None:
                print(f"FAIL {case['id']}: unknown kind {kind}")
                failed += 1
                continue
            ok, msg = runner(case)
            if ok:
                passed += 1
                print(f"PASS {case['id']}")
            else:
                failed += 1
                print(f"FAIL {case['id']}: {msg}")

    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
