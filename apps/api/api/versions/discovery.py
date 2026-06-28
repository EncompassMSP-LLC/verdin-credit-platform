"""API version discovery and documentation routes."""

from fastapi import APIRouter

from api.core.config import get_settings
from api.core.constants import APP_VERSION
from api.core.responses import BaseSchema
from api.versions.constants import CURRENT_API_VERSION
from api.versions.registry import get_registered_versions

router = APIRouter(prefix="/api", tags=["API Discovery"])
settings = get_settings()


class ApiVersionInfo(BaseSchema):
    version: str
    prefix: str
    status: str
    description: str
    deprecated: bool
    sunset: str | None
    docs: str
    openapi: str
    redoc: str


class ApiVersionsResponse(BaseSchema):
    current: str
    application_version: str
    versions: list[ApiVersionInfo]


@router.get("/versions", response_model=ApiVersionsResponse)
async def list_api_versions() -> ApiVersionsResponse:
    return ApiVersionsResponse(
        current=CURRENT_API_VERSION,
        application_version=APP_VERSION,
        versions=[
            ApiVersionInfo(
                version=v.version,
                prefix=v.prefix,
                status=v.status,
                description=v.description,
                deprecated=v.deprecated,
                sunset=v.sunset,
                docs=f"{v.prefix}/docs",
                openapi=f"{v.prefix}/openapi.json",
                redoc=f"{v.prefix}/redoc",
            )
            for v in get_registered_versions()
        ],
    )
