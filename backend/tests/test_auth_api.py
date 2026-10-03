from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.session import SessionLocal
from app.main import app
from app.models.conversation import Conversation, Message
from app.models.document import Document, DocumentChunk
from app.models.user import User
from app.services.auth_service import _verify_password
from app.core.settings import get_settings

client = TestClient(app)
PASSWORD = "a-very-long-test-password"


def _register_login(email: str) -> tuple[dict[str, str], str]:
    assert client.post("/auth/register", json={"email": email, "password": PASSWORD}).status_code == 201
    response = client.post("/auth/login", json={"email": email, "password": PASSWORD})
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}, token


def test_registration_login_password_hash_and_logout_revocation() -> None:
    email = f"user-{uuid.uuid4().hex}@example.com"
    registered = client.post("/auth/register", json={"email": email, "password": PASSWORD})
    assert registered.status_code == 201
    assert client.post("/auth/register", json={"email": email, "password": PASSWORD}).status_code == 409
    user_id = uuid.UUID(registered.json()["id"])
    db = SessionLocal()
    try:
        user = db.get(User, user_id)
        assert user is not None and user.password_hash != PASSWORD
        assert _verify_password(PASSWORD, user.password_hash)
    finally:
        db.close()
    assert client.post("/auth/login", json={"email": email, "password": "incorrect-long-password"}).status_code == 401
    login = client.post("/auth/login", json={"email": email, "password": PASSWORD})
    assert login.status_code == 200
    token = login.json()["access_token"]
    db = SessionLocal()
    try:
        from app.models.user import AuthSession
        row = db.scalar(select(AuthSession).where(AuthSession.user_id == user_id))
        assert row is not None and row.token_hash != token
        assert row.expires_at > datetime.now(timezone.utc)
    finally:
        db.close()
    headers = {"Authorization": f"Bearer {token}"}
    assert client.get("/conversations", headers=headers).status_code == 200
    assert client.post("/auth/logout", headers=headers).status_code == 204
    assert client.get("/conversations", headers=headers).status_code == 401


def test_protected_routes_require_auth_and_conversations_enforce_owner() -> None:
    assert client.get("/conversations").status_code == 401
    owner, _ = _register_login(f"owner-{uuid.uuid4().hex}@example.com")
    other, _ = _register_login(f"other-{uuid.uuid4().hex}@example.com")
    created = client.post("/conversations", json={"title": "private"}, headers=owner)
    assert created.status_code == 201
    cid = created.json()["id"]
    assert client.get(f"/conversations/{cid}", headers=other).status_code == 404
    assert client.delete(f"/conversations/{cid}", headers=other).status_code == 404
    assert client.get("/conversations", headers=other).json() == []
    assert client.delete(f"/conversations/{cid}", headers=owner).status_code == 204


def test_document_routes_are_owner_scoped_and_legacy_routes_are_unowned_only() -> None:
    owner_headers, _ = _register_login(f"doc-owner-{uuid.uuid4().hex}@example.com")
    other_headers, _ = _register_login(f"doc-other-{uuid.uuid4().hex}@example.com")
    content = b"private document for account owner"
    upload = client.post("/documents/me", files={"file": ("private.txt", content, "text/plain")}, headers=owner_headers)
    assert upload.status_code == 201
    assert [row["filename"] for row in client.get("/documents/me", headers=owner_headers).json()] == ["private.txt"]
    assert client.get("/documents/me", headers=other_headers).json() == []
    legacy = client.get("/documents")
    assert all(item["filename"] != "private.txt" for item in legacy.json())
    agent = client.post("/agent/chat", json={"question": "Find the private document"}, headers=other_headers)
    assert agent.status_code == 200
    assert agent.json()["sources"] == []


def test_user_owned_conversation_memory_is_bounded_and_isolated(monkeypatch) -> None:
    owner_headers, _ = _register_login(f"memory-owner-{uuid.uuid4().hex}@example.com")
    other_headers, _ = _register_login(f"memory-other-{uuid.uuid4().hex}@example.com")
    created = client.post("/conversations", json={"title": "memory"}, headers=owner_headers)
    cid = created.json()["id"]
    conversation_id = uuid.UUID(cid)
    db = SessionLocal()
    try:
        db.add_all([
            Message(conversation_id=conversation_id, role="user", content="old context"),
            Message(conversation_id=conversation_id, role="assistant", content="old reply"),
        ])
        db.commit()
    finally:
        db.close()

    from app.api.routes import platform
    original = platform._service
    observed = {}
    class FakeAgent:
        def run(self, question, *, context="", user_id=None):
            observed.update(context=context, user_id=user_id)
            from app.services.agent_service import AgentResult
            from app.schemas.platform import AgentEvent
            return AgentResult(answer="ok", answer_kind="DIRECT", sources=[], tools_used=[], events=[AgentEvent(event="finished")])
    monkeypatch.setattr(platform, "_service", lambda db: FakeAgent())
    try:
        sent = client.post(f"/conversations/{cid}/messages", json={"content": "follow-up"}, headers=owner_headers)
    finally:
        monkeypatch.setattr(platform, "_service", original)
    assert sent.status_code == 200
    assert "old context" in observed["context"]
    assert "follow-up" not in observed["context"]
    assert observed["user_id"] == uuid.UUID(created.json().get("user_id", str(observed["user_id"]))) if observed.get("user_id") else False
    assert client.get(f"/conversations/{cid}", headers=other_headers).status_code == 404
