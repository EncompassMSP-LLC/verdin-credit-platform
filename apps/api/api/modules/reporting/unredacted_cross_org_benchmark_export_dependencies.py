"""Unredacted cross-org benchmark export feature flag dependency."""

from fastapi import HTTPException, status

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.modules.reporting.dependencies import require_cross_org_benchmark_analytics_enabled


def require_unredacted_cross_org_benchmark_export_enabled() -> None:
    require_cross_org_benchmark_analytics_enabled()
    if not is_feature_enabled(FeatureFlag.ENABLE_UNREDACTED_CROSS_ORG_BENCHMARK_EXPORT):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unredacted cross-org benchmark export is not enabled",
        )
