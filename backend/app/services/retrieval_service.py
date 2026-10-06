from __future__ import annotations

import uuid
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


class RetrievalService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()
        self.embedding_service = EmbeddingService()

    def search(self, question: str, top_k: int | None = None, *, user_id: uuid.UUID | None = None) -> list[RetrievedChunk]:
        k = top_k if top_k is not None else self.settings.rag_top_k_default
        k = min(max(k, 1), self.settings.rag_top_k_max)
        vector = self.embedding_service.embed_texts([question])[0]
        distance = DocumentChunk.embedding.cosine_distance(vector)
        similarity = (1 - distance).label("similarity")
        candidates = min(self.settings.rag_candidate_max, max(k, k * 3))
        statement: Select = (
            select(DocumentChunk, Document, similarity)
            .join(Document, Document.id == DocumentChunk.document_id)
            .where(Document.user_id.is_(None) if user_id is None else Document.user_id == user_id)
            .order_by(distance, DocumentChunk.id)
            .limit(candidates)
        )
        rows = self.db.execute(statement).all()
        items = [RetrievedChunk(chunk_id=str(chunk.id), document_id=str(document.id),
                                filename=document.filename, chunk_index=chunk.chunk_index,
                                content=chunk.content, similarity=float(score))
                 for chunk, document, score in rows]
        return select_evidence(question, items, limit=k, minimum_similarity=self.settings.rag_min_similarity)
