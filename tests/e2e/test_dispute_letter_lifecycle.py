"""End-to-end dispute letter workflow over the HTTP API.

Exercises the Version 4.5 dispute letter happy path against a running stack:

    Authenticate → Case → Account → Dispute draft preview → Save letter
    → Review task → Approve → Send → Awaiting response → Record outcome
    → Export artifact → Follow-up task
"""

from __future__ import annotations

import httpx

from tests.e2e.fixtures import dispute as dispute_fixtures
from tests.e2e.fixtures.users import UserRecord
from tests.e2e.helpers import auth
from tests.e2e.helpers.artifacts import ArtifactCollector
from tests.e2e.helpers.assertions import expect_ok


def test_dispute_letter_lifecycle(
    http: httpx.Client,
    owner: UserRecord,
    artifacts: ArtifactCollector,
) -> None:
    tokens = auth.login(http, owner.email, owner.password)
    headers = tokens.headers

    case = expect_ok(
        http.post(
            "/api/v1/cases",
            headers=headers,
            json=dispute_fixtures.DISPUTE_CASE_PAYLOAD,
        ),
        label="dispute_case",
        artifacts=artifacts,
        expected_status=201,
    )
    case_id = case["id"]

    account = expect_ok(
        http.post(
            "/api/v1/accounts",
            headers=headers,
            json={**dispute_fixtures.DISPUTE_ACCOUNT_PAYLOAD, "case_id": case_id},
        ),
        label="dispute_account",
        artifacts=artifacts,
        expected_status=201,
    )
    account_id = account["id"]
    assert account["creditor_name"] == dispute_fixtures.DISPUTE_ACCOUNT_PAYLOAD["creditor_name"]

    draft = expect_ok(
        http.get(
            f"/api/v1/accounts/{account_id}/dispute-draft",
            headers=headers,
        ),
        label="dispute_draft_preview",
        artifacts=artifacts,
    )
    assert draft["account_id"] == account_id
    assert draft["template_id"]
    assert dispute_fixtures.DISPUTE_ACCOUNT_PAYLOAD["creditor_name"] in draft["body"]
    assert draft["disputed_items"]

    letter = expect_ok(
        http.post(
            f"/api/v1/accounts/{account_id}/dispute-draft/letters",
            headers=headers,
        ),
        label="dispute_save_letter",
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
        label="dispute_list_letters",
        artifacts=artifacts,
    )
    assert isinstance(letters, list)
    assert any(item["id"] == letter_id for item in letters)

    review_task = expect_ok(
        http.post(
            f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/review-task",
            headers=headers,
        ),
        label="dispute_review_task",
        artifacts=artifacts,
        expected_status=200,
    )
    assert review_task["account_id"] == account_id
    assert review_task["source_module"] == "accounts.dispute_letter"

    in_review = expect_ok(
        http.get(
            f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}",
            headers=headers,
        ),
        label="dispute_letter_in_review",
        artifacts=artifacts,
    )
    assert in_review["status"] == "review"

    approved = expect_ok(
        http.post(
            f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/approve",
            headers=headers,
        ),
        label="dispute_approve_letter",
        artifacts=artifacts,
    )
    assert approved["status"] == "approved"

    sent = expect_ok(
        http.post(
            f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/send",
            headers=headers,
        ),
        label="dispute_send_letter",
        artifacts=artifacts,
    )
    assert sent["status"] == "sent"
    assert sent["sent_at"] is not None

    account_sent = expect_ok(
        http.get(f"/api/v1/accounts/{account_id}", headers=headers),
        label="dispute_account_after_send",
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
        label="dispute_followup_tasks",
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
        "dispute_export_text",
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
        label="dispute_awaiting_response",
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
        label="dispute_response_received",
        artifacts=artifacts,
    )
    assert outcome["dispute_status"] == "corrected"
    assert outcome["response_received"] is True
    assert outcome["investigation_status"] == "completed"
