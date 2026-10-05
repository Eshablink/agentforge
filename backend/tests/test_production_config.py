from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.core.settings import Settings


def _production(**overrides):
    data = dict(app_env="production", database_url="postgresql+psycopg://service:injected-secret@managed-db.example:5432/agentforge",
                cors_origins="https://app.example", llm_provider="fake", embedding_provider="fake",
                rate_limit_backend="redis", redis_url="rediss://redis.example:6380/0")
    data.update(overrides)
    return Settings(**data)


def test_production_configuration_requires_explicit_safe_dependencies():
    with pytest.raises(ValidationError):
        Settings(app_env="production")
    assert _production().app_env == "production"
    with pytest.raises(ValidationError):
        _production(cors_origins="*")
    with pytest.raises(ValidationError):
        _production(cors_origins="http://app.example")
    with pytest.raises(ValidationError):
        _production(database_url="postgresql+psycopg://agentforge:agentforge@localhost:5432/agentforge")
    with pytest.raises(ValidationError):
        _production(rate_limit_backend="memory")
    with pytest.raises(ValidationError):
        _production(redis_url=None)
    with pytest.raises(ValidationError):
        _production(llm_provider="openai", openai_api_key=None)
    with pytest.raises(ValidationError):
        _production(embedding_provider="openai", openai_api_key=None)


def test_test_and_dev_allow_local_fake_providers_but_not_sqlite():
    assert Settings(app_env="test").llm_provider == "fake"
    assert Settings(app_env="development").rate_limit_backend == "memory"
    with pytest.raises(ValidationError):
        Settings(database_url="sqlite:///test.sqlite3")
    with pytest.raises(ValidationError):
        Settings(max_document_chunks=6000)
