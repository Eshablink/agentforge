from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    id: UUID
    filename: str
    content_type: str
    status: str
    chunk_count: int
    created_at: datetime


class DocumentListItem(BaseModel):
    id: UUID
    filename: str
    content_type: str
    status: str
    chunk_count: int = Field(ge=0)
    created_at: datetime
