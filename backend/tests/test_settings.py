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


def test_production_requires_secret_and_explicit_cors_origins() -> None:
    with pytest.raises(ValidationError):
        Settings(app_env="production", auth_secret=None)
    with pytest.raises(ValidationError):
        Settings(app_env="production", auth_secret="x" * 40, cors_origins="*")
    production = Settings(app_env="production", auth_secret="x" * 40, cors_origins="https://app.example")
    assert production.cors_origin_list == ["https://app.example"]


def test_agent_limits_are_bounded() -> None:
    with pytest.raises(ValidationError):
        Settings(max_agent_steps=99)
    with pytest.raises(ValidationError):
        Settings(max_tool_calls=99)
