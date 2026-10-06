from __future__ import annotations

from uuid import uuid4
from app.services.evidence_ranker import select_evidence
from app.services.retrieval_service import RetrievedChunk
from app.services.rag_service import RAGService


def row(content, similarity, document=None, index=0):
    return RetrievedChunk(chunk_id=str(uuid4()), document_id=document or str(uuid4()),
                          filename="evidence.txt", chunk_index=index, content=content, similarity=similarity)


def test_reranker_prefers_relevant_evidence_and_suppresses_duplicate_text():
    irrelevant = row("irrelevant unrelated data", 0.70)
    useful = row("Paris is the capital of France", 0.68)
    duplicated = row("  paris  is the capital of FRANCE  ", 0.67)
    result = select_evidence("capital France Paris", [irrelevant, duplicated, useful], limit=3)
    assert result[0].chunk_id == useful.chunk_id
    assert len(result) == 2


def test_similarity_threshold_and_ties_are_deterministic():
    high = row("first evidence", 0.8, document="00000000-0000-0000-0000-000000000001")
    low = row("second evidence", 0.3)
    assert select_evidence("first", [low, high], limit=2, minimum_similarity=0.5) == [high]
    assert select_evidence("irrelevant", [high, low], limit=2) == select_evidence("irrelevant", [low, high], limit=2)


def test_rag_context_budget_only_cites_chunks_actually_used(monkeypatch):
    from app.core.settings import Settings
    monkeypatch.setattr("app.services.rag_service.get_settings", lambda: Settings(rag_max_context_chars=200))
    first, second = row("a" * 800, 0.9), row("b" * 800, 0.8)
    svc = RAGService.__new__(RAGService)
    context, used = svc._bounded_context([first, second])
    assert len(context) <= 200
    assert used == [first]
    assert second.chunk_id not in context
