from __future__ import annotations

from sqlalchemy.orm import Session

from app.schemas.chat import ChatResponse, ChatSource
from app.services.llm_service import LLMService
from app.services.retrieval_service import RetrievalService


class RAGServiceError(Exception):
    """Raised when RAG answer generation fails."""


class RAGService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.retrieval = RetrievalService(db=db)
        self.llm = LLMService()

    def answer(self, question: str, top_k: int | None = None) -> ChatResponse:
        retrieved = self.retrieval.search(question=question, top_k=top_k)
        if not retrieved:
            return ChatResponse(
                answer="I could not find enough information in the uploaded documents to answer that.",
                sources=[],
                retrieved_chunks=0,
            )

        context = self._build_context(retrieved)
        answer = self.llm.answer(question=question, context=context)

        sources = [
            ChatSource(
                document_id=item.document_id,
                filename=item.filename,
                chunk_id=item.chunk_id,
                chunk_index=item.chunk_index,
                similarity=round(item.similarity, 6),
            )
            for item in retrieved
        ]

        return ChatResponse(answer=answer, sources=sources, retrieved_chunks=len(retrieved))

    def _build_context(self, chunks) -> str:
        return "\n\n".join(
            [
                f"[source {idx}] {item.filename} (chunk {item.chunk_index})\n{item.content}"
                for idx, item in enumerate(chunks, start=1)
            ]
        )
