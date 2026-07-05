"""Admin-gated Stripe invoice PDF generation readiness helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.billing_invoice_collection import get_billing_invoice_collection_status
from api.core.feature_flags import FeatureFlag, is_feature_enabled


@dataclass(frozen=True)
class StripeInvoicePdfStatus:
    enabled: bool
    ready: bool
    collection_ready: bool
    blockers: tuple[str, ...]


def get_stripe_invoice_pdf_status() -> StripeInvoicePdfStatus:
    pdf_enabled = is_feature_enabled(FeatureFlag.ENABLE_STRIPE_INVOICE_PDF)
    collection_status = get_billing_invoice_collection_status()

    blockers: list[str] = []
    if not pdf_enabled:
        blockers.append("ENABLE_STRIPE_INVOICE_PDF is false")
    if pdf_enabled and not collection_status.ready:
        blockers.extend(collection_status.blockers)

    enabled = pdf_enabled and collection_status.enabled
    return StripeInvoicePdfStatus(
        enabled=enabled,
        ready=enabled and not blockers,
        collection_ready=collection_status.ready,
        blockers=tuple(blockers),
    )
