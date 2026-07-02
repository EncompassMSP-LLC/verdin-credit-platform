"""Enterprise reporting status helpers."""

from api.modules.reporting.schemas import EnterpriseReportingStatusResponse

_ENTERPRISE_CAPABILITIES = [
    "bureau_performance_by_tradeline",
    "team_productivity_by_staff",
    "org_scoped_aggregates",
]

_DEFERRED_CAPABILITIES = [
    "materialized_views",
    "revenue_metrics",
    "score_improvement_trends",
    "cross_org_benchmarks",
]


def get_enterprise_reporting_status() -> EnterpriseReportingStatusResponse:
    return EnterpriseReportingStatusResponse(
        enterprise_reporting_enabled=True,
        capabilities=list(_ENTERPRISE_CAPABILITIES),
        deferred_capabilities=list(_DEFERRED_CAPABILITIES),
    )
