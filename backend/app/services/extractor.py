from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from fastapi import UploadFile
from pypdf import PdfReader


class ExtractionError(Exception):
    """Raised when document extraction fails."""


@dataclass(slots=True)
class ExtractedDocument:
    text: str
    metadata: dict


class DocumentExtractor:
    def extract(self, file: UploadFile) -> ExtractedDocument:
        content_type = (file.content_type or "").lower()
        data = file.file.read()

        if not data:
            raise ExtractionError("Uploaded file is empty")

        if content_type == "application/pdf" or file.filename.lower().endswith(".pdf"):
            return self._extract_pdf(data)
        if content_type in {"text/plain", "text/markdown"} or file.filename.lower().endswith(
            (".txt", ".md")
        ):
            return self._extract_text(data)

        raise ExtractionError("Unsupported file type. Supported: PDF, TXT, Markdown")

    def _extract_pdf(self, data: bytes) -> ExtractedDocument:
        try:
            from io import BytesIO

            reader = PdfReader(BytesIO(data))
            texts = [(page.extract_text() or "").strip() for page in reader.pages]
            full_text = "\n\n".join([text for text in texts if text])
        except Exception as exc:  # pragma: no cover - defensive
            raise ExtractionError("Failed to parse PDF file") from exc

        if not full_text.strip():
            raise ExtractionError("No extractable text found in PDF")

        return ExtractedDocument(text=full_text, metadata={"page_count": len(reader.pages), "format": "pdf"})

    def _extract_text(self, data: bytes) -> ExtractedDocument:
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

        suffix = Path("x.md").suffix
        format_name = "markdown" if suffix == ".md" else "text"
        return ExtractedDocument(text=normalized, metadata={"format": format_name})
