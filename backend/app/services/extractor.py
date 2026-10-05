from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from fastapi import UploadFile
from pypdf import PdfReader

from app.core.settings import get_settings


class ExtractionError(Exception):
    """Raised when document extraction fails."""


@dataclass(slots=True)
class ExtractedDocument:
    text: str
    metadata: dict


class DocumentExtractor:
    def extract(self, file: UploadFile) -> ExtractedDocument:
        filename = (file.filename or "").lower()
        content_type = (file.content_type or "").lower()
        settings = get_settings()
        # Limit bytes before decoding even when extractor is called directly.
        data = file.file.read(settings.max_upload_size_bytes + 1)
        if len(data) > settings.max_upload_size_bytes:
            raise ExtractionError("Uploaded file exceeds maximum allowed size")
        if not data:
            raise ExtractionError("Uploaded file is empty")
        if content_type == "application/pdf" or filename.endswith(".pdf"):
            return self._extract_pdf(data)
        if content_type in {"text/plain", "text/markdown"} or filename.endswith((".txt", ".md")):
            return self._extract_text(data, filename)
        raise ExtractionError("Unsupported file type. Supported: PDF, TXT, Markdown")

    def _extract_pdf(self, data: bytes) -> ExtractedDocument:
        from io import BytesIO
        settings = get_settings()
        try:
            reader = PdfReader(BytesIO(data))
            if len(reader.pages) > settings.max_pdf_pages:
                raise ExtractionError("PDF exceeds maximum allowed page count")
            texts = []
            total = 0
            for page in reader.pages:
                text = (page.extract_text() or "").strip()
                total += len(text)
                if total > settings.max_extracted_chars:
                    raise ExtractionError("Document exceeds maximum extracted text size")
                if text:
                    texts.append(text)
            full_text = "\n\n".join(texts)
        except ExtractionError:
            raise
        except Exception as exc:
            raise ExtractionError("Failed to parse PDF file") from exc
        if not full_text.strip():
            raise ExtractionError("No extractable text found in PDF")
        return ExtractedDocument(text=full_text, metadata={"page_count": len(reader.pages), "format": "pdf"})

    def _extract_text(self, data: bytes, filename: str) -> ExtractedDocument:
        settings = get_settings()
        if len(data) > settings.max_extracted_chars:
            raise ExtractionError("Document exceeds maximum extracted text size")
        for encoding in ("utf-8", "latin-1"):
            try:
                text = data.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            raise ExtractionError("Unable to decode text file")
        normalized = text.replace("\r\n", "\n").strip()
        if not normalized:
            raise ExtractionError("Document text is empty")
        if len(normalized) > settings.max_extracted_chars:
            raise ExtractionError("Document exceeds maximum extracted text size")
        suffix = Path(filename).suffix
        format_name = "markdown" if suffix == ".md" else "text"
        return ExtractedDocument(text=normalized, metadata={"format": format_name})
