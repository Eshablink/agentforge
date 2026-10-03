import io

import pytest
from fastapi import UploadFile
from fpdf import FPDF

from app.services.extractor import DocumentExtractor, ExtractionError


def _upload_file(name: str, content: bytes, content_type: str) -> UploadFile:
    return UploadFile(filename=name, file=io.BytesIO(content), headers={"content-type": content_type})


def test_extract_txt_document() -> None:
    extractor = DocumentExtractor()
    file = _upload_file("note.txt", b"hello\nworld", "text/plain")

    result = extractor.extract(file)

    assert result.text == "hello\nworld"
    assert result.metadata["format"] == "text"


def test_extract_markdown_document() -> None:
    extractor = DocumentExtractor()
    file = _upload_file("note.md", b"# Title\n\nBody", "text/markdown")

    result = extractor.extract(file)

    assert "Title" in result.text
    assert result.metadata["format"] == "markdown"


def test_extract_pdf_document() -> None:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)
    pdf.multi_cell(0, 10, "PDF content for extractor")
    data = pdf.output(dest="S")
    if isinstance(data, str):
        pdf_bytes = data.encode("latin-1")
    else:
        pdf_bytes = bytes(data)

    extractor = DocumentExtractor()
    file = _upload_file("doc.pdf", pdf_bytes, "application/pdf")

    result = extractor.extract(file)

    assert "PDF content" in result.text
    assert result.metadata["format"] == "pdf"


def test_extract_rejects_empty_document() -> None:
    extractor = DocumentExtractor()
    file = _upload_file("empty.txt", b"", "text/plain")

    with pytest.raises(ExtractionError):
        extractor.extract(file)


def test_extract_rejects_unsupported_content_type() -> None:
    extractor = DocumentExtractor()
    file = _upload_file("data.csv", b"a,b", "text/csv")

    with pytest.raises(ExtractionError):
        extractor.extract(file)
