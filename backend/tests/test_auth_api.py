from __future__ import annotations

import uuid

from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.session import SessionLocal
from app.main import app
from app.models.user import User
from app.services.auth_service import _verify_password

client = TestClient(app)


def test_register_login_logout_and_revocation() -> None:
    email = f"user-{uuid.uuid4().hex}@example.com"
    registered = client.post("/auth/register", json={"email": email, "password": "a-very-long-test-password"})
    assert registered.status_code == 201
    user_id = registered.json()["id"]

    db = SessionLocal()
    try:
        user = db.get(User, uuid.UUID(user_id))
        assert user is not None
        assert user.password_hash != "a-very-long-test-password"
        assert _verify_password("a-very-long-test-password", user.password_hash)
    finally:
        db.close()

    login = client.post("/auth/login", json={"email": email, "password": "a-very-long-test-password"})
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    assert client.get("/conversations", headers=headers).status_code == 200
    assert client.post("/auth/logout", headers=headers).status_code == 204
    assert client.get("/conversations", headers=headers).status_code == 401


def test_conversation_ownership_and_memory_roundtrip() -> None:
    def login(email: str) -> dict[str, str]:
        client.post("/auth/register", json={"email": email, "password": "a-very-long-test-password"})
        token = client.post("/auth/login", json={"email": email, "password": "a-very-long-test-password"}).json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    owner_headers = login(f"owner-{uuid.uuid4().hex}@example.com")
    other_headers = login(f"other-{uuid.uuid4().hex}@example.com")
    created = client.post("/conversations", json={"title": "test"}, headers=owner_headers)
    assert created.status_code == 201
    conversation_id = created.json()["id"]
    assert client.get(f"/conversations/{conversation_id}", headers=other_headers).status_code == 404
    response = client.post(f"/conversations/{conversation_id}/messages", json={"content": "2 + 2"}, headers=owner_headers)
    assert response.status_code == 200
    assert len(response.json()["messages"]) == 2
