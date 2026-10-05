from __future__ import annotations

from uuid import UUID, uuid4

import pytest

from app.schemas.chat import ChatResponse
from app.services.rag_service import RAGService
from app.services.retrieval_service import RetrievedChunk


class _FakeRetrieval:
    """RAG retrieval test double matching the ownership-aware service signature."""

    def __init__(self, rows: list[RetrievedChunk]) -> None:
        self.rows = rows
        self.calls: list[tuple[str, int | None, UUID | None]] = []

    def search(
        self, question: str, top_k: int | None = None, *, user_id: UUID | None = None
    ) -> list[RetrievedChunk]:
        self.calls.append((question, top_k, user_id))
        return self.rows


class _FakeLLM:
    def answer(self, question: str, context: str) -> str:
        return f"ANSWER::{question}::{context[:40]}"


def test_rag_service_returns_insufficient_context_when_no_chunks() -> None:
    service = RAGService.__new__(RAGService)
    fake_retrieval = _FakeRetrieval(rows=[])
    service.retrieval = fake_retrieval
    service.llm = _FakeLLM()

    response = service.answer("What is this?")

    assert response.retrieved_chunks == 0
    assert response.sources == []
    assert "could not find enough information" in response.answer.lower()
    assert fake_retrieval.calls == [("What is this?", None, None)]


def test_rag_service_builds_answer_and_sources() -> None:
    chunk = RetrievedChunk(
        chunk_id=str(uuid4()),
        document_id=str(uuid4()),
        filename="doc.md",
        chunk_index=0,
        content="important evidence",
        similarity=0.91,
    )

    service = RAGService.__new__(RAGService)
    fake_retrieval = _FakeRetrieval(rows=[chunk])
    service.retrieval = fake_retrieval
    service.llm = _FakeLLM()

    response = service.answer("Explain evidence")

    assert isinstance(response, ChatResponse)
    assert response.retrieved_chunks == 1
    assert response.sources[0].filename == "doc.md"
    assert response.sources[0].similarity == pytest.approx(0.91)
    assert "ANSWER::Explain evidence" in response.answer
    assert fake_retrieval.calls == [("Explain evidence", None, None)]


def test_rag_service_passes_authenticated_owner_to_retrieval() -> None:
    owner_id = uuid4()
    service = RAGService.__new__(RAGService)
    fake_retrieval = _FakeRetrieval(rows=[])
    service.retrieval = fake_retrieval
    service.llm = _FakeLLM()

    response = service.answer("private docs", user_id=owner_id)

    assert response.retrieved_chunks == 0
    assert fake_retrieval.calls == [("private docs", None, owner_id)]
