"""Offline deployment artifact checks wired into pytest, no external accounts."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_backend_migration_runs_outside_app_replica():
    image = (ROOT / "backend" / "Dockerfile").read_text()
    assert "USER agentforge" in image
    assert 'python", "serve.py"' in image
    assert "alembic upgrade head &&" not in image
    compose = (ROOT / "docker-compose.yml").read_text()
    assert "service_completed_successfully" in compose


def test_frontend_artifact_and_edge_limits_are_defined():
    image = (ROOT / "frontend" / "Dockerfile.production").read_text()
    assert "nginx-unprivileged" in image
    assert "npm ci" in image
    assert "frontend/package-lock.json" in image
    edge = (ROOT / "deploy" / "nginx.edge.example.conf").read_text()
    for directive in (
        "limit_req_zone",
        "limit_conn streams",
        "proxy_buffering off",
        "proxy_cache off",
        "client_max_body_size",
        "proxy_read_timeout",
    ):
        assert directive in edge
    assert "location = /health" in edge
    assert "location = /ready" in edge
    assert "location ~ ^/(agent|me|chat|conversations)" in edge


def test_health_and_readiness_are_not_inside_ai_rate_limited_location():
    edge = (ROOT / "deploy" / "nginx.edge.example.conf").read_text()
    generic = edge.split("location ~ ^/(agent|me|chat|conversations)", 1)[1]
    assert "/health" not in generic
    assert "/ready" not in generic


def test_stream_proxy_timeout_exceeds_application_stream_limit():
    edge = (ROOT / "deploy" / "nginx.edge.example.conf").read_text()
    assert "proxy_read_timeout 120s" in edge
    assert "MAX_STREAM_DURATION_SECONDS=60" in (ROOT / ".env.example").read_text()
