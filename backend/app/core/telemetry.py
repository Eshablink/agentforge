"""Request-scoped safe operational telemetry."""

import contextvars
import logging
import time
import uuid

logger = logging.getLogger("agentforge.observability")
request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("request_id", default=None)


def new_request_id() -> str:
    return uuid.uuid4().hex


def get_request_id() -> str | None:
    return request_id_var.get()


def set_request_id(request_id: str):
    return request_id_var.set(request_id)


def reset_request_id(token) -> None:
    request_id_var.reset(token)


def record(event_name: str, **metadata) -> dict:
    """Log only bounded operational metadata; never pass user or provider text."""
    payload = {"event": event_name[:64], "request_id": get_request_id(), "ts_ms": round(time.time() * 1000)}
    for key, value in metadata.items():
        payload[key[:64]] = value if isinstance(value, (int, float, bool)) or value is None else str(value)[:256]
    logger.info("observability", extra={"agentforge_event": payload})
    return payload
