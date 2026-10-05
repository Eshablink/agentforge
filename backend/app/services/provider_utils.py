"""Bounded retry and error-normalization for external AI providers.

Keeps provider calls bounded (explicit timeout, finite retries) and maps raw
exceptions to the normalized :mod:`app.services.provider_errors` taxonomy so
secrets and response bodies never leak into logs or client responses.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import TypeVar

from app.services.provider_errors import (
    ProviderAuth,
    ProviderInvalidResponse,
    ProviderRateLimited,
    ProviderTimeout,
    ProviderUnavailable,
)

T = TypeVar("T")

# Retry only these transient, idempotent categories.
_RETRYABLE = {ProviderTimeout, ProviderRateLimited, ProviderUnavailable}


def classify(exc: Exception) -> Exception:
    """Normalize a raw provider exception into a safe taxonomy instance."""
    name = type(exc).__name__.lower()
    if "timeout" in name or "timed" in name:
        return ProviderTimeout("The AI provider timed out.")
    if "rate" in name or "429" in str(exc) or "quota" in name:
        return ProviderRateLimited("The AI provider rate limit was reached.")
    if "auth" in name or "401" in str(exc) or "permission" in name:
        return ProviderAuth("The AI provider credentials are invalid.")
    if "invalid" in name or "json" in name or "decode" in name:
        return ProviderInvalidResponse("The AI provider returned an invalid response.")
    return ProviderUnavailable("The AI provider is unavailable.")


def run_bounded(
    fn: Callable[[], T],
    *,
    timeout_seconds: float,
    max_retries: int,
    backoff_seconds: float = 0.2,
) -> T:
    """Call ``fn`` with a bounded timeout and finite retries on transient errors."""
    deadline = time.monotonic() + max(timeout_seconds, 0.0)
    last_exc: Exception | None = None
    attempts = max_retries + 1
    for attempt in range(attempts):
        try:
            # Cooperative deadline check cannot preempt a blocking library call,
            # so we rely on provider-level timeout settings plus this guard.
            if time.monotonic() > deadline:
                raise ProviderTimeout("The AI provider timed out.")
            return fn()
        except Exception as exc:  # noqa: BLE001 - normalized below
            normalized = classify(exc)
            last_exc = normalized
            if attempt >= max_retries or type(normalized) not in _RETRYABLE:
                break
            time.sleep(backoff_seconds * (2 ** attempt))
    if last_exc is not None:
        raise last_exc
    raise ProviderUnavailable("The AI provider is unavailable.")
