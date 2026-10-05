from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.settings import get_settings
from app.core.telemetry import new_request_id, reset_request_id, set_request_id

settings = get_settings()
app = FastAPI(title=settings.app_name, version=settings.app_version)
origins = settings.cors_origin_list
if settings.app_env.lower() == "production" and (not origins or "*" in origins):
    raise RuntimeError("Production CORS must use explicit allowed origins")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = new_request_id()
    token = set_request_id(request_id)
    try:
        response = await call_next(request)
    finally:
        reset_request_id(token)
    response.headers["X-Request-Id"] = request_id
    return response


app.include_router(api_router, prefix=settings.api_prefix)
