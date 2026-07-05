"""Admin-gated Stripe tax calculation readiness helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.core.stripe_invoice_pdf import get_stripe_invoice_pdf_status


@dataclass(frozen=True)
class StripeTaxCalculationStatus:
    enabled: bool
    ready: bool
    invoice_pdf_ready: bool
    blockers: tuple[str, ...]


def get_stripe_tax_calculation_status() -> StripeTaxCalculationStatus:
    tax_enabled = is_feature_enabled(FeatureFlag.ENABLE_STRIPE_TAX_CALCULATION)
    pdf_status = get_stripe_invoice_pdf_status()

    blockers: list[str] = []
    if not tax_enabled:
        blockers.append("ENABLE_STRIPE_TAX_CALCULATION is false")
    if tax_enabled and not pdf_status.ready:
        blockers.extend(pdf_status.blockers)

    enabled = tax_enabled and pdf_status.enabled
    return StripeTaxCalculationStatus(
        enabled=enabled,
        ready=enabled and not blockers,
        invoice_pdf_ready=pdf_status.ready,
        blockers=tuple(blockers),
    )
