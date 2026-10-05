from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.main import app
from app.api.routes import health


def test_liveness_does_not_touch_database(monkeypatch):
    monkeypatch.setattr(health, "get_settings", lambda: (_ for _ in ()).throw(AssertionError("health touched settings")))
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_checks_database_and_is_safe_on_failure(monkeypatch):
    client = TestClient(app)
    assert client.get("/ready").json() == {"status": "ready"}
    original = health.ready_check
    class BrokenDB:
        def execute(self, *_):
            raise RuntimeError("database password secret")
        def rollback(self):
            pass
    app.dependency_overrides[health.get_db] = lambda: BrokenDB()
    try:
        failed = client.get("/ready")
        assert failed.status_code == 503
        assert failed.json() == {"status": "unavailable"}
        assert "secret" not in failed.text
    finally:
        app.dependency_overrides.clear()
