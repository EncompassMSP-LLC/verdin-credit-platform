"""Revenue analytics helpers — billing-derived org readiness scaffold."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from api.modules.billing.models import OrganizationBillingAccount, SubscriptionStatus

_ACTIVE_SUBSCRIPTION_STATUSES = {
    SubscriptionStatus.ACTIVE,
    SubscriptionStatus.TRIALING,
}


def compute_revenue_readiness_score(
    *,
    stripe_customer_configured: bool,
    subscription_active: bool,
    active_clients: int,
    portal_users: int,
) -> int:
    score = 0
    if stripe_customer_configured:
        score += 35
    if subscription_active:
        score += 35
    if active_clients > 0:
        score += 15
    if portal_users > 0:
        score += 15
    return min(score, 100)


def build_revenue_analytics(
    *,
    billing_enabled: bool,
    billing_ready: bool,
    account: OrganizationBillingAccount | None,
    active_clients: int,
    portal_enabled_clients: int,
    portal_users: int,
) -> dict[str, Any]:
    stripe_customer_configured = account is not None
    subscription_status = account.subscription_status if account else SubscriptionStatus.NONE
    subscription_active = subscription_status in _ACTIVE_SUBSCRIPTION_STATUSES
    current_period_end = account.current_period_end if account else None

    renewal_within_30_days: bool | None = None
    if current_period_end is not None:
        delta = current_period_end - datetime.now(UTC)
        renewal_within_30_days = 0 <= delta.days <= 30

    return {
        "billing_enabled": billing_enabled,
        "billing_ready": billing_ready,
        "stripe_customer_configured": stripe_customer_configured,
        "stripe_subscription_configured": bool(
            account is not None and account.stripe_subscription_id is not None
        ),
        "subscription_active": subscription_active,
        "subscription_status": subscription_status.value,
        "price_id": account.price_id if account else None,
        "current_period_end": current_period_end,
        "renewal_within_30_days": renewal_within_30_days,
        "active_clients": active_clients,
        "portal_enabled_clients": portal_enabled_clients,
        "portal_users": portal_users,
        "readiness_score": compute_revenue_readiness_score(
            stripe_customer_configured=stripe_customer_configured,
            subscription_active=subscription_active,
            active_clients=active_clients,
            portal_users=portal_users,
        ),
    }
