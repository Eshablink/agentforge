from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_legacy_document_list_requires_authentication():
    response = client.get("/documents")
    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"


def test_legacy_document_upload_requires_authentication():
    response = client.post(
        "/documents",
        files={"file": ("notes.txt", b"private notes", "text/plain")},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"


def test_legacy_chat_requires_authentication():
    response = client.post(
        "/chat",
        json={"question": "What is in my document?", "top_k": 5},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"


def test_owned_routes_require_authentication():
    assert client.get("/documents/me").status_code == 401
    assert client.post("/me/chat", json={"question": "hello"}).status_code == 401
