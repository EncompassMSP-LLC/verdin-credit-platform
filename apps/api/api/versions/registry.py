"""API version registry for mounting coexistence-friendly version routers."""

from dataclasses import dataclass

from fastapi import APIRouter, FastAPI

from api.versions.constants import SUPPORTED_API_VERSIONS, ApiVersionStatus
from api.versions.v1 import router as v1_router

# Import v2 when implemented; router remains empty until routes are added.
# from api.versions.v2 import router as v2_router


@dataclass(frozen=True, slots=True)
class ApiVersion:
    version: str
    prefix: str
    router: APIRouter
    status: ApiVersionStatus
    description: str
    deprecated: bool = False
    sunset: str | None = None


def get_registered_versions() -> list[ApiVersion]:
    return [
        ApiVersion(
            version="v1",
            prefix="/api/v1",
            router=v1_router,
            status="current",
            description="Stable API — initial platform release.",
        ),
        # Example for future coexistence:
        # ApiVersion(
        #     version="v2",
        #     prefix="/api/v2",
        #     router=v2_router,
        #     status="preview",
        #     description="Next-generation API (preview).",
        # ),
    ]


def mount_api_versions(app: FastAPI) -> None:
    for api_version in get_registered_versions():
        app.include_router(
            api_version.router,
            prefix=api_version.prefix,
            tags=[f"API {api_version.version}"],
        )


def get_version_by_name(version: str) -> ApiVersion | None:
    return next((v for v in get_registered_versions() if v.version == version), None)


def is_supported_version(version: str) -> bool:
    return version in SUPPORTED_API_VERSIONS
