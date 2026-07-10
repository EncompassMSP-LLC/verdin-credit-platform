"""Validate Stripe env configuration for the local pilot."""

from __future__ import annotations

import asyncio
import os

import httpx

from api.core.feature_flags import FeatureFlag, get_feature_flags, is_feature_enabled
from api.core.stripe_billing import STRIPE_API_BASE, get_stripe_billing_settings


async def verify_stripe_config() -> int:
    get_feature_flags.cache_clear()
    settings = get_stripe_billing_settings()

    print("Stripe configuration check")
    print("-" * 40)
    print(f"ENABLE_BILLING: {is_feature_enabled(FeatureFlag.ENABLE_BILLING)}")

    if not settings.stripe_secret_key:
        print("FAIL: STRIPE_SECRET_KEY is missing")
        return 1

    if not settings.stripe_webhook_secret:
        print("WARN: STRIPE_WEBHOOK_SECRET is missing (webhooks will fail until set)")

    if not settings.stripe_default_price_id:
        print("WARN: STRIPE_DEFAULT_PRICE_ID is missing (subscribe requires price_id in request)")

    secret = settings.stripe_secret_key
    mode = "test" if secret.startswith("sk_test_") else "live"
    print(f"Secret key mode: {mode}")

    if secret.endswith("_local_only"):
        print("WARN: Pilot placeholder secret detected — replace with a real Stripe test key")

    async with httpx.AsyncClient(timeout=30) as client:
        account_response = await client.get(
            f"{STRIPE_API_BASE}/account",
            auth=(secret, ""),
        )
        if account_response.status_code >= 400:
            print(f"FAIL: Stripe rejected the secret key ({account_response.status_code})")
            print(account_response.text)
            return 1

        account = account_response.json()
        print(f"OK: Connected to Stripe account {account.get('id', 'unknown')}")

        price_id = settings.stripe_default_price_id
        if price_id:
            price_response = await client.get(
                f"{STRIPE_API_BASE}/prices/{price_id}",
                auth=(secret, ""),
            )
            if price_response.status_code >= 400:
                print(f"FAIL: Price {price_id} not found or inaccessible")
                print(price_response.text)
                return 1
            price = price_response.json()
            product_id = price.get("product")
            print(f"OK: Price {price_id} is valid (product {product_id})")

    print("-" * 40)
    print("Stripe configuration looks good.")
    if mode == "live":
        print("NOTE: You are using a live secret key. Prefer sk_test_* for local development.")
    return 0


if __name__ == "__main__":
    if os.getenv("DATABASE_URL") is None:
        print("Tip: run inside the api container or with DATABASE_URL set.")
    raise SystemExit(asyncio.run(verify_stripe_config()))
