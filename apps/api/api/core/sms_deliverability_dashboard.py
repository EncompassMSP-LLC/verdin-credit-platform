"""SMS deliverability dashboard readiness helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.core.sms_marketing_delivery import get_sms_marketing_delivery_status


@dataclass(frozen=True)
class SmsDeliverabilityDashboardStatus:
    enabled: bool
    ready: bool
    delivery_ready: bool
    blockers: tuple[str, ...]


def get_sms_deliverability_dashboard_status() -> SmsDeliverabilityDashboardStatus:
    dashboard_enabled = is_feature_enabled(FeatureFlag.ENABLE_SMS_DELIVERABILITY_DASHBOARD)
    delivery_status = get_sms_marketing_delivery_status()

    blockers: list[str] = []
    if not dashboard_enabled:
        blockers.append("ENABLE_SMS_DELIVERABILITY_DASHBOARD is false")
    if not delivery_status.enabled:
        blockers.append("ENABLE_SMS_MARKETING_DELIVERY is false")
    if dashboard_enabled and delivery_status.enabled and not delivery_status.ready:
        blockers.extend(delivery_status.blockers)

    enabled = dashboard_enabled and delivery_status.enabled
    return SmsDeliverabilityDashboardStatus(
        enabled=enabled,
        ready=enabled and delivery_status.ready,
        delivery_ready=delivery_status.ready,
        blockers=tuple(blockers),
    )


def compute_delivery_success_rate(*, messages_sent: int, messages_failed: int) -> float | None:
    total = messages_sent + messages_failed
    if total <= 0:
        return None
    return round((messages_sent / total) * 100, 2)


def build_sms_deliverability_metrics(
    *,
    total_campaign_runs: int,
    completed_campaign_runs: int,
    failed_campaign_runs: int,
    pending_campaign_runs: int,
    delivery_logs_sent: int,
    delivery_logs_failed: int,
    recent_campaign_outcomes: list[dict[str, Any]],
) -> dict[str, Any]:
    aggregate_sent = delivery_logs_sent
    aggregate_failed = delivery_logs_failed
    return {
        "total_campaign_runs": total_campaign_runs,
        "completed_campaign_runs": completed_campaign_runs,
        "failed_campaign_runs": failed_campaign_runs,
        "pending_campaign_runs": pending_campaign_runs,
        "delivery_logs_sent": delivery_logs_sent,
        "delivery_logs_failed": delivery_logs_failed,
        "delivery_success_rate": compute_delivery_success_rate(
            messages_sent=aggregate_sent,
            messages_failed=aggregate_failed,
        ),
        "recent_campaign_outcomes": recent_campaign_outcomes,
    }
