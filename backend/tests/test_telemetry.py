from __future__ import annotations

import logging

from app.core.telemetry import get_request_id, new_request_id, record, reset_request_id, set_request_id


def test_request_id_context_and_safe_telemetry(caplog) -> None:
    request_id = new_request_id()
    token = set_request_id(request_id)
    try:
        assert get_request_id() == request_id
        with caplog.at_level(logging.INFO, logger="agentforge.observability"):
            event = record("agent_test", endpoint="/agent/chat", latency_ms=1.25, error_category="none")
        assert event["request_id"] == request_id
        assert event["endpoint"] == "/agent/chat"
        assert "agent_test" in caplog.text
        assert request_id in caplog.text
    finally:
        reset_request_id(token)
    assert get_request_id() is None


def test_telemetry_bounds_string_values() -> None:
    value = "x" * 1000
    result = record("bounded", detail=value)
    assert len(result["detail"]) <= 256
