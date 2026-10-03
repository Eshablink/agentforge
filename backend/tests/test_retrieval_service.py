from __future__ import annotations

from app.services.retrieval_service import RetrievedChunk


def test_retrieved_chunk_dataclass_fields() -> None:
    chunk = RetrievedChunk(
        chunk_id="c1",
        document_id="d1",
        filename="report.txt",
        chunk_index=2,
        content="value",
        similarity=0.87,
    )

    assert chunk.chunk_id == "c1"
    assert chunk.document_id == "d1"
    assert chunk.filename == "report.txt"
    assert chunk.chunk_index == 2
    assert chunk.content == "value"
    assert chunk.similarity == 0.87
