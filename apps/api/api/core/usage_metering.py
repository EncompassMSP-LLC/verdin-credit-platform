"""Billing usage metering helpers — org-scoped event aggregation scaffold."""

from __future__ import annotations

from datetime import datetime
from typing import Any


def build_usage_summary(
    *,
    organization_id: str,
    metering_enabled: bool,
    stripe_customer_configured: bool,
    total_events: int,
    metrics: list[dict[str, Any]],
    first_recorded_at: datetime | None,
    last_recorded_at: datetime | None,
) -> dict[str, Any]:
    return {
        "organization_id": organization_id,
        "metering_enabled": metering_enabled,
        "stripe_customer_configured": stripe_customer_configured,
        "total_events": total_events,
        "metrics": metrics,
        "first_recorded_at": first_recorded_at,
        "last_recorded_at": last_recorded_at,
    }
