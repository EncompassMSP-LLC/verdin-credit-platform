"""Enterprise reporting status helpers."""

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.modules.reporting.schemas import EnterpriseReportingStatusResponse

_ENTERPRISE_CAPABILITIES = [
    "bureau_performance_by_tradeline",
    "team_productivity_by_staff",
    "org_scoped_aggregates",
]

_DEFERRED_CAPABILITIES = [
    "revenue_metrics",
    "score_improvement_trends",
    "cross_org_benchmarks",
]


def get_enterprise_reporting_status() -> EnterpriseReportingStatusResponse:
    capabilities = list(_ENTERPRISE_CAPABILITIES)
    deferred = list(_DEFERRED_CAPABILITIES)
    if is_feature_enabled(FeatureFlag.ENABLE_MATERIALIZED_REPORTING):
        capabilities.append("materialized_views")
    else:
        deferred.insert(0, "materialized_views")

    return EnterpriseReportingStatusResponse(
        enterprise_reporting_enabled=True,
        capabilities=capabilities,
        deferred_capabilities=deferred,
    )
