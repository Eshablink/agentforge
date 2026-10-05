"""Bounded retry and error normalization for external AI providers.

``timeout_seconds`` is a PER-ATTEMPT timeout, not a total operation budget.
The callable must enforce it at the transport/client layer (the OpenAI clients
are constructed with this timeout). This helper enforces a finite retry count
and bounded backoff; it cannot preempt an arbitrary blocking Python callable.

Therefore the maximum operation duration is approximately
``(max_retries + 1) * timeout_seconds + bounded_backoff`` when the wrapped
provider honors its configured per-attempt timeout.
"""

from __future__ import annotations

import math
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
_RETRYABLE = {ProviderTimeout, ProviderRateLimited, ProviderUnavailable}
_MAX_RETRIES = 3
_MAX_BACKOFF_SECONDS = 2.0


def classify(exc: Exception) -> Exception:
    """Normalize raw provider errors without retaining raw exception text."""
    name = type(exc).__name__.lower()
    message = str(exc).lower()
    if "timeout" in name or "timed" in name:
        return ProviderTimeout("The AI provider timed out.")
    if "rate" in name or "429" in message or "quota" in name:
        return ProviderRateLimited("The AI provider rate limit was reached.")
    if "auth" in name or "401" in message or "permission" in message:
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
    """Retry a client-time-bounded call a finite number of times.

    ``timeout_seconds`` documents and matches the transport's per-attempt
    timeout. The helper deliberately does not run arbitrary callables in a
    thread/process just to interrupt them. Provider constructors must set their
    own request timeout to this value.
    """
    if not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
        raise ValueError("per-attempt timeout_seconds must be positive and finite")
    if not 0 <= max_retries <= _MAX_RETRIES:
        raise ValueError(f"max_retries must be between 0 and {_MAX_RETRIES}")
    if not math.isfinite(backoff_seconds) or backoff_seconds < 0:
        raise ValueError("backoff_seconds must be non-negative and finite")

    last_exc: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001 - normalized below
            normalized = classify(exc)
            last_exc = normalized
            if attempt >= max_retries or type(normalized) not in _RETRYABLE:
                break
            delay = min(backoff_seconds * (2 ** attempt), _MAX_BACKOFF_SECONDS)
            time.sleep(delay)
    if last_exc is not None:
        raise last_exc
    raise ProviderUnavailable("The AI provider is unavailable.")
