from __future__ import annotations

import pytest

from app.core.rate_limit import (RateLimitExceeded, RateLimitUnavailable, RedisLimiter,
                                 SlidingWindowLimiter, build_limiters)
from app.core.settings import Settings


class FakeRedis:
    def __init__(self):
        self.counts = {}
        self.keys = []
    def eval(self, script, nkeys, key, ttl):
        self.keys.append(key)
        self.counts[key] = self.counts.get(key, 0) + 1
        return self.counts[key]


def test_shared_limiter_is_atomic_per_user_and_namespaced():
    redis = FakeRedis()
    limiter = RedisLimiter(redis, 2, 60, "ai")
    limiter.check("user-a")
    limiter.check("user-b")
    limiter.check("user-a")
    with pytest.raises(RateLimitExceeded):
        limiter.check("user-a")
    assert redis.keys[0] != redis.keys[1]
    assert all(key.startswith("agentforge:ai:") for key in redis.keys)


def test_shared_store_failure_fails_closed():
    class BrokenRedis:
        def eval(self, *args):
            raise ConnectionError("private Redis endpoint")
    limiter = RedisLimiter(BrokenRedis(), 1, 60, "ai")
    with pytest.raises(RateLimitUnavailable, match="Rate limiter unavailable"):
        limiter.check("opaque-id")


def test_development_uses_local_limiters_and_production_requires_shared():
    ai, auth = build_limiters(Settings(app_env="development", rate_limit_backend="memory"))
    assert isinstance(ai, SlidingWindowLimiter)
    assert isinstance(auth, SlidingWindowLimiter)
    production = Settings(app_env="production", database_url="postgresql+psycopg://service:secret@managed.example:5432/app",
                          cors_origins="https://app.example", llm_provider="fake", embedding_provider="fake",
                          rate_limit_backend="redis", redis_url="rediss://redis.example:6380")
    ai, auth = build_limiters(production, redis_client=FakeRedis())
    assert isinstance(ai, RedisLimiter)
    assert isinstance(auth, RedisLimiter)
