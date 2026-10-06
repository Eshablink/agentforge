from __future__ import annotations

import uuid

from app.services.retrieval_service import RetrievedChunk, SessionScopedRetrieval


def test_session_scoped_retrieval_closes_session_after_search(monkeypatch):
    class TrackingSession:
        def __init__(self):
            self.closed = False

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            self.closed = True

    session = TrackingSession()

    class FakeRetrievalService:
        def __init__(self, db):
            self.db = db

        def search(self, question, top_k=None, *, user_id=None):
            return [
                RetrievedChunk(
                    chunk_id=str(uuid.uuid4()),
                    document_id=str(uuid.uuid4()),
                    filename="test.txt",
                    chunk_index=0,
                    content=question,
                    similarity=1.0,
                )
            ]

    monkeypatch.setattr("app.services.retrieval_service.RetrievalService", FakeRetrievalService)

    result = SessionScopedRetrieval(lambda: session).search("question", user_id=uuid.uuid4())

    assert result
    assert session.closed
