"""Account payloads used to exercise the dispute letter lifecycle."""

from __future__ import annotations

from tests.e2e.fixtures.documents import EXPECTED_CREDITOR

DISPUTE_CASE_PAYLOAD = {
    "title": "E2E Dispute Letter - Jordan Sample",
    "client_name": "Jordan A. Sample",
    "client_email": "jordan.dispute@verdin-e2e.com",
    "priority": "high",
}

DISPUTE_ACCOUNT_PAYLOAD = {
    "bureau": "equifax",
    "creditor_name": EXPECTED_CREDITOR,
    "original_creditor": EXPECTED_CREDITOR,
    "account_number_masked": "****4521",
    "account_type": "credit_card",
    "account_status": "open",
    "payment_status": "late_60",
    "balance": 2450.00,
    "past_due_amount": 420.00,
    "date_opened": "2019-03-15",
    "date_reported": "2026-05-01",
}
