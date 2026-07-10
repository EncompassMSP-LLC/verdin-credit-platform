"""Client self-enrollment configuration and Stripe Checkout helpers."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any
from urllib.parse import urlencode

import httpx
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from api.core.config import get_settings
from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.core.stripe_billing import STRIPE_API_BASE, get_stripe_billing_settings

ANNUAL_CREDIT_REPORT_URL = "https://www.annualcreditreport.com/index.action"


class ClientEnrollmentSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    enrollment_organization_slug: str = Field(default="verdin-demo")
    stripe_enrollment_price_id: str | None = None
    enrollment_skip_payment: bool = Field(default=False)
    enrollment_checkout_mode: str = Field(default="payment")


@dataclass(frozen=True, slots=True)
class ClientEnrollmentStatus:
    enabled: bool
    ready: bool
    payment_required: bool
    checkout_available: bool
    organization_slug: str
    price_id: str | None
    annual_credit_report_url: str
    blockers: list[str]


@dataclass(frozen=True, slots=True)
class StripeCheckoutSessionResult:
    session_id: str
    checkout_url: str


@lru_cache
def get_client_enrollment_settings() -> ClientEnrollmentSettings:
    return ClientEnrollmentSettings()


def _resolve_enrollment_price_id(settings: ClientEnrollmentSettings | None = None) -> str | None:
    current = settings or get_client_enrollment_settings()
    if current.stripe_enrollment_price_id:
        return current.stripe_enrollment_price_id
    return get_stripe_billing_settings().stripe_default_price_id


def get_client_enrollment_status(
    settings: ClientEnrollmentSettings | None = None,
) -> ClientEnrollmentStatus:
    current = settings or get_client_enrollment_settings()
    billing = get_stripe_billing_settings()
    blockers: list[str] = []
    feature_enabled = is_feature_enabled(FeatureFlag.ENABLE_CLIENT_ENROLLMENT)
    portal_enabled = is_feature_enabled(FeatureFlag.ENABLE_CLIENT_PORTAL)

    if not feature_enabled:
        blockers.append("ENABLE_CLIENT_ENROLLMENT is false")
    if not portal_enabled:
        blockers.append("ENABLE_CLIENT_PORTAL is false")
    if not current.enrollment_organization_slug.strip():
        blockers.append("ENROLLMENT_ORGANIZATION_SLUG is not configured")

    price_id = _resolve_enrollment_price_id(current)
    payment_required = not current.enrollment_skip_payment
    checkout_available = payment_required and bool(billing.stripe_secret_key and price_id)

    if payment_required and not current.enrollment_skip_payment:
        if not billing.stripe_secret_key:
            blockers.append("STRIPE_SECRET_KEY is not configured for enrollment checkout")
        if not price_id:
            blockers.append(
                "STRIPE_ENROLLMENT_PRICE_ID or STRIPE_DEFAULT_PRICE_ID is not configured"
            )
        if price_id and not price_id.startswith("price_"):
            blockers.append("Enrollment price id must be a Stripe Price id (price_...)")

    ready = (
        feature_enabled
        and portal_enabled
        and bool(current.enrollment_organization_slug.strip())
        and (
            current.enrollment_skip_payment
            or (
                payment_required
                and bool(billing.stripe_secret_key)
                and price_id is not None
                and price_id.startswith("price_")
            )
        )
    )

    return ClientEnrollmentStatus(
        enabled=feature_enabled,
        ready=ready,
        payment_required=payment_required and not current.enrollment_skip_payment,
        checkout_available=checkout_available,
        organization_slug=current.enrollment_organization_slug,
        price_id=price_id,
        annual_credit_report_url=ANNUAL_CREDIT_REPORT_URL,
        blockers=blockers,
    )


def build_enrollment_success_url(session_id: str) -> str:
    app_settings = get_settings()
    base = app_settings.public_app_url.rstrip("/")
    query = urlencode({"session_id": session_id})
    return f"{base}/enroll/success?{query}"


def build_enrollment_cancel_url() -> str:
    app_settings = get_settings()
    base = app_settings.public_app_url.rstrip("/")
    return f"{base}/enroll?cancelled=1"


async def create_stripe_checkout_session(
    *,
    enrollment_id: str,
    customer_email: str,
    customer_name: str,
    price_id: str,
    enrollment_settings: ClientEnrollmentSettings | None = None,
) -> StripeCheckoutSessionResult:
    billing = get_stripe_billing_settings()
    secret_key = billing.stripe_secret_key
    if secret_key is None:
        raise ValueError("STRIPE_SECRET_KEY is not configured")

    current = enrollment_settings or get_client_enrollment_settings()
    mode = current.enrollment_checkout_mode
    if mode not in {"payment", "subscription"}:
        mode = "payment"

    data: dict[str, str] = {
        "mode": mode,
        "customer_email": customer_email,
        "client_reference_id": enrollment_id,
        "success_url": build_enrollment_success_url("{CHECKOUT_SESSION_ID}"),
        "cancel_url": build_enrollment_cancel_url(),
        "line_items[0][price]": price_id,
        "line_items[0][quantity]": "1",
        "metadata[enrollment_id]": enrollment_id,
        "metadata[customer_name]": customer_name[:500],
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{STRIPE_API_BASE}/checkout/sessions",
            auth=(secret_key, ""),
            data=data,
        )
    if response.status_code >= 400:
        raise ValueError(response.text)

    body = response.json()
    session_id = str(body["id"])
    checkout_url = str(body["url"])
    return StripeCheckoutSessionResult(session_id=session_id, checkout_url=checkout_url)


async def retrieve_stripe_checkout_session(session_id: str) -> dict[str, Any]:
    billing = get_stripe_billing_settings()
    secret_key = billing.stripe_secret_key
    if secret_key is None:
        raise ValueError("STRIPE_SECRET_KEY is not configured")

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(
            f"{STRIPE_API_BASE}/checkout/sessions/{session_id}",
            auth=(secret_key, ""),
        )
    if response.status_code >= 400:
        raise ValueError(response.text)
    body: dict[str, Any] = response.json()
    return body
