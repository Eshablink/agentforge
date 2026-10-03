from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_application_starts() -> None:
    assert app.title == "AgentForge API"


def test_health_endpoint_returns_200() -> None:
    response = client.get("/health")
    assert response.status_code == 200


def test_health_endpoint_response_schema() -> None:
    response = client.get("/health")
    assert response.json() == {"status": "ok"}
