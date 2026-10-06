from __future__ import annotations

import io

import pytest
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.settings import Settings
from app.services.extractor import DocumentExtractor, ExtractionError, ExtractedDocument
from app.services.ingestion_service import DocumentIngestionService, IngestionError
from app.services.chunker import ChunkResult


def test_extractor_rejects_excess_text_without_materializing_all(monkeypatch):
    monkeypatch.setattr("app.services.extractor.get_settings", lambda: Settings(max_extracted_chars=10))
    upload = UploadFile(filename="large.txt", file=io.BytesIO(b"a" * 11))
    with pytest.raises(ExtractionError, match="extracted text size"):
        DocumentExtractor().extract(upload)


def test_ingestion_rejects_excess_chunks_before_embedding(monkeypatch):
    service = DocumentIngestionService.__new__(DocumentIngestionService)
    service.settings = Settings(max_document_chunks=1, max_extracted_chars=1000)
    service.chunker = type("Chunker", (), {"chunk_size": 5, "chunk_overlap": 0,
        "chunk": lambda self, text: (_ for _ in ()).throw(AssertionError("chunk materialized"))})()
    service.extractor = type("Extractor", (), {"extract": lambda self, file: ExtractedDocument(text="x" * 40, metadata={})})()
    service.db = type("DB", (), {"rollback": lambda self: None})()
    service.embedding_service = type("Embed", (), {"embed_texts": lambda self, texts: (_ for _ in ()).throw(AssertionError("embedded"))})()
    with pytest.raises(IngestionError, match="maximum chunk count"):
        service.ingest(UploadFile(filename="data.txt", file=io.BytesIO(b"x" * 40), headers={"content-type": "text/plain"}))
