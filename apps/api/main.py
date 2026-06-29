"""Verdin Credit Platform API."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.core.config import get_settings
from api.core.events import configure_event_bus
from api.core.exceptions import register_exception_handlers
from api.core.logging import setup_logging
from api.middleware.logging import RequestLoggingMiddleware
from api.versions import configure_openapi, discovery_router, mount_api_versions
from api.versions.constants import CURRENT_API_VERSION
from api.versions.docs import register_version_docs

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    setup_logging(debug=settings.debug)
    configure_event_bus()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Production-grade credit operations platform API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)
register_exception_handlers(app)

mount_api_versions(app)
app.include_router(discovery_router)
register_version_docs(app, settings)
configure_openapi(app, settings)


@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "api_version": CURRENT_API_VERSION,
        "api_base": "/api/v1",
        "api_versions": "/api/versions",
        "docs": "/docs",
        "docs_v1": "/api/v1/docs",
    }
