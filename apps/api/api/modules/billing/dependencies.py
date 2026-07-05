"""Billing feature gate dependencies."""

from fastapi import HTTPException, status

from api.core.feature_flags import FeatureFlag, is_feature_enabled


def require_billing_enabled() -> None:
    if not is_feature_enabled(FeatureFlag.ENABLE_BILLING):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Billing is not enabled",
        )


def require_usage_metering_enabled() -> None:
    require_billing_enabled()
    if not is_feature_enabled(FeatureFlag.ENABLE_BILLING_USAGE_METERING):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Billing usage metering is not enabled",
        )


def require_billing_invoicing_enabled() -> None:
    require_billing_enabled()
    if not is_feature_enabled(FeatureFlag.ENABLE_BILLING_INVOICING):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Billing invoicing is not enabled",
        )


def require_billing_invoice_collection_enabled() -> None:
    require_billing_invoicing_enabled()
    if not is_feature_enabled(FeatureFlag.ENABLE_BILLING_INVOICE_COLLECTION):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Billing invoice collection is not enabled",
        )


def require_stripe_invoice_pdf_enabled() -> None:
    require_billing_invoice_collection_enabled()
    if not is_feature_enabled(FeatureFlag.ENABLE_STRIPE_INVOICE_PDF):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stripe invoice PDF generation is not enabled",
        )


def require_stripe_tax_calculation_enabled() -> None:
    require_stripe_invoice_pdf_enabled()
    if not is_feature_enabled(FeatureFlag.ENABLE_STRIPE_TAX_CALCULATION):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stripe tax calculation is not enabled",
        )
