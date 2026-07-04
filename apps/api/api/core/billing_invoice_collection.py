"""Billing invoice collection scaffold helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.billing_invoicing import get_billing_invoicing_status
from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.modules.billing.models import SubscriptionStatus


@dataclass(frozen=True)
class BillingInvoiceCollectionStatus:
    enabled: bool
    ready: bool
    invoicing_ready: bool
    blockers: tuple[str, ...]


def get_billing_invoice_collection_status() -> BillingInvoiceCollectionStatus:
    enabled = is_feature_enabled(FeatureFlag.ENABLE_BILLING_INVOICE_COLLECTION)
    invoicing_status = get_billing_invoicing_status()
    blockers: list[str] = []
    if not enabled:
        blockers.append("ENABLE_BILLING_INVOICE_COLLECTION is false")
    if not invoicing_status.enabled:
        blockers.append("ENABLE_BILLING_INVOICING is false")
    if not invoicing_status.billing_ready and invoicing_status.enabled:
        blockers.append("Stripe billing is not ready")
    if enabled and invoicing_status.enabled and not invoicing_status.ready:
        blockers.extend(invoicing_status.blockers)
    return BillingInvoiceCollectionStatus(
        enabled=enabled and invoicing_status.enabled,
        ready=enabled and invoicing_status.ready,
        invoicing_ready=invoicing_status.ready,
        blockers=tuple(blockers),
    )


def compute_collection_run_counts(
    *,
    run_kind: str,
    subscription_status: SubscriptionStatus,
    stripe_customer_configured: bool,
) -> tuple[int, int]:
    if not stripe_customer_configured:
        return 0, 0

    invoices_pdf_generated = 0
    payment_reminders_queued = 0
    if run_kind == "invoice_pdf" and subscription_status in {
        SubscriptionStatus.ACTIVE,
        SubscriptionStatus.TRIALING,
    }:
        invoices_pdf_generated = 1
    if run_kind == "payment_reminder" and subscription_status in {
        SubscriptionStatus.PAST_DUE,
        SubscriptionStatus.UNPAID,
    }:
        payment_reminders_queued = 1
    return invoices_pdf_generated, payment_reminders_queued
