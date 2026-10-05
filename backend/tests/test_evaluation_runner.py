from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def test_deterministic_evaluation_runner_passes() -> None:
    backend_dir = Path(__file__).resolve().parents[1]
    runner = backend_dir.parent / "evaluation" / "runner" / "run_evals.py"
    env = os.environ.copy()
    env.setdefault("LLM_PROVIDER", "fake")
    env.setdefault("EMBEDDING_PROVIDER", "fake")
    result = subprocess.run(
        [sys.executable, str(runner)],
        cwd=backend_dir,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "passed, 0 failed" in result.stdout
