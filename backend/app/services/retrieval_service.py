from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.core.settings import get_settings
from app.models.document import Document, DocumentChunk
from app.services.embedding_service import EmbeddingService


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

    def search(self, question: str, top_k: int | None = None) -> list[RetrievedChunk]:
        k = top_k if top_k is not None else self.settings.rag_top_k_default
        k = min(max(k, 1), self.settings.rag_top_k_max)

        query_embedding = self.embedding_service.embed_texts([question])[0]
        distance = DocumentChunk.embedding.cosine_distance(query_embedding)
        similarity = (1 - distance).label("similarity")

        statement: Select[tuple[DocumentChunk, Document, float]] = (
            select(DocumentChunk, Document, similarity)
            .join(Document, Document.id == DocumentChunk.document_id)
            .order_by(distance)
            .limit(k)
        )

        rows = self.db.execute(statement).all()
        return [
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
