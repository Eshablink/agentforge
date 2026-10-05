"""Process-local sliding-window limiter for expensive AI endpoints.

This is an intentionally small single-process guard, not a distributed quota.
Use a gateway/shared store when running multiple workers or replicas.
"""

from __future__ import annotations

import threading
import time
from collections import deque


class RateLimitExceeded(Exception):
    """Raised when a client exceeds an in-process request window."""


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
                raise RateLimitExceeded("AI request rate limit exceeded")
            events.append(current)
            # Bound stale keys under client churn.
            if len(self._events) > 10000:
                stale = [item for item, stamps in self._events.items() if not stamps or stamps[-1] <= cutoff]
                for item in stale[:5000]:
                    self._events.pop(item, None)
