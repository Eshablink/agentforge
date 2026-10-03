import pytest

from app.services.embedding_service import EmbeddingError, EmbeddingService


def test_fake_embedding_provider_is_deterministic() -> None:
    service = EmbeddingService()

    vectors_first = service.embed_texts(["alpha", "beta"])
    vectors_second = service.embed_texts(["alpha", "beta"])

    assert vectors_first == vectors_second
    assert len(vectors_first[0]) == service.settings.embedding_dimension


def test_embedding_dimension_validation() -> None:
    service = EmbeddingService()

    def bad_fake(_: str) -> list[float]:
        return [0.1, 0.2]

    service._fake_embedding = bad_fake  # type: ignore[method-assign]

    with pytest.raises(EmbeddingError):
        service.embed_texts(["text"])
