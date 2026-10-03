from __future__ import annotations

import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.core.settings import get_settings
from app.db.session import SessionLocal, engine
from app.models.document import Document, DocumentChunk


def test_pgvector_extension_enabled() -> None:
    with engine.connect() as connection:
        extension = connection.execute(
            text("SELECT extname FROM pg_extension WHERE extname = 'vector'")
        ).scalar_one_or_none()

    assert extension == "vector"


def test_document_chunk_unique_constraint() -> None:
    settings = get_settings()
    session = SessionLocal()

    document_id = uuid.uuid4()

    try:
        session.add(
            Document(
                id=document_id,
                filename="constraint.txt",
                content_type="text/plain",
                metadata_json={},
                status="processed",
            )
        )
        session.flush()

        vector = [0.01] * settings.embedding_dimension
        session.add(
            DocumentChunk(
                id=uuid.uuid4(),
                document_id=document_id,
                chunk_index=0,
                content="first",
                metadata_json={},
                embedding_model=settings.embedding_model,
                embedding=vector,
            )
        )
        session.flush()

        session.add(
            DocumentChunk(
                id=uuid.uuid4(),
                document_id=document_id,
                chunk_index=0,
                content="duplicate index",
                metadata_json={},
                embedding_model=settings.embedding_model,
                embedding=vector,
            )
        )

        with pytest.raises(IntegrityError):
            session.flush()
    finally:
        session.rollback()
        session.close()
