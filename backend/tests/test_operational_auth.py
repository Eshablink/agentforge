from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.rate_limit import RateLimitExceeded, RateLimitUnavailable
from app.db.session import SessionLocal
from app.main import app
from app.models.user import AuthSession, User
from app.services import auth_service


def test_auth_attempt_throttled_without_exposing_credentials(monkeypatch):
    calls = []
    class Limited:
        def check(self, key):
            calls.append(key)
            raise RateLimitExceeded()
    monkeypatch.setattr(auth_service, "auth_request_limiter", Limited())
    client = TestClient(app)
    response = client.post("/auth/login", json={"email": "Alice@Example.com", "password": "long-enough-password"})
    assert response.status_code == 429
    assert "Alice" not in response.text
    assert len(calls[0]) == 64


def test_auth_backend_unavailable_fails_closed(monkeypatch):
    class Down:
        def check(self, key):
            raise RateLimitUnavailable()
    monkeypatch.setattr(auth_service, "auth_request_limiter", Down())
    response = TestClient(app).post("/auth/login", json={"email": "alice@example.com", "password": "long-enough-password"})
    assert response.status_code == 503
    assert response.json() == {"detail": "Authentication temporarily unavailable"}


def test_session_cleanup_keeps_active_and_limits_batch():
    db = SessionLocal()
    try:
        user = User(email=f"cleanup-{uuid4().hex}@example.com", password_hash="fake-hash")
        db.add(user); db.flush()
        now = datetime.now(timezone.utc)
        expired = [AuthSession(user_id=user.id, token_hash=uuid4().hex + uuid4().hex,
                               expires_at=now - timedelta(days=1)) for _ in range(2)]
        active = AuthSession(user_id=user.id, token_hash=uuid4().hex + uuid4().hex,
                             expires_at=now + timedelta(days=1))
        db.add_all([*expired, active]); db.commit()
        assert auth_service.cleanup_sessions(db, batch_size=1) == 1
        assert db.scalar(select(AuthSession).where(AuthSession.id == active.id)) is not None
        assert auth_service.cleanup_sessions(db, batch_size=1) == 1
        assert auth_service.cleanup_sessions(db, batch_size=1) == 0
        with pytest.raises(ValueError):
            auth_service.cleanup_sessions(db, batch_size=1001)
    finally:
        db.close()
