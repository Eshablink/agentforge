"""Safe HTTP smoke probes: no provider calls or credentials."""
from __future__ import annotations

import os
import urllib.error
import urllib.request


def probe(url: str, expected_status: int = 200) -> None:
    with urllib.request.urlopen(url, timeout=5) as response:
        if response.status != expected_status:
            raise SystemExit("Smoke probe failed")


def main() -> None:
    api = os.environ.get("SMOKE_API_URL", "http://127.0.0.1:8000").rstrip("/")
    frontend = os.environ.get("SMOKE_FRONTEND_URL", "").rstrip("/")
    for endpoint in ("/health", "/ready", "/openapi.json"):
        probe(api + endpoint)
    if frontend:
        probe(frontend + "/")
    print("PASS: safe API/frontend probes")


if __name__ == "__main__":
    main()
