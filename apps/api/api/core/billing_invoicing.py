"""Billing invoicing and dunning scaffold helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.core.stripe_billing import get_billing_status
from api.modules.billing.models import SubscriptionStatus


@dataclass(frozen=True)
class BillingInvoicingStatus:
    enabled: bool
    ready: bool
    billing_ready: bool
    blockers: tuple[str, ...]


def get_billing_invoicing_status() -> BillingInvoicingStatus:
    enabled = is_feature_enabled(FeatureFlag.ENABLE_BILLING_INVOICING)
    billing_status = get_billing_status()
    blockers: list[str] = []
    if not enabled:
        blockers.append("ENABLE_BILLING_INVOICING is false")
    if not billing_status.enabled:
        blockers.append("ENABLE_BILLING is false")
    if enabled and billing_status.enabled and not billing_status.ready:
        blockers.append("Stripe billing is not ready")
    return BillingInvoicingStatus(
        enabled=enabled,
        ready=enabled and billing_status.enabled and billing_status.ready,
        billing_ready=billing_status.ready,
        blockers=tuple(blockers),
    )


def compute_invoicing_run_counts(
    *,
    run_kind: str,
    subscription_status: SubscriptionStatus,
    stripe_customer_configured: bool,
) -> tuple[int, int]:
    if not stripe_customer_configured:
        return 0, 0

    invoices_prepared = 0
    dunning_reminders_queued = 0
    if run_kind == "invoice_cycle" and subscription_status in {
        SubscriptionStatus.ACTIVE,
        SubscriptionStatus.TRIALING,
    }:
        invoices_prepared = 1
    if run_kind == "dunning_reminder" and subscription_status in {
        SubscriptionStatus.PAST_DUE,
        SubscriptionStatus.UNPAID,
    }:
        dunning_reminders_queued = 1
    return invoices_prepared, dunning_reminders_queued
