from app.core.settings import Settings
import pytest
from pydantic import ValidationError


def _production(**overrides):
    values = dict(
        app_env="production",
        cors_origins="https://app.example",
        database_url="postgresql+psycopg://service:injected-secret@managed.example:5432/agentforge",
        llm_provider="openai",
        embedding_provider="openai",
        openai_api_key="ci-test-key-not-used-for-network-calls",
        rate_limit_backend="redis",
        redis_url="rediss://redis.example:6380",
    )
    values.update(overrides)
    return Settings(**values)


def test_settings_validate_chunk_overlap() -> None:
    settings = Settings(chunk_size=100, chunk_overlap=20)
    assert settings.chunk_size == 100
    assert settings.chunk_overlap == 20


def test_settings_content_types_parsing() -> None:
    settings = Settings(supported_content_types="text/plain, application/pdf")
    assert settings.supported_content_type_list == ["text/plain", "application/pdf"]


def test_settings_normalize_supabase_pooler_username() -> None:
    settings = _production(
        database_url="postgresql+psycopg://postgres:secret@aws-0-ap-southeast-2.pooler.supabase.com:5432/postgres",
        supabase_project_ref="walfvdeurvjhhlxyupln",
    )
    assert "postgres.walfvdeurvjhhlxyupln@" in settings.database_url
    assert "sslmode=require" in settings.database_url


def test_settings_normalize_managed_postgres_urls() -> None:
    for source_url in (
        "postgres://service:secret@managed.example:5432/agentforge",
        "postgresql://service:secret@managed.example:5432/agentforge?sslmode=require",
    ):
        settings = _production(database_url=source_url)
        assert settings.database_url.startswith("postgresql+psycopg://")
        assert "managed.example:5432/agentforge" in settings.database_url
        assert "sslmode=require" in settings.database_url or "?" not in settings.database_url


def test_production_requires_explicit_cors_origins_and_selected_provider_credentials() -> None:
    with pytest.raises(ValidationError):
        _production(cors_origins="*")
    with pytest.raises(ValidationError):
        _production(llm_provider="fake")
    with pytest.raises(ValidationError):
        _production(embedding_provider="fake")
    with pytest.raises(ValidationError):
        _production(llm_provider="openai", openai_api_key=None)
    assert _production().cors_origin_list == ["https://app.example"]


def test_agent_limits_are_bounded() -> None:
    with pytest.raises(ValidationError):
        Settings(max_agent_steps=99)
    with pytest.raises(ValidationError):
        Settings(max_tool_calls=99)


def test_phase7_provider_and_resource_bounds() -> None:
    configured = Settings(llm_timeout_seconds=12, llm_max_retries=3, ai_requests_per_minute=7)
    assert configured.llm_timeout_seconds == 12
    assert configured.ai_requests_per_minute == 7
    with pytest.raises(ValidationError):
        Settings(llm_max_retries=4)
    with pytest.raises(ValidationError):
        Settings(llm_timeout_seconds=0)
    with pytest.raises(ValidationError):
        Settings(max_request_body_bytes=0)
