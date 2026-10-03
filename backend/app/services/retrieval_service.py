from __future__ import annotations

import uuid

from pgvector.sqlalchemy import cosine_distance
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.core.settings import get_settings
from app.models.document import Document, DocumentChunk
from app.services.embedding_service import EmbeddingService


class RetrievalService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()
        self.embedding_service = EmbeddingService()

    def search(self, question: str, top_k: int | None = None, *, user_id: uuid.UUID | None = None):
        k = top_k if top_k is not None else self.settings.rag_top_k_default
        k = min(max(k, 1), self.settings.rag_top_k_max)
        query_embedding = self.embedding_service.embed_texts([question])[0]
        distance = DocumentChunk.embedding.cosine_distance(query_embedding)
        similarity = (1 - distance).label("similarity")
        statement = (
            select(DocumentChunk, Document, similarity)
            .join(Document, Document.id == DocumentChunk.document_id)
            .order_by(distance)
            .limit(k)
        )
        if user_id is not None:
            statement = statement.where(Document.user_id == user_id)
        rows = self.db.execute(statement).all()
        from app.services.retrieval_service import RetrievedChunk
        return [RetrievedChunk(chunk_id=str(chunk.id), document_id=str(document.id), filename=document.filename, chunk_index=chunk.chunk_index, content=chunk.content, similarity=float(score)) for chunk, document, score in rows]
