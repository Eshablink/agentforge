from __future__ import annotations

from dataclasses import dataclass

from app.core.settings import get_settings


@dataclass(slots=True)
class ChunkResult:
    index: int
    content: str
    metadata: dict


class TextChunker:
    def __init__(self, chunk_size: int | None = None, chunk_overlap: int | None = None) -> None:
        settings = get_settings()
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap if chunk_overlap is not None else settings.chunk_overlap
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

    def chunk(self, text: str) -> list[ChunkResult]:
        normalized = text.strip()
        if not normalized:
            return []

        chunks: list[ChunkResult] = []
        step = self.chunk_size - self.chunk_overlap
        index = 0
        start = 0

        while start < len(normalized):
            end = min(start + self.chunk_size, len(normalized))
            value = normalized[start:end].strip()
            if value:
                chunks.append(
                    ChunkResult(
                        index=index,
                        content=value,
                        metadata={"start": start, "end": end, "length": len(value)},
                    )
                )
                index += 1
            if end >= len(normalized):
                break
            start += step

        return chunks
