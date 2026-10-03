import os

from fastapi.testclient import TestClient

os.environ.setdefault(
    "DATABASE_URL", "postgresql+psycopg://agentforge:agentforge@localhost:5432/agentforge"
)
os.environ.setdefault("EMBEDDING_PROVIDER", "fake")
os.environ.setdefault("LLM_PROVIDER", "fake")

from app.main import app  # noqa: E402

client = TestClient(app)


def test_application_starts() -> None:
    assert app.title == "AgentForge API"


def test_health_endpoint_returns_200() -> None:
    response = client.get("/health")
    assert response.status_code == 200


def test_health_endpoint_response_schema() -> None:
    response = client.get("/health")
    assert response.json() == {"status": "ok"}
