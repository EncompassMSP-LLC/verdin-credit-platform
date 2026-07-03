"""Materialized reporting view names and status helpers."""

from datetime import datetime

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.modules.reporting.schemas import MaterializedReportingStatusResponse

BUREAU_ACCOUNT_MV = "mv_bureau_account_counts"
BUREAU_SENT_LETTERS_MV = "mv_bureau_sent_letter_counts"
TEAM_PRODUCTIVITY_MV = "mv_team_member_productivity"

REPORTING_MATERIALIZED_VIEWS: tuple[str, ...] = (
    BUREAU_ACCOUNT_MV,
    BUREAU_SENT_LETTERS_MV,
    TEAM_PRODUCTIVITY_MV,
)


def get_materialized_reporting_status(
    *,
    last_refreshed_at: datetime | None,
) -> MaterializedReportingStatusResponse:
    return MaterializedReportingStatusResponse(
        enabled=is_feature_enabled(FeatureFlag.ENABLE_MATERIALIZED_REPORTING),
        views=list(REPORTING_MATERIALIZED_VIEWS),
        last_refreshed_at=last_refreshed_at,
    )
