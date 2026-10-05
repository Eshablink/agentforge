from datetime import date
from uuid import uuid4

from app.core.settings import Settings
import pytest
from pydantic import ValidationError


def test_settings_validate_chunk_overlap() -> None:
    settings = Settings(chunk_size=100, chunk_overlap=20)
    assert settings.chunk_size == 100
    assert settings.chunk_overlap == 20


def test_settings_content_types_parsing() -> None:
    settings = Settings(supported_content_types="text/plain, application/pdf")
    assert settings.supported_content_type_list == ["text/plain", "application/pdf"]


def test_production_requires_explicit_cors_origins_and_selected_provider_credentials() -> None:
    with pytest.raises(ValidationError):
        Settings(app_env="production", cors_origins="*")
    with pytest.raises(ValidationError):
        Settings(app_env="production", cors_origins="https://app.example", llm_provider="openai", openai_api_key=None)
    production = Settings(app_env="production", cors_origins="https://app.example", llm_provider="fake")
    assert production.cors_origin_list == ["https://app.example"]


def test_agent_limits_are_bounded() -> None:
    with pytest.raises(ValidationError):
        Settings(max_agent_steps=99)
    with pytest.raises(ValidationError):
        Settings(max_tool_calls=99)


def test_phase7_provider_and_resource_bounds() -> None:
    configured = Settings(llm_timeout_seconds=12, llm_max_retries=3, ai_requests_per_minute=7)
    assert configured.llm_timeout_seconds == 12
    assert configured.llm_max_retries == 3
    assert configured.ai_requests_per_minute == 7
    with pytest.raises(ValidationError):
        Settings(llm_max_retries=4)
    with pytest.raises(ValidationError):
        Settings(llm_timeout_seconds=0)
    with pytest.raises(ValidationError):
        Settings(max_request_body_bytes=0)
