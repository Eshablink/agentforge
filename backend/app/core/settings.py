from __future__ import annotations

from urllib.parse import urlparse

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url

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
    max_request_body_bytes: int = 64 * 1024
    max_extracted_chars: int = 2_000_000
    max_pdf_pages: int = 200
    max_document_chunks: int = 2500
    embedding_batch_size: int = 32
    supported_content_types: str = "application/pdf,text/plain,text/markdown"
    chunk_size: int = 800
    chunk_overlap: int = 120
    embedding_provider: str = "fake"
    embedding_model: str = EMBEDDING_MODEL_DEFAULT
    embedding_dimension: int = EMBEDDING_DIMENSION_DEFAULT
    openai_api_key: str | None = None
    llm_provider: str = "fake"
    llm_model: str = LLM_MODEL_DEFAULT
    llm_timeout_seconds: float = 20.0
    llm_max_retries: int = 2
    session_ttl_seconds: int = 3600
    password_min_length: int = 12
    max_agent_steps: int = 5
    max_tool_calls: int = 4
    max_conversation_messages: int = 20
    max_conversation_context_chars: int = 8000
    rag_top_k_default: int = 5
    rag_top_k_max: int = 10
    rag_candidate_max: int = 30
    rag_min_similarity: float = -1.0
    rag_max_context_chars: int = 6000
    ai_requests_per_minute: int = 20
    auth_attempts_per_minute: int = 10
    max_prompt_chars: int = 5000
    max_stream_duration_seconds: int = 60
    max_stream_output_chars: int = 12000
    rate_limit_backend: str = "memory"
    redis_url: str | None = None
    redis_ssl_ca_cert: str | None = None
    forwarded_allow_ips: str = "127.0.0.1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("app_env")
    @classmethod
    def valid_environment(cls, value: str) -> str:
        if value.lower() not in {"development", "test", "production"}:
            raise ValueError("APP_ENV must be development, test or production")
        return value.lower()

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        """
        Accept standard PostgreSQL URLs from hosted providers.

        SQLAlchemy needs the psycopg driver explicitly, while managed Postgres
        providers commonly expose URLs as postgres:// or postgresql://.
        """
        normalized = str(value).strip()
        for prefix in ("postgres://", "postgresql://"):
            if normalized.startswith(prefix):
                return "postgresql+psycopg://" + normalized.split("://", 1)[1]
        return normalized

    @field_validator("embedding_provider", "llm_provider")
    @classmethod
    def validate_provider(cls, value: str) -> str:
        provider = value.strip().lower()
        if provider not in {"fake", "openai"}:
            raise ValueError("provider must be either 'fake' or 'openai'")
        return provider

    @field_validator("rate_limit_backend")
    @classmethod
    def validate_rate_backend(cls, value: str) -> str:
        if value.lower() not in {"memory", "redis"}:
            raise ValueError("RATE_LIMIT_BACKEND must be memory or redis")
        return value.lower()

    @field_validator("chunk_overlap")
    @classmethod
    def validate_chunk_overlap(cls, value: int, info) -> int:
        if value >= info.data.get("chunk_size", 0):
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        return value

    @field_validator("embedding_dimension")
    @classmethod
    def validate_embedding_dimension(cls, value: int) -> int:
        if value not in SUPPORTED_EMBEDDING_DIMENSIONS:
            raise ValueError("Unsupported embedding dimension")
        return value

    @model_validator(mode="after")
    def validate_security_settings(self):
        if self.session_ttl_seconds < 60 or self.password_min_length < 12:
            raise ValueError("session lifetime and password minimum are below secure defaults")
        if not 1 <= self.max_agent_steps <= 5 or not 1 <= self.max_tool_calls <= 4:
            raise ValueError("agent execution limits exceed safe configured bounds")
        if not 0 <= self.llm_max_retries <= 3 or not 0 < self.llm_timeout_seconds <= 60:
            raise ValueError("provider timeout/retry settings exceed safe bounds")
        limits = (
            self.max_upload_size_bytes,
            self.max_request_body_bytes,
            self.max_conversation_messages,
            self.max_conversation_context_chars,
            self.ai_requests_per_minute,
            self.auth_attempts_per_minute,
            self.max_prompt_chars,
            self.max_stream_duration_seconds,
            self.max_stream_output_chars,
            self.max_extracted_chars,
            self.max_pdf_pages,
            self.max_document_chunks,
            self.embedding_batch_size,
        )
        if any(value < 1 for value in limits) or self.embedding_batch_size > 128 or self.max_document_chunks > 5000 or self.max_extracted_chars > 5_000_000:
            raise ValueError("configured resource limits exceed safe bounds")
        if not (1 <= self.rag_top_k_default <= self.rag_top_k_max <= 10 and self.rag_top_k_max <= self.rag_candidate_max <= 40):
            raise ValueError("RAG candidate and top-k bounds are invalid")
        if not -1 <= self.rag_min_similarity <= 1 or not 200 <= self.rag_max_context_chars <= 12000:
            raise ValueError("RAG similarity or context bounds are invalid")
        if make_url(self.database_url).drivername != "postgresql+psycopg":
            raise ValueError("PostgreSQL with psycopg is required")
        if self.rate_limit_backend == "redis":
            parsed = urlparse(self.redis_url or "")
            if parsed.scheme not in {"redis", "rediss"} or not parsed.hostname:
                raise ValueError("REDIS_URL must be a redis:// or rediss:// URL")
        if self.app_env == "production":
            explicit = self.model_fields_set
            if not {"database_url", "cors_origins", "llm_provider", "embedding_provider", "rate_limit_backend"}.issubset(explicit):
                raise ValueError("production requires explicit database, CORS, provider and rate limiter settings")
            db = make_url(self.database_url)
            if not db.host or not db.password or db.password == "agentforge" or db.host in {"localhost", "db", "127.0.0.1"}:
                raise ValueError("production DATABASE_URL cannot use development credentials or host")
            if not self.cors_origin_list or any(not origin.startswith("https://") or "*" in origin for origin in self.cors_origin_list):
                raise ValueError("production CORS_ORIGINS must be explicit HTTPS origins")
            if self.rate_limit_backend != "redis":
                raise ValueError("production requires a shared rate limiter")
            redis = urlparse(self.redis_url or "")
            is_render_internal_redis = (
                redis.scheme == "redis"
                and redis.hostname is not None
                and redis.hostname.startswith("red-")
                and redis.port in {None, 6379}
                and not redis.username
                and not redis.password
            )
            if redis.scheme != "rediss" and not is_render_internal_redis:
                raise ValueError(
                    "production REDIS_URL must use TLS (rediss://), or the private Render Key Value endpoint"
                )
            if self.llm_provider == "fake" or self.embedding_provider == "fake":
                raise ValueError("production requires real LLM and embedding providers")
            if self.openai_api_key is None or not self.openai_api_key.strip():
                raise ValueError("OPENAI_API_KEY required for selected production provider")
            if "*" in self.forwarded_allow_ips:
                raise ValueError("production forwarded proxy trust cannot be wildcard")
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    @property
    def supported_content_type_list(self) -> list[str]:
        return [item.strip() for item in self.supported_content_types.split(",") if item.strip()]


def get_settings() -> Settings:
    return Settings()
