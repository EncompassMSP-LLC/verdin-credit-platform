"""Shared dispute letter lifecycle steps for E2E tests."""

from __future__ import annotations

import httpx

from tests.e2e.helpers.artifacts import ArtifactCollector
from tests.e2e.helpers.assertions import expect_ok
from tests.e2e.helpers.wait_for_worker import poll_until


def run_dispute_letter_lifecycle(
    http: httpx.Client,
    headers: dict[str, str],
    account_id: str,
    *,
    expected_creditor: str,
    artifacts: ArtifactCollector,
    label_prefix: str = "",
) -> None:
    """Exercise dispute draft through CRA outcome for an existing account."""
    label = f"{label_prefix}dispute"

    draft = expect_ok(
        http.get(
            f"/api/v1/accounts/{account_id}/dispute-draft",
            headers=headers,
        ),
        label=f"{label}_draft_preview",
        artifacts=artifacts,
    )
    assert draft["account_id"] == account_id
    assert draft["template_id"]
    assert expected_creditor in draft["body"]
    assert draft["disputed_items"]

    letter = expect_ok(
        http.post(
            f"/api/v1/accounts/{account_id}/dispute-draft/letters",
            headers=headers,
        ),
        label=f"{label}_save_letter",
        artifacts=artifacts,
    )
    letter_id = letter["id"]
    assert letter["status"] == "draft"
    assert letter["account_id"] == account_id

    letters = expect_ok(
        http.get(
            f"/api/v1/accounts/{account_id}/dispute-letters",
            headers=headers,
        ),
        label=f"{label}_list_letters",
        artifacts=artifacts,
    )
    assert isinstance(letters, list)
    assert any(item["id"] == letter_id for item in letters)

    review_task = expect_ok(
        http.post(
            f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/review-task",
            headers=headers,
        ),
        label=f"{label}_review_task",
        artifacts=artifacts,
        expected_status=200,
    )
    assert review_task["account_id"] == account_id
    assert review_task["source_module"] == "accounts.dispute_letter"

    review_response = poll_until(
        lambda: http.get(
            f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}",
            headers=headers,
        ),
        lambda response: (
            response.status_code == 200 and response.json().get("status") == "review"
        ),
        description="dispute letter status == review",
        timeout=15.0,
        interval=0.25,
    )
    in_review = review_response.json()
    artifacts.record(f"{label}_letter_in_review", in_review)

    approved = expect_ok(
        http.post(
            f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/approve",
            headers=headers,
        ),
        label=f"{label}_approve_letter",
        artifacts=artifacts,
    )
    assert approved["status"] == "approved"

    sent = expect_ok(
        http.post(
            f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/send",
            headers=headers,
        ),
        label=f"{label}_send_letter",
        artifacts=artifacts,
    )
    assert sent["status"] == "sent"
    assert sent["sent_at"] is not None

    account_sent = expect_ok(
        http.get(f"/api/v1/accounts/{account_id}", headers=headers),
        label=f"{label}_account_after_send",
        artifacts=artifacts,
    )
    assert account_sent["dispute_status"] == "dispute_sent"
    assert account_sent["cra_dispute"] is True

    followup_tasks = expect_ok(
        http.get(
            "/api/v1/tasks",
            headers=headers,
            params={
                "account_id": account_id,
                "source_module": "accounts.dispute_letter_followup",
            },
        ),
        label=f"{label}_followup_tasks",
        artifacts=artifacts,
    )
    assert len(followup_tasks["items"]) >= 1
    assert followup_tasks["items"][0]["source_event_id"] == letter_id

    export_text = http.get(
        f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/export",
        headers=headers,
        params={"format": "text"},
    )
    artifacts.record(
        f"{label}_export_text",
        {
            "method": export_text.request.method,
            "url": str(export_text.request.url),
            "status_code": export_text.status_code,
            "body": export_text.text[:500],
        },
    )
    assert export_text.status_code == 200
    assert "DISPUTED ITEMS" in export_text.text

    awaiting = expect_ok(
        http.post(
            f"/api/v1/accounts/{account_id}/dispute-awaiting-response",
            headers=headers,
        ),
        label=f"{label}_awaiting_response",
        artifacts=artifacts,
    )
    assert awaiting["dispute_status"] == "awaiting_response"
    assert awaiting["investigation_status"] == "pending"

    outcome = expect_ok(
        http.post(
            f"/api/v1/accounts/{account_id}/dispute-response-received",
            headers=headers,
            json={"outcome": "corrected"},
        ),
        label=f"{label}_response_received",
        artifacts=artifacts,
    )
    assert outcome["dispute_status"] == "corrected"
    assert outcome["response_received"] is True
    assert outcome["investigation_status"] == "completed"
