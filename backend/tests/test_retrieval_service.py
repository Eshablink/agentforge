from __future__ import annotations

import uuid

from app.core.settings import get_settings
from app.db.session import SessionLocal
from app.models.document import Document, DocumentChunk
from app.models.user import User
from app.services.embedding_service import EmbeddingService
from app.services.retrieval_service import RetrievalService


def _make_user(session, user_id: uuid.UUID, suffix: str) -> None:
    session.add(User(id=user_id, email=f"{suffix}-{user_id.hex}@example.com", password_hash="test-hash", is_active=True))
    session.flush()


def test_retrieval_returns_relevant_chunks(monkeypatch) -> None:
    settings = get_settings()
    session = SessionLocal()
    owner_id, doc1_id, doc2_id = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    try:
        _make_user(session, owner_id, "owner")
        session.add_all([
            Document(id=doc1_id, user_id=owner_id, filename="relevant.txt", content_type="text/plain", metadata_json={}, status="processed"),
            Document(id=doc2_id, user_id=owner_id, filename="other.txt", content_type="text/plain", metadata_json={}, status="processed"),
        ])
        session.flush()
        near = [0.9] * settings.embedding_dimension
        far = [-0.9] * settings.embedding_dimension
        session.add_all([
            DocumentChunk(id=uuid.uuid4(), document_id=doc1_id, chunk_index=0, content="important retrieval context", metadata_json={}, embedding_model=settings.embedding_model, embedding=near),
            DocumentChunk(id=uuid.uuid4(), document_id=doc2_id, chunk_index=0, content="irrelevant context", metadata_json={}, embedding_model=settings.embedding_model, embedding=far),
        ])
        session.flush()
        monkeypatch.setattr(EmbeddingService, "embed_texts", lambda self, texts: [near])
        results = RetrievalService(db=session).search(question="important", top_k=1, user_id=owner_id)
        assert len(results) == 1
        assert results[0].filename == "relevant.txt"
        assert results[0].chunk_index == 0
    finally:
        session.rollback()
        session.close()


def test_retrieval_excludes_other_users_documents(monkeypatch) -> None:
    settings = get_settings()
    session = SessionLocal()
    owner_id, foreign_id = uuid.uuid4(), uuid.uuid4()
    try:
        _make_user(session, owner_id, "owner")
        _make_user(session, foreign_id, "foreign")
        own_doc = Document(id=uuid.uuid4(), user_id=owner_id, filename="own.txt", content_type="text/plain", metadata_json={}, status="processed")
        foreign_doc = Document(id=uuid.uuid4(), user_id=foreign_id, filename="private.txt", content_type="text/plain", metadata_json={}, status="processed")
        session.add_all([own_doc, foreign_doc])
        session.flush()
        vector = [0.8] * settings.embedding_dimension
        session.add_all([
            DocumentChunk(id=uuid.uuid4(), document_id=own_doc.id, chunk_index=0, content="own content", metadata_json={}, embedding_model=settings.embedding_model, embedding=vector),
            DocumentChunk(id=uuid.uuid4(), document_id=foreign_doc.id, chunk_index=0, content="private other user content", metadata_json={}, embedding_model=settings.embedding_model, embedding=vector),
        ])
        session.flush()
        monkeypatch.setattr(EmbeddingService, "embed_texts", lambda self, texts: [vector])
        results = RetrievalService(db=session).search("own content", user_id=owner_id)
        assert results
        assert all(r.filename != "private.txt" for r in results)
    finally:
        session.rollback()
        session.close()
