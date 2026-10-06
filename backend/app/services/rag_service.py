from __future__ import annotations

import uuid
from sqlalchemy.orm import Session
from app.core.settings import get_settings
from app.schemas.chat import ChatResponse, ChatSource
from app.services.embedding_service import EmbeddingError
from app.services.llm_service import LLMError, LLMService
from app.services.retrieval_service import RetrievalService


class RAGServiceError(Exception):
    """Raised when RAG answer generation fails."""


class RAGService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.retrieval = RetrievalService(db=db)
        self.llm = LLMService()

    def answer(self, question: str, top_k: int | None = None, *, user_id: uuid.UUID | None = None) -> ChatResponse:
        try:
            retrieved = self.retrieval.search(question=question, top_k=top_k, user_id=user_id)
        except EmbeddingError as exc:
            raise RAGServiceError("Failed to generate retrieval embedding") from exc
        if not retrieved:
            return ChatResponse(answer="I could not find enough information in the uploaded documents to answer that.", sources=[], retrieved_chunks=0)
        context, used = self._bounded_context(retrieved)
        if not used:
            return ChatResponse(answer="I could not find enough information in the uploaded documents to answer that.", sources=[], retrieved_chunks=0)
        try:
            answer = self.llm.answer(question=question, context=context)
        except LLMError as exc:
            raise RAGServiceError("Failed to generate grounded answer") from exc
        if not answer.strip():
            return ChatResponse(answer="I could not find enough information in the uploaded documents to answer that.", sources=[], retrieved_chunks=0)
        sources = [ChatSource(document_id=item.document_id, filename=item.filename, chunk_id=item.chunk_id, chunk_index=item.chunk_index, similarity=round(item.similarity, 6)) for item in used]
        return ChatResponse(answer=answer[:4000], sources=sources, retrieved_chunks=len(used))

    def _bounded_context(self, chunks):
        budget = get_settings().rag_max_context_chars
        sections = []
        used = []
        for item in chunks[:get_settings().rag_top_k_max]:
            prefix = f"[source {len(used) + 1}] {item.filename[:255]} (chunk {item.chunk_index})\n"
            available = budget - sum(map(len, sections)) - len(prefix) - 2
            if available < 1:
                break
            content = item.content[:min(available, 800)]
            if not content:
                continue
            sections.append(prefix + content + "\n\n")
            used.append(item)
        return "".join(sections), used

    def _build_context(self, chunks) -> str:
        return self._bounded_context(chunks)[0]
