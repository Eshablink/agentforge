from __future__ import annotations

import uuid

from app.core.settings import get_settings
from app.db.session import SessionLocal
from app.models.document import Document, DocumentChunk
from app.services.embedding_service import EmbeddingService
from app.services.retrieval_service import RetrievalService


def test_retrieval_returns_relevant_chunks(monkeypatch) -> None:
    settings = get_settings()
    session = SessionLocal()

    doc1_id = uuid.uuid4()
    doc2_id = uuid.uuid4()

    try:
        session.add_all(
            [
                Document(
                    id=doc1_id,
                    filename="relevant.txt",
                    content_type="text/plain",
                    metadata_json={},
                    status="processed",
                ),
                Document(
                    id=doc2_id,
                    filename="other.txt",
                    content_type="text/plain",
                    metadata_json={},
                    status="processed",
                ),
            ]
        )
        session.flush()

        near = [0.9] * settings.embedding_dimension
        far = [-0.9] * settings.embedding_dimension

        session.add_all(
            [
                DocumentChunk(
                    id=uuid.uuid4(),
                    document_id=doc1_id,
                    chunk_index=0,
                    content="important retrieval context",
                    metadata_json={},
                    embedding_model=settings.embedding_model,
                    embedding=near,
                ),
                DocumentChunk(
                    id=uuid.uuid4(),
                    document_id=doc2_id,
                    chunk_index=0,
                    content="irrelevant context",
                    metadata_json={},
                    embedding_model=settings.embedding_model,
                    embedding=far,
                ),
            ]
        )
        session.commit()

        monkeypatch.setattr(EmbeddingService, "embed_texts", lambda self, texts: [near])

        service = RetrievalService(db=session)
        results = service.search(question="important", top_k=1)

        assert len(results) == 1
        assert results[0].filename == "relevant.txt"
        assert results[0].chunk_index == 0
    finally:
        session.rollback()
        session.close()
