from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.core.settings import Settings


def _production(**overrides):
    data = dict(
        app_env="production",
        database_url="postgresql+psycopg://service:injected-secret@managed-db.example:5432/agentforge",
        cors_origins="https://app.example",
        llm_provider="openai",
        embedding_provider="openai",
        openai_api_key="ci-test-key-not-used-for-network-calls",
        rate_limit_backend="redis",
        redis_url="rediss://redis.example:6380/0",
    )
    data.update(overrides)
    return Settings(**data)


def test_production_configuration_requires_explicit_safe_dependencies():
    with pytest.raises(ValidationError):
        Settings(app_env="production")
    assert _production().app_env == "production"
    for values in (
        {"cors_origins": "*"},
        {"cors_origins": "http://app.example"},
        {"database_url": "postgresql+psycopg://agentforge:agentforge@localhost:5432/agentforge"},
        {"rate_limit_backend": "memory"},
        {"redis_url": None},
        {"redis_url": "redis://redis.example:6379"},
        {"redis_url": "redis://red-not-render.example:6379"},
        {"llm_provider": "fake"},
        {"embedding_provider": "fake"},
        {"openai_api_key": None},
        {"forwarded_allow_ips": "*"},
    ):
        with pytest.raises(ValidationError):
            _production(**values)


def test_test_and_dev_allow_local_fake_providers_but_not_sqlite():
    assert Settings(app_env="test").llm_provider == "fake"
    assert Settings(app_env="development").rate_limit_backend == "memory"
    with pytest.raises(ValidationError):
        Settings(database_url="sqlite:///test.sqlite3")
    with pytest.raises(ValidationError):
        Settings(max_document_chunks=6000)


def test_production_accepts_private_render_key_value_endpoint() -> None:
    settings = _production(
        redis_url="redis://red-db34h1l9fdbs739urr8g:6379",
        render_key_value_id="red-db34h1l9fdbs739urr8g",
    )
    assert settings.redis_url == "redis://red-db34h1l9fdbs739urr8g:6379"


def test_production_rejects_unbound_private_redis_endpoint() -> None:
    with pytest.raises(ValidationError):
        _production(
            redis_url="redis://red-db34h1l9fdbs739urr8g:6379",
            render_key_value_id="red-other-resource",
        )
