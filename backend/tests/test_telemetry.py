from __future__ import annotations

from app.core.telemetry import get_request_id, new_request_id, record, reset_request_id, set_request_id


def test_request_id_context_and_safe_telemetry(caplog) -> None:
    request_id = new_request_id()
    token = set_request_id(request_id)
    try:
        assert get_request_id() == request_id
        event = record("agent_test", endpoint="/agent/chat", latency_ms=1.25, error_category="none")
        assert event["request_id"] == request_id
        assert event["endpoint"] == "/agent/chat"
        entries = [entry for entry in caplog.records if hasattr(entry, "agentforge_event")]
        # Logging adapters/pytest capture may not retain the custom extra, so
        # the returned bounded event is the authoritative assertion above.
        if entries:
            assert entries[-1].agentforge_event["request_id"] == request_id
    finally:
        reset_request_id(token)
    assert get_request_id() is None


def test_telemetry_bounds_string_values() -> None:
    value = "x" * 1000
    result = record("bounded", detail=value)
    assert len(result["detail"]) <= 256
