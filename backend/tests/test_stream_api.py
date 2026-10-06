from __future__ import annotations

import json
import logging
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


def _events(body: str) -> list[tuple[str, dict]]:
    parsed = []
    for frame in body.strip().split("\n\n"):
        name = "message"
        data = {}
        for line in frame.splitlines():
            if line.startswith("event:"):
                name = line.split(":", 1)[1].strip()
            elif line.startswith("data:"):
                data = json.loads(line.split(":", 1)[1].strip())
        if data:
            parsed.append((name, data))
    return parsed


def test_stream_requires_auth() -> None:
    assert client.post("/agent/chat/stream", json={"question": "7 * 8"}).status_code == 401


def test_stream_returns_typed_events_one_start_and_correlated_request_id(caplog) -> None:
    caplog.set_level(logging.INFO, logger="agentforge.observability")
    headers = _register_login(f"stream-{uuid.uuid4().hex}@example.com")
    resp = client.post("/agent/chat/stream", json={"question": "7 * 8"}, headers=headers)
    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers.get("content-type", "")
    assert resp.headers["Cache-Control"] == "no-store"
    assert resp.headers["X-Accel-Buffering"] == "no"
    events = _events(resp.text)
    names = [name for name, _ in events]
    assert names.count("message_start") == 1
    assert names[0] == "message_start"
    assert "tool_start" in names and "token" in names and "message_end" in names
    request_id = resp.headers["X-Request-Id"]
    assert events[0][1]["request_id"] == request_id
    correlated = [
        rec.agentforge_event
        for rec in caplog.records
        if hasattr(rec, "agentforge_event")
        and rec.agentforge_event.get("event") in {"agent_request", "agent_stream_complete"}
    ]
    assert correlated
    assert all(item.get("request_id") == request_id for item in correlated)


def test_stream_does_not_leak_secrets_in_body() -> None:
    headers = _register_login(f"stream-secret-{uuid.uuid4().hex}@example.com")
    body = client.post("/agent/chat/stream", json={"question": "7 * 8"}, headers=headers).text.lower()
    assert "sk-" not in body and "bearer" not in body


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
    assert response.status_code in (413, 422)


def test_stream_owns_preflight_session_before_provider_iteration(monkeypatch) -> None:
    headers = _register_login(f"stream-session-{uuid.uuid4().hex}@example.com")
    created = client.post("/conversations", json={"title": "session"}, headers=headers)
    assert created.status_code == 201
    conversation_id = created.json()["id"]

    from app.api.routes import stream as stream_route

    original_session_local = stream_route.SessionLocal
    sessions = []

    class TrackingSession:
        def __init__(self):
            self.inner = original_session_local()
            self.closed = False

        def __enter__(self):
            self.inner.__enter__()
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            self.closed = True
            return self.inner.__exit__(exc_type, exc_value, traceback)

        def close(self):
            self.closed = True
            return self.inner.close()

        def __getattr__(self, name):
            return getattr(self.inner, name)

    def tracking_factory():
        session = TrackingSession()
        sessions.append(session)
        return session

    class FakeStreamService:
        def stream(self, question: str, *, context: str = "", user_id=None):
            assert sessions and sessions[0].closed
            yield "token", {"text": "safe response"}
            yield "message_end", {
                "answer_kind": "DIRECT",
                "tools_used": [],
                "sources": [],
                "stream_mode": "simulated",
            }

    monkeypatch.setattr(stream_route, "SessionLocal", tracking_factory)
    monkeypatch.setattr(stream_route, "_stream_service", lambda: FakeStreamService())

    response = client.post(
        "/agent/chat/stream",
        json={"question": "hello", "conversation_id": conversation_id},
        headers=headers,
    )

    assert response.status_code == 200
    assert len(sessions) >= 2
    assert sessions[0].closed
    assert sessions[1].closed
