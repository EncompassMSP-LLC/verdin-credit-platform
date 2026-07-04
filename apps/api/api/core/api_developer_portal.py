"""API developer portal helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.feature_flags import FeatureFlag, is_feature_enabled


@dataclass(frozen=True)
class ApiDeveloperPortalStatus:
    enabled: bool
    ready: bool
    rotation_enabled: bool
    blockers: tuple[str, ...]


def get_api_developer_portal_status() -> ApiDeveloperPortalStatus:
    enterprise_enabled = is_feature_enabled(FeatureFlag.ENABLE_ENTERPRISE)
    portal_enabled = is_feature_enabled(FeatureFlag.ENABLE_API_DEVELOPER_PORTAL)

    blockers: list[str] = []
    if not enterprise_enabled:
        blockers.append("ENABLE_ENTERPRISE is false")
    if not portal_enabled:
        blockers.append("ENABLE_API_DEVELOPER_PORTAL is false")

    enabled = enterprise_enabled and portal_enabled
    return ApiDeveloperPortalStatus(
        enabled=enabled,
        ready=enabled and not blockers,
        rotation_enabled=enabled,
        blockers=tuple(blockers),
    )
