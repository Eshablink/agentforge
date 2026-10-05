from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.settings import get_settings

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
app.include_router(api_router, prefix=settings.api_prefix)
