import pytest

from app.services.chunker import TextChunker


def test_chunker_is_deterministic() -> None:
    chunker = TextChunker(chunk_size=12, chunk_overlap=4)
    text = "abcdefghijklmnopqrstuvwxyz"

    first = chunker.chunk(text)
    second = chunker.chunk(text)

    assert first == second
    assert [chunk.index for chunk in first] == list(range(len(first)))


def test_chunker_respects_size_and_overlap() -> None:
    chunker = TextChunker(chunk_size=10, chunk_overlap=2)
    chunks = chunker.chunk("0123456789ABCDEFG")

    assert len(chunks) >= 2
    assert all(len(chunk.content) <= 10 for chunk in chunks)
    assert chunks[1].metadata["start"] == chunks[0].metadata["start"] + 8


def test_chunker_requires_overlap_less_than_size() -> None:
    with pytest.raises(ValueError):
        TextChunker(chunk_size=10, chunk_overlap=10)
