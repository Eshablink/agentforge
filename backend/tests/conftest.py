from __future__ import annotations

import os
import shutil
import subprocess
import time
import uuid
from pathlib import Path

import psycopg
import pytest
from sqlalchemy.engine import make_url

from app.core.settings import get_settings


@pytest.fixture(scope="session", autouse=True)
def prepare_postgres_and_schema() -> None:
    settings = get_settings()
    backend_dir = Path(__file__).resolve().parents[1]

    container_name = f"agentforge-test-pg-{uuid.uuid4().hex[:8]}"
    started_container = False

    if not can_connect(settings.database_url):
        if not shutil.which("docker"):
            pytest.fail("Docker is required to run PostgreSQL integration tests")

        subprocess.run(
            [
                "docker",
                "run",
                "-d",
                "--rm",
                "--name",
                container_name,
                "-e",
                "POSTGRES_DB=agentforge",
                "-e",
                "POSTGRES_USER=agentforge",
                "-e",
                "POSTGRES_PASSWORD=agentforge",
                "-p",
                "5432:5432",
                "pgvector/pgvector:pg16",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        started_container = True
        wait_for_database(settings.database_url)

    env = os.environ.copy()
    env["DATABASE_URL"] = settings.database_url
    subprocess.run(
        ["alembic", "-c", "alembic.ini", "upgrade", "head"],
        cwd=backend_dir,
        env=env,
        check=True,
    )

    yield

    if started_container:
        subprocess.run(["docker", "rm", "-f", container_name], check=False)


def wait_for_database(database_url: str, timeout_seconds: int = 90) -> None:
    end_time = time.time() + timeout_seconds
    while time.time() < end_time:
        if can_connect(database_url):
            return
        time.sleep(2)
    pytest.fail("PostgreSQL did not become available in time")


def can_connect(database_url: str) -> bool:
    # psycopg accepts PostgreSQL DSNs, while SQLAlchemy URLs may include the
    # driver qualifier (+psycopg); normalize that URL before probing readiness.
    psycopg_dsn = make_url(database_url).set(drivername="postgresql").render_as_string(
        hide_password=False
    )
    try:
        with psycopg.connect(psycopg_dsn, connect_timeout=1) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        return True
    except psycopg.Error:
        return False
