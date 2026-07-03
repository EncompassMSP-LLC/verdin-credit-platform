"""Stripe billing configuration, client helpers, and readiness gates."""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

import httpx
from pydantic_settings import BaseSettings, SettingsConfigDict

from api.core.feature_flags import FeatureFlag, is_feature_enabled

STRIPE_API_BASE = "https://api.stripe.com/v1"


class BillingNotReadyError(Exception):
    def __init__(self, blockers: list[str]) -> None:
        self.blockers = blockers
        super().__init__("Stripe billing is not ready")


class StripeBillingSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    stripe_secret_key: str | None = None
    stripe_webhook_secret: str | None = None
    stripe_default_price_id: str | None = None


@dataclass(frozen=True, slots=True)
class BillingStatus:
    enabled: bool
    ready: bool
    provider: str
    default_price_id: str | None
    blockers: list[str]


@dataclass(frozen=True, slots=True)
class StripeCustomerResult:
    customer_id: str


@dataclass(frozen=True, slots=True)
class StripeSubscriptionResult:
    subscription_id: str
    status: str
    price_id: str | None
    current_period_end: int | None


@lru_cache
def get_stripe_billing_settings() -> StripeBillingSettings:
    return StripeBillingSettings()


def get_billing_status(settings: StripeBillingSettings | None = None) -> BillingStatus:
    feature_enabled = is_feature_enabled(FeatureFlag.ENABLE_BILLING)
    current = settings or get_stripe_billing_settings()
    blockers: list[str] = []

    if not feature_enabled:
        blockers.append("ENABLE_BILLING is false")
    if not current.stripe_secret_key:
        blockers.append("STRIPE_SECRET_KEY is not configured")
    if not current.stripe_webhook_secret:
        blockers.append("STRIPE_WEBHOOK_SECRET is not configured")

    return BillingStatus(
        enabled=feature_enabled,
        ready=len(blockers) == 0,
        provider="stripe",
        default_price_id=current.stripe_default_price_id,
        blockers=blockers,
    )


def require_billing_ready(settings: StripeBillingSettings | None = None) -> BillingStatus:
    status = get_billing_status(settings)
    if not status.ready:
        raise BillingNotReadyError(status.blockers)
    return status


def verify_stripe_webhook_signature(
    payload: bytes,
    signature_header: str,
    *,
    secret: str,
    tolerance_seconds: int = 300,
) -> bool:
    parts: dict[str, list[str]] = {}
    for item in signature_header.split(","):
        key, _, value = item.partition("=")
        parts.setdefault(key, []).append(value)

    timestamp_values = parts.get("t")
    signature_values = parts.get("v1")
    if not timestamp_values or not signature_values:
        return False

    try:
        timestamp = int(timestamp_values[0])
    except ValueError:
        return False

    if abs(int(time.time()) - timestamp) > tolerance_seconds:
        return False

    signed_payload = f"{timestamp}.{payload.decode()}".encode()
    expected = hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()
    return any(hmac.compare_digest(expected, value) for value in signature_values)


async def create_stripe_customer(
    *,
    email: str,
    name: str,
    organization_id: str,
    settings: StripeBillingSettings | None = None,
) -> StripeCustomerResult:
    current = settings or get_stripe_billing_settings()
    status = require_billing_ready(current)
    if status.blockers:
        raise BillingNotReadyError(status.blockers)
    secret_key = current.stripe_secret_key
    if secret_key is None:
        raise BillingNotReadyError(["STRIPE_SECRET_KEY is not configured"])

    data = {
        "email": email,
        "name": name,
        "metadata[organization_id]": organization_id,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{STRIPE_API_BASE}/customers",
            auth=(secret_key, ""),
            data=data,
        )
    if response.status_code >= 400:
        raise ValueError(response.text)
    body = response.json()
    return StripeCustomerResult(customer_id=str(body["id"]))


async def create_stripe_subscription(
    *,
    customer_id: str,
    price_id: str,
    settings: StripeBillingSettings | None = None,
) -> StripeSubscriptionResult:
    current = settings or get_stripe_billing_settings()
    require_billing_ready(current)
    secret_key = current.stripe_secret_key
    if secret_key is None:
        raise BillingNotReadyError(["STRIPE_SECRET_KEY is not configured"])

    data = {
        "customer": customer_id,
        "items[0][price]": price_id,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{STRIPE_API_BASE}/subscriptions",
            auth=(secret_key, ""),
            data=data,
        )
    if response.status_code >= 400:
        raise ValueError(response.text)
    body = response.json()
    items = body.get("items", {}).get("data", [])
    item_price = items[0]["price"]["id"] if items else None
    return StripeSubscriptionResult(
        subscription_id=str(body["id"]),
        status=str(body.get("status", "unknown")),
        price_id=str(item_price) if item_price else None,
        current_period_end=body.get("current_period_end"),
    )


def parse_stripe_event(payload: bytes) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(payload.decode())
    return data
