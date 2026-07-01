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
from tests.e2e.helpers.dispute_lifecycle import run_dispute_letter_lifecycle
from tests.e2e.helpers.readiness import wait_for_case_visible


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
    wait_for_case_visible(http, headers, case_id, artifacts=artifacts, label="dispute_case_ready")

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

    run_dispute_letter_lifecycle(
        http,
        headers,
        account_id,
        expected_creditor=dispute_fixtures.DISPUTE_ACCOUNT_PAYLOAD["creditor_name"],
        artifacts=artifacts,
    )
