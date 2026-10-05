"""Normalized provider error taxonomy for bounded, secret-safe failures.

External provider failures (OpenAI, embeddings, decision providers) are mapped
to a small, stable set of categories so callers and logs never leak raw
exception text, API keys, or chain-of-thought. Category values are safe to expose
to clients; the underlying detail is retained only for server-side diagnosis
and is never placed in structured logs or responses.
"""

from __future__ import annotations


class ProviderError(Exception):
    """Base class for normalized provider failures.

    ``category`` is a stable, safe, user-exposable machine-readable code.
    ``message`` is a short safe human-readable description. ``context`` may hold
    bounded, safe operational metadata (never secrets or prompt text).
    """

    category = "provider_error"

    def __init__(self, message: str, *, category: str | None = None, **context: object) -> None:
        super().__init__(message)
        self.message = message
        if category is not None:
            self.category = category
        self.context = context

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.message


class ProviderTimeout(ProviderError):
    category = "provider_timeout"


class ProviderRateLimited(ProviderError):
    category = "provider_rate_limited"


class ProviderAuth(ProviderError):
    category = "provider_auth"


class ProviderUnavailable(ProviderError):
    category = "provider_unavailable"


class ProviderInvalidResponse(ProviderError):
    category = "provider_invalid_response"


class ProviderConfig(ProviderError):
    category = "provider_config"


# Safe fallback message used whenever a raw exception cannot be trusted.
SAFE_PROVIDER_MESSAGE = "The AI provider is currently unavailable. Please try again."
