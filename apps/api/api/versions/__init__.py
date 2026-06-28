"""API versioning — mount versioned routers and configure OpenAPI."""

from api.versions.constants import (
    API_ROOT_PREFIX,
    CURRENT_API_VERSION,
    SUPPORTED_API_VERSIONS,
)
from api.versions.discovery import router as discovery_router
from api.versions.docs import register_version_docs
from api.versions.openapi import configure_openapi
from api.versions.registry import (
    ApiVersion,
    get_registered_versions,
    get_version_by_name,
    is_supported_version,
    mount_api_versions,
)

__all__ = [
    "API_ROOT_PREFIX",
    "CURRENT_API_VERSION",
    "SUPPORTED_API_VERSIONS",
    "ApiVersion",
    "configure_openapi",
    "discovery_router",
    "get_registered_versions",
    "get_version_by_name",
    "is_supported_version",
    "mount_api_versions",
    "register_version_docs",
]
