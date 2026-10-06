from __future__ import annotations

import uuid
from collections.abc import Callable
from dataclasses import dataclass

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.core.settings import get_settings
from app.models.document import Document, DocumentChunk
from app.services.embedding_service import EmbeddingService
from app.services.evidence_ranker import select_evidence


@dataclass(slots=True)
class RetrievedChunk:
    chunk_id: str
    document_id: str
    filename: str
    chunk_index: int
    content: str
    similarity: float


def _candidate_statement(vector: list[float], user_id: uuid.UUID | None, limit: int) -> Select:
    """Apply ownership in PostgreSQL *before* candidate limiting/reranking."""
    distance = DocumentChunk.embedding.cosine_distance(vector)
    similarity = (1 - distance).label("similarity")
    return (
        select(DocumentChunk, Document, similarity)
        .join(Document, Document.id == DocumentChunk.document_id)
        .where(Document.user_id.is_(None) if user_id is None else Document.user_id == user_id)
        .order_by(distance, DocumentChunk.id)
        .limit(limit)
    )


class RetrievalService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()
        self.embedding_service = EmbeddingService()

    def search(self, question: str, top_k: int | None = None, *, user_id: uuid.UUID | None = None) -> list[RetrievedChunk]:
        k = top_k if top_k is not None else self.settings.rag_top_k_default
        k = min(max(k, 1), self.settings.rag_top_k_max)
        vector = self.embedding_service.embed_texts([question])[0]
        candidates = min(self.settings.rag_candidate_max, max(k, k * 3))
        rows = self.db.execute(_candidate_statement(vector, user_id, candidates)).all()
        items = [
            RetrievedChunk(
                chunk_id=str(chunk.id),
                document_id=str(document.id),
                filename=document.filename,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                similarity=float(score),
            )
            for chunk, document, score in rows
        ]
        return select_evidence(question, items, limit=k, minimum_similarity=self.settings.rag_min_similarity)


class SessionScopedRetrieval:
    """Retrieval adapter that owns one short-lived DB session per search call."""

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory

    def search(self, question: str, top_k: int | None = None, *, user_id: uuid.UUID | None = None) -> list[RetrievedChunk]:
        with self._session_factory() as db:
            return RetrievalService(db).search(question, top_k, user_id=user_id)
