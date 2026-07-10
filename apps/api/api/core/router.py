"""System health and version endpoints."""

import redis
from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse
from sqlalchemy import text

from api.core.config import get_settings
from api.core.responses import HealthResponse, ReadinessResponse, VersionResponse
from api.database.session import AsyncSessionLocal

router = APIRouter(tags=["System"])
settings = get_settings()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        environment=settings.app_env,
    )


@router.get("/health/ready", response_model=ReadinessResponse)
async def readiness_check(response: Response) -> ReadinessResponse | JSONResponse:
    checks: dict[str, str] = {}

    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:  # noqa: BLE001 — surface dependency status to operators
        checks["database"] = str(exc)

    try:
        redis_client = redis.Redis.from_url(settings.redis_url)
        redis_client.ping()
        checks["redis"] = "ok"
    except Exception as exc:  # noqa: BLE001
        checks["redis"] = str(exc)

    ready = all(value == "ok" for value in checks.values())
    payload = ReadinessResponse(
        status="ready" if ready else "not_ready",
        checks=checks,
    )
    if ready:
        return payload

    return JSONResponse(status_code=503, content=payload.model_dump())


@router.get("/version", response_model=VersionResponse)
async def version() -> VersionResponse:
    return VersionResponse(
        version=settings.app_version,
        name=settings.app_name,
    )
