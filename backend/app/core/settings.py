from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.constants import (
    EMBEDDING_DIMENSION_DEFAULT,
    EMBEDDING_MODEL_DEFAULT,
    LLM_MODEL_DEFAULT,
    SUPPORTED_EMBEDDING_DIMENSIONS,
)


class Settings(BaseSettings):
    app_name: str = "AgentForge API"
    app_env: str = "development"
    app_version: str = "0.1.0"
    api_prefix: str = ""
    cors_origins: str = "http://localhost:5173"

    database_url: str = "postgresql+psycopg://agentforge:agentforge@localhost:5432/agentforge"

    max_upload_size_bytes: int = 10 * 1024 * 1024
    supported_content_types: str = "application/pdf,text/plain,text/markdown"

    chunk_size: int = 800
    chunk_overlap: int = 120

    embedding_provider: str = "fake"
    embedding_model: str = EMBEDDING_MODEL_DEFAULT
    embedding_dimension: int = EMBEDDING_DIMENSION_DEFAULT
    openai_api_key: str | None = None

    llm_provider: str = "fake"
    llm_model: str = LLM_MODEL_DEFAULT
    auth_secret: str = "development-only-change-me"
    session_ttl_seconds: int = 3600
    password_min_length: int = 12
    max_agent_steps: int = 5
    max_tool_calls: int = 4
    max_conversation_messages: int = 20
    max_conversation_context_chars: int = 8000

    rag_top_k_default: int = 5
    rag_top_k_max: int = 10

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    @field_validator("chunk_overlap")
    @classmethod
    def validate_chunk_overlap(cls, value: int, info) -> int:
        chunk_size = info.data.get("chunk_size", 0)
        if value >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        return value

    @field_validator("embedding_dimension")
    @classmethod
    def validate_embedding_dimension(cls, value: int) -> int:
        if value not in SUPPORTED_EMBEDDING_DIMENSIONS:
            supported = ", ".join(str(item) for item in sorted(SUPPORTED_EMBEDDING_DIMENSIONS))
            raise ValueError(f"Unsupported embedding_dimension {value}. Supported dimensions: {supported}")
        return value

    @field_validator("auth_secret")
    @classmethod
    def validate_auth_secret(cls, value: str, info) -> str:
        env_name = str(info.data.get("app_env", "development")).lower()
        if env_name == "production" and (len(value) < 32 or value == "development-only-change-me"):
            raise ValueError("AUTH_SECRET must be a unique value of at least 32 characters in production")
        return value

    @field_validator("session_ttl_seconds", "max_agent_steps", "max_tool_calls", "max_conversation_messages", "max_conversation_context_chars")
    @classmethod
    def positive_limits(cls, value: int) -> int:
        if value < 1:
            raise ValueError("configured limits must be positive")
        return value

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    @property
    def supported_content_type_list(self) -> list[str]:
        return [item.strip() for item in self.supported_content_types.split(",") if item.strip()]


def get_settings() -> Settings:
    return Settings()
