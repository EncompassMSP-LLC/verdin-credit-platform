"""System health and version endpoints."""

from fastapi import APIRouter

from api.core.config import get_settings
from api.core.responses import HealthResponse, VersionResponse

router = APIRouter(tags=["System"])
settings = get_settings()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        environment=settings.app_env,
    )


@router.get("/version", response_model=VersionResponse)
async def version() -> VersionResponse:
    return VersionResponse(
        version=settings.app_version,
        name=settings.app_name,
    )
