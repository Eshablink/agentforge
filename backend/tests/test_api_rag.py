import io
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.embedding_service import EmbeddingService

client = TestClient(app)


@pytest.fixture(autouse=True)
def _mock_embeddings(monkeypatch: pytest.MonkeyPatch) -> None:
    def _fake(self, texts):
        return [[0.1] * self.settings.embedding_dimension for _ in texts]

    monkeypatch.setattr(EmbeddingService, "embed_texts", _fake)


@pytest.fixture(autouse=True)
def _mock_retrieval_and_llm(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.services.rag_service import RAGService

    def _fake_answer(self, question: str, top_k: int | None = None, *, user_id=None):
        from app.schemas.chat import ChatResponse, ChatSource

        if "missing" in question.lower():
            return ChatResponse(answer="I could not find enough information in the uploaded documents to answer that.", sources=[], retrieved_chunks=0)
        return ChatResponse(answer=f"Grounded answer for: {question}", sources=[ChatSource(document_id=uuid4(), filename="test.txt", chunk_id=uuid4(), chunk_index=0, similarity=0.95)], retrieved_chunks=1)

    monkeypatch.setattr(RAGService, "answer", _fake_answer)


def test_documents_endpoint_rejects_unsupported_file_type() -> None:
    response = client.post("/documents", files={"file": ("data.csv", io.BytesIO(b"a,b"), "text/csv")})
    assert response.status_code == 400


def test_documents_endpoint_accepts_txt_upload() -> None:
    response = client.post("/documents", files={"file": ("note.txt", io.BytesIO(b"agentforge data"), "text/plain")})
    assert response.status_code == 201
    payload = response.json()
    assert payload["filename"] == "note.txt"
    assert payload["status"] == "processed"
    assert payload["chunk_count"] >= 1


def test_chat_endpoint_returns_answer_and_sources() -> None:
    response = client.post("/chat", json={"question": "What is in docs?", "top_k": 3})
    assert response.status_code == 200
    assert response.json()["answer"].startswith("Grounded answer")
    assert len(response.json()["sources"]) == 1


def test_chat_endpoint_handles_insufficient_context() -> None:
    response = client.post("/chat", json={"question": "missing context", "top_k": 3})
    assert response.status_code == 200
    assert response.json()["retrieved_chunks"] == 0
    assert response.json()["sources"] == []
