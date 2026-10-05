from __future__ import annotations

import hashlib
from collections.abc import Iterable

from openai import OpenAI

from app.core.settings import get_settings
from app.services.provider_errors import ProviderError
from app.services.provider_utils import run_bounded


class EmbeddingError(Exception):
    """Raised when embedding generation fails."""


class EmbeddingService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.provider = self.settings.embedding_provider.lower()
        self._client: OpenAI | None = None
        if self.provider == "openai":
            if not self.settings.openai_api_key:
                raise EmbeddingError("OPENAI_API_KEY is required when embedding provider is openai")
            self._client = OpenAI(api_key=self.settings.openai_api_key, timeout=self.settings.llm_timeout_seconds, max_retries=0)

    def embed_texts(self, texts: Iterable[str]) -> list[list[float]]:
        values = [value.strip() for value in texts if value and value.strip()]
        if not values:
            return []
        if self.provider == "openai":
            assert self._client is not None
            def _call():
                return self._client.embeddings.create(model=self.settings.embedding_model, input=values)
            try:
                response = run_bounded(_call, timeout_seconds=self.settings.llm_timeout_seconds, max_retries=self.settings.llm_max_retries)
            except ProviderError as exc:
                raise EmbeddingError(str(exc)) from exc
            vectors = [item.embedding for item in response.data]
        else:
            vectors = [self._fake_embedding(value) for value in values]
        for vector in vectors:
            if len(vector) != self.settings.embedding_dimension:
                raise EmbeddingError(f"Invalid embedding dimension {len(vector)}; expected {self.settings.embedding_dimension}")
        return vectors

    def _fake_embedding(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        vector: list[float] = []
        for index in range(self.settings.embedding_dimension):
            byte = digest[index % len(digest)]
            normalized = (byte / 255.0) * 2 - 1
            vector.append(round(normalized, 6))
        return vector
