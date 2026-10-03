from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=3, max_length=5000)
    top_k: int | None = Field(default=None, ge=1, le=50)


class ChatSource(BaseModel):
    document_id: UUID
    filename: str
    chunk_id: UUID
    chunk_index: int
    similarity: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSource]
    retrieved_chunks: int
