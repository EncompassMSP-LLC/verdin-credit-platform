"""API version metadata."""

from typing import Literal

ApiVersionStatus = Literal["current", "stable", "deprecated", "preview"]

CURRENT_API_VERSION = "v1"
API_ROOT_PREFIX = "/api"

SUPPORTED_API_VERSIONS: tuple[str, ...] = ("v1",)
