"""Atomic shared-store or local fixed-window request protection.

Redis uses a single atomic Lua operation (INCR + EXPIRE); backend failure
raises RateLimitUnavailable. Production never silently falls back to memory.
"""
from __future__ import annotations

import threading
import time
from collections import deque
from typing import Protocol

from app.core.settings import get_settings


class RateLimitExceeded(Exception):
    pass


class RateLimitUnavailable(Exception):
    pass


class Limiter(Protocol):
    def check(self, key: str) -> None: ...


class SlidingWindowLimiter:
    def __init__(self, limit: int, window_seconds: int) -> None:
        if limit < 1 or window_seconds < 1:
            raise ValueError("rate limit and window must be positive")
        self.limit = limit
        self.window_seconds = window_seconds
        self._events: dict[str, deque[float]] = {}
        self._lock = threading.Lock()

    def check(self, key: str, *, now: float | None = None) -> None:
        current = time.monotonic() if now is None else now
        cutoff = current - self.window_seconds
        with self._lock:
            events = self._events.setdefault(key, deque())
            while events and events[0] <= cutoff:
                events.popleft()
            if len(events) >= self.limit:
                raise RateLimitExceeded("Request rate limit exceeded")
            events.append(current)
            if len(self._events) > 10000:
                for item, stamps in list(self._events.items())[:5000]:
                    if not stamps or stamps[-1] <= cutoff:
                        self._events.pop(item, None)


class RedisLimiter:
    """Atomic fixed window with TTL; redis client is injected for tests."""
    _SCRIPT = """local n = redis.call('INCR', KEYS[1])
if n == 1 then redis.call('EXPIRE', KEYS[1], ARGV[1]) end
return n"""

    def __init__(self, client, limit: int, window_seconds: int, namespace: str) -> None:
        if limit < 1 or window_seconds < 1:
            raise ValueError("rate limit and window must be positive")
        self.client, self.limit, self.window_seconds = client, limit, window_seconds
        self.namespace = namespace

    def check(self, key: str) -> None:
        bucket = int(time.time()) // self.window_seconds
        try:
            count = int(
                self.client.eval(
                    self._SCRIPT,
                    1,
                    f"agentforge:{self.namespace}:{key}:{bucket}",
                    self.window_seconds * 2,
                )
            )
        except Exception as exc:
            raise RateLimitUnavailable("Rate limiter unavailable") from exc
        if count > self.limit:
            raise RateLimitExceeded("Request rate limit exceeded")


def build_limiters(settings=None, redis_client=None) -> tuple[Limiter, Limiter]:
    settings = settings or get_settings()
    if settings.rate_limit_backend == "memory":
        if settings.app_env == "production":
            raise ValueError("Production requires shared rate limiting")
        return (
            SlidingWindowLimiter(settings.ai_requests_per_minute, 60),
            SlidingWindowLimiter(settings.auth_attempts_per_minute, 60),
        )
    if redis_client is None:
        from redis import Redis

        redis_kwargs = {
            "socket_timeout": 2,
            "socket_connect_timeout": 2,
            "decode_responses": True,
        }
        if settings.redis_ssl_ca_cert:
            redis_kwargs.update(
                {
                    "ssl_ca_certs": settings.redis_ssl_ca_cert,
                    "ssl_cert_reqs": "required",
                }
            )
        redis_client = Redis.from_url(settings.redis_url, **redis_kwargs)
    return (
        RedisLimiter(redis_client, settings.ai_requests_per_minute, 60, "ai"),
        RedisLimiter(redis_client, settings.auth_attempts_per_minute, 60, "auth"),
    )


ai_request_limiter, auth_request_limiter = build_limiters()
