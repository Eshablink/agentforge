"""Offline deployment artifact checks wired into pytest/CI, no external accounts."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_backend_migration_runs_outside_app_replica():
    image = (ROOT / "backend" / "Dockerfile").read_text()
    assert "USER agentforge" in image
    assert 'CMD ["uvicorn"' in image
    assert "alembic upgrade head &&" not in image
    compose = (ROOT / "docker-compose.yml").read_text()
    assert "service_completed_successfully" in compose


def test_frontend_artifact_and_edge_limits_are_defined():
    image = (ROOT / "frontend" / "Dockerfile.production").read_text()
    assert "nginx-unprivileged" in image and "npm run build" in image
    edge = (ROOT / "deploy" / "nginx.edge.example.conf").read_text()
    for directive in ("limit_req_zone", "limit_conn streams", "proxy_buffering off", "proxy_cache off", "client_max_body_size", "proxy_read_timeout"):
        assert directive in edge


def test_smoke_script_uses_safe_endpoints_only():
    smoke = (ROOT / "deploy" / "smoke.py").read_text()
    assert '"/health"' in smoke and '"/ready"' in smoke
    assert "/agent/chat" not in smoke
