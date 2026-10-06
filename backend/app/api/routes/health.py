from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.rate_limit import RateLimitUnavailable, ai_request_limiter
from app.core.settings import get_settings
from app.core.telemetry import record
from app.db.dependencies import get_db
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Cheap liveness: no network access or provider calls."""
    return HealthResponse(status="ok")


@router.get("/ready")
def ready_check(db: Session = Depends(get_db)):
    """Check mandatory serving dependencies; do not expose underlying errors."""
    try:
        db.execute(text("SELECT 1"))
        if get_settings().rate_limit_backend == "redis":
            # The shared limiter is mandatory in production; failure is not ignored.
            ai_request_limiter.client.ping()
    except Exception:
        db.rollback()
        record("readiness", outcome="unavailable")
        return JSONResponse(status_code=503, content={"status": "unavailable"})
    record("readiness", outcome="ready")
    return {"status": "ready"}
