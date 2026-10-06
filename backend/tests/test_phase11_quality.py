from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy.dialects import postgresql

from app.services.evidence_ranker import select_evidence
from app.services.retrieval_service import RetrievedChunk, _candidate_statement
from app.services.rag_service import RAGService
from app.schemas.chat import ChatResponse


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


def test_ranking_consumes_no_more_than_forty_candidates():
    consumed = []
    def candidates():
        for index in range(60):
            consumed.append(index)
            yield row(f"evidence {index}", 0.9, index=index)
    assert len(select_evidence("evidence", candidates(), limit=3)) == 3
    assert len(consumed) == 40


def test_owner_predicate_and_candidate_cap_reside_in_sql_query():
    owner = UUID("00000000-0000-0000-0000-000000000111")
    dialect = postgresql.dialect()
    owned = str(_candidate_statement([0.0] * 1536, owner, 12).compile(
        dialect=dialect, compile_kwargs={"literal_binds": True}))
    legacy = str(_candidate_statement([0.0] * 1536, None, 12).compile(
        dialect=dialect, compile_kwargs={"literal_binds": True}))
    assert "documents.user_id =" in owned and str(owner) in owned
    assert "documents.user_id IS NULL" in legacy
    assert " LIMIT 12" in owned and " LIMIT 12" in legacy


def test_rag_context_budget_only_cites_chunks_actually_used(monkeypatch):
    from app.core.settings import Settings
    monkeypatch.setattr("app.services.rag_service.get_settings", lambda: Settings(rag_max_context_chars=200))
    first, second = row("a" * 800, 0.9), row("b" * 800, 0.8)
    svc = RAGService.__new__(RAGService)
    context, used = svc._bounded_context([first, second])
    assert len(context) <= 200
    assert used == [first]
    assert second.chunk_id not in context


def test_answer_cites_only_evidence_in_bounded_context(monkeypatch):
    from app.core.settings import Settings
    monkeypatch.setattr("app.services.rag_service.get_settings", lambda: Settings(rag_max_context_chars=200))
    first = row("Paris is the capital of France " + "x" * 500, 0.9)
    second = row("Berlin is the capital of Germany " + "y" * 500, 0.8)
    class Retrieval:
        def search(self, question, top_k=None, *, user_id=None):
            return [first, second]
    class LLM:
        def answer(self, question, context):
            assert "Paris is the capital" in context
            assert "Berlin" not in context
            assert len(context) <= 200
            return "Paris is the capital of France."
    service = RAGService.__new__(RAGService)
    service.retrieval = Retrieval()
    service.llm = LLM()
    response = service.answer("Capital of France?")
    assert isinstance(response, ChatResponse)
    assert [str(source.chunk_id) for source in response.sources] == [first.chunk_id]
    assert response.retrieved_chunks == 1


def test_empty_answer_returns_insufficient_evidence_without_sources():
    first = row("Evidence exists", 0.9)
    class Retrieval:
        def search(self, question, top_k=None, *, user_id=None):
            return [first]
    class LLM:
        def answer(self, question, context):
            return "  "
    service = RAGService.__new__(RAGService)
    service.retrieval = Retrieval()
    service.llm = LLM()
    response = service.answer("Something?")
    assert response.sources == []
    assert response.retrieved_chunks == 0
    assert "could not find enough" in response.answer.lower()
