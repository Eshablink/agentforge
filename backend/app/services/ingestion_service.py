from __future__ import annotations

import uuid
from dataclasses import dataclass

from fastapi import UploadFile
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.settings import get_settings
from app.models.document import Document, DocumentChunk
from app.services.chunker import TextChunker
from app.services.embedding_service import EmbeddingError, EmbeddingService
from app.services.extractor import DocumentExtractor, ExtractionError


class IngestionError(Exception):
    """Raised when document ingestion cannot complete."""


@dataclass(slots=True)
class IngestionResult:
    document: Document
    chunk_count: int


class DocumentIngestionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()
        self.extractor = DocumentExtractor()
        self.chunker = TextChunker()
        self.embedding_service = EmbeddingService()

    def ingest(self, file: UploadFile, *, user_id: uuid.UUID | None = None) -> tuple[Document, int]:
        self._validate_upload(file)

        try:
            extracted = self.extractor.extract(file)
            chunks = self.chunker.chunk(extracted.text)

            if not chunks:
                raise IngestionError("Document does not contain enough content to ingest")

            embeddings = self.embedding_service.embed_texts([chunk.content for chunk in chunks])

            document = Document(
                id=uuid.uuid4(),
                user_id=user_id,
                filename=file.filename or "uploaded-document",
                content_type=(file.content_type or "application/octet-stream").lower(),
                metadata_json=extracted.metadata,
                status="processed",
            )
            self.db.add(document)
            self.db.flush()

            for chunk, embedding in zip(chunks, embeddings, strict=True):
                self.db.add(
                    DocumentChunk(
                        id=uuid.uuid4(),
                        document_id=document.id,
                        chunk_index=chunk.index,
                        content=chunk.content,
                        metadata_json=chunk.metadata,
                        embedding_model=self.settings.embedding_model,
                        embedding=embedding,
                    )
                )

            self.db.commit()
            self.db.refresh(document)
            return document, len(chunks)
        except (ExtractionError, EmbeddingError) as exc:
            self.db.rollback()
            raise IngestionError(str(exc)) from exc
        except SQLAlchemyError as exc:
            self.db.rollback()
            raise IngestionError("Failed to persist document ingestion data") from exc

    def _validate_upload(self, file: UploadFile) -> None:
        if not file.filename:
            raise IngestionError("Filename is required")

        content_type = (file.content_type or "").lower()
        filename = file.filename.lower()

        if content_type not in self.settings.supported_content_type_list and not filename.endswith(
            (".pdf", ".txt", ".md")
        ):
            raise IngestionError("Unsupported file type. Supported: PDF, TXT, Markdown")

        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(0)
        if size > self.settings.max_upload_size_bytes:
            raise IngestionError("Uploaded file exceeds maximum allowed size")
