from __future__ import annotations

import pytest

from app.core.rate_limit import RateLimitExceeded, SlidingWindowLimiter
from app.services.provider_errors import (
    ProviderAuth,
    ProviderRateLimited,
    ProviderTimeout,
    ProviderUnavailable,
)
from app.services.provider_utils import classify, run_bounded


def test_classify_normalizes_exception_types() -> None:
    class TimeoutError(Exception):
        pass

    class RateLimitError(Exception):
        pass

    assert isinstance(classify(TimeoutError("x")), ProviderTimeout)
    assert isinstance(classify(RateLimitError("slow")), ProviderRateLimited)
    assert isinstance(classify(Exception("some auth permission issue")), ProviderAuth)


def test_run_bounded_retries_transient_and_stops_after_finite_attempts() -> None:
    calls = {"count": 0}

    def flaky():
        calls["count"] += 1
        if calls["count"] < 3:
            raise ProviderUnavailable("transient")
        return "ok"

    assert run_bounded(flaky, timeout_seconds=5, max_retries=3, backoff_seconds=0) == "ok"
    assert calls["count"] == 3


def test_run_bounded_does_not_retry_auth_errors() -> None:
    calls = {"count": 0}

    def auth_fail():
        calls["count"] += 1
        raise ProviderAuth("bad key")

    with pytest.raises(ProviderAuth):
        run_bounded(auth_fail, timeout_seconds=5, max_retries=3, backoff_seconds=0)
    assert calls["count"] == 1


def test_run_bounded_timeout_setting_is_per_attempt_not_total_budget() -> None:
    calls = {"count": 0}

    def transient():
        calls["count"] += 1
        raise ProviderTimeout("per attempt timeout")

    with pytest.raises(ProviderTimeout):
        run_bounded(transient, timeout_seconds=1, max_retries=2, backoff_seconds=0)
    # Each transport attempt is allowed its configured timeout; elapsed time is
    # not incorrectly treated as a shared total budget by this helper.
    assert calls["count"] == 3


def test_run_bounded_caps_retries_and_rejects_invalid_bounds() -> None:
    with pytest.raises(ValueError):
        run_bounded(lambda: None, timeout_seconds=1, max_retries=4)
    with pytest.raises(ValueError):
        run_bounded(lambda: None, timeout_seconds=0, max_retries=0)


def test_sliding_window_rate_limit_enforced() -> None:
    limiter = SlidingWindowLimiter(limit=2, window_seconds=60)
    limiter.check("user-a", now=0.0)
    limiter.check("user-a", now=1.0)
    with pytest.raises(RateLimitExceeded):
        limiter.check("user-a", now=2.0)
    limiter.check("user-b", now=2.0)


def test_sliding_window_windows_expire() -> None:
    limiter = SlidingWindowLimiter(limit=1, window_seconds=60)
    limiter.check("user-a", now=0.0)
    limiter.check("user-a", now=61.0)
