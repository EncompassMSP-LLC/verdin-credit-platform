"""Live unredacted benchmark blob export feature flag dependency."""

from fastapi import HTTPException, status

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.modules.reporting.unredacted_cross_org_benchmark_export_dependencies import (
    require_unredacted_cross_org_benchmark_export_enabled,
)


def require_live_unredacted_benchmark_blob_export_enabled() -> None:
    require_unredacted_cross_org_benchmark_export_enabled()
    if not is_feature_enabled(FeatureFlag.ENABLE_LIVE_UNREDACTED_BENCHMARK_BLOB_EXPORT):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Live unredacted benchmark blob export is not enabled",
        )
