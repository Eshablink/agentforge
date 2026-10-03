from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_auth_requires_identity_and_rejects_invalid_login() -> None:
    response = client.get("/conversations")
    assert response.status_code == 401
    login = client.post("/auth/login", json={"email": "missing@example.com", "password": "not-the-password"})
    assert login.status_code == 401


def test_registration_validates_password_policy() -> None:
    response = client.post("/auth/register", json={"email": "short@example.com", "password": "short"})
    assert response.status_code == 422
