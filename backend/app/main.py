import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.rate_limit import RateLimitUnavailable
from app.core.settings import get_settings
from app.core.telemetry import new_request_id, record, reset_request_id, set_request_id

settings = get_settings()
app = FastAPI(title=settings.app_name, version=settings.app_version)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.exception_handler(RateLimitUnavailable)
async def limiter_unavailable(request: Request, exc: RateLimitUnavailable):
    record("rate_limit", category="backend_unavailable")
    return JSONResponse(status_code=503, content={"detail": "Request protection unavailable"})


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = new_request_id()
    request.state.request_id = request_id
    token = set_request_id(request_id)
    started = time.perf_counter()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        response.headers["X-Request-Id"] = request_id
        return response
    finally:
        record("http_request", request_id=request_id, endpoint=request.url.path[:128],
               method=request.method[:8], latency_ms=round((time.perf_counter() - started) * 1000, 3),
               status_code=status_code)
        reset_request_id(token)


app.include_router(api_router, prefix=settings.api_prefix)
