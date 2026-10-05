from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
PASSWORD = "a-very-long-test-password"


def _register_login(email: str) -> dict[str, str]:
    assert client.post("/auth/register", json={"email": email, "password": PASSWORD}).status_code == 201
    resp = client.post("/auth/login", json={"email": email, "password": PASSWORD})
    assert resp.status_code == 200
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def test_stream_requires_auth() -> None:
    resp = client.post("/agent/chat/stream", json={"question": "7 * 8"})
    assert resp.status_code == 401


def test_stream_returns_sse_events_for_calculator() -> None:
    headers = _register_login(f"stream-{uuid.uuid4().hex}@example.com")
    resp = client.post("/agent/chat/stream", json={"question": "7 * 8"}, headers=headers)
    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers.get("content-type", "")
    assert "X-Request-Id" in resp.headers
    body = resp.text
    assert "event: message_start" in body
    assert "event: tool_start" in body
    assert "event: token" in body
    assert "event: message_end" in body


def test_stream_does_not_leak_secrets_in_body() -> None:
    headers = _register_login(f"stream-secret-{uuid.uuid4().hex}@example.com")
    resp = client.post("/agent/chat/stream", json={"question": "7 * 8"}, headers=headers)
    body = resp.text.lower()
    assert "sk-" not in body
    assert "bearer" not in body


def test_stream_enforces_conversation_ownership() -> None:
    owner = _register_login(f"stream-owner-{uuid.uuid4().hex}@example.com")
    other = _register_login(f"stream-other-{uuid.uuid4().hex}@example.com")
    created = client.post("/conversations", json={"title": "private"}, headers=owner)
    assert created.status_code == 201
    response = client.post(
        "/agent/chat/stream",
        json={"question": "7 * 8", "conversation_id": created.json()["id"]},
        headers=other,
    )
    assert response.status_code == 404


def test_stream_rejects_oversized_prompt() -> None:
    headers = _register_login(f"stream-limit-{uuid.uuid4().hex}@example.com")
    response = client.post("/agent/chat/stream", json={"question": "x" * 5001}, headers=headers)
    assert response.status_code == 422 or response.status_code == 413
