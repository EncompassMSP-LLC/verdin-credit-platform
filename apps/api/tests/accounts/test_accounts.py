"""Account management endpoint tests."""

import uuid
from datetime import date, timedelta

from fastapi.testclient import TestClient

from tests.accounts.conftest import sample_account_payload


def test_create_account(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    response = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["creditor_name"] == "Example Bank"
    assert data["bureau"] == "equifax"
    assert data["risk_score"] is not None
    assert data["readiness_score"] is not None


def test_create_account_forbidden_for_read_only(
    api_client: TestClient,
    readonly_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    response = api_client.post(
        "/api/v1/accounts",
        headers=readonly_headers,
        json=sample_account_payload(sample_case_id),
    )
    assert response.status_code == 403


def test_list_accounts(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    response = api_client.get("/api/v1/accounts", headers=manager_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert "items" in data


def test_list_accounts_bureau_filter(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    response = api_client.get(
        "/api/v1/accounts",
        headers=manager_headers,
        params={"bureau": "equifax"},
    )
    assert response.status_code == 200
    assert response.json()["total"] >= 1


def test_list_accounts_search(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    unique = f"Creditor-{uuid.uuid4().hex[:6]}"
    payload = sample_account_payload(sample_case_id)
    payload["creditor_name"] = unique
    api_client.post("/api/v1/accounts", headers=manager_headers, json=payload)
    response = api_client.get(
        "/api/v1/accounts",
        headers=manager_headers,
        params={"search": unique},
    )
    assert response.status_code == 200
    assert any(item["creditor_name"] == unique for item in response.json()["items"])


def test_get_account(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    create = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    account_id = create.json()["id"]
    response = api_client.get(f"/api/v1/accounts/{account_id}", headers=manager_headers)
    assert response.status_code == 200
    assert response.json()["id"] == account_id


def test_get_account_dispute_draft(
    api_client: TestClient,
    manager_headers: dict[str, str],
    readonly_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    create = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    account_id = create.json()["id"]

    response = api_client.get(
        f"/api/v1/accounts/{account_id}/dispute-draft",
        headers=readonly_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["account_id"] == account_id
    assert data["case_id"] == sample_case_id
    assert data["bureau"] == "equifax"
    assert data["recipient_type"] == "credit_bureau"
    assert data["template_id"] == "cra-tradeline-investigation-v1"
    assert data["generated_by"] == "rules"
    assert "Example Bank" in data["subject"]
    assert "Example Bank" in data["body"]
    assert "Account Client" in data["body"]
    assert any("payment history" in item for item in data["disputed_items"])
    assert data["dispute_reason_suggestions"]
    assert any(item["code"] == "payment_history" for item in data["dispute_reason_suggestions"])
    assert any(item["code"] == "balance" for item in data["dispute_reason_suggestions"])
    assert all(
        item["description"] in data["disputed_items"] for item in data["dispute_reason_suggestions"]
    )
    assert data["evidence_ready"] is False
    assert any(item["code"] == "client_contact" for item in data["missing_evidence"])
    assert any(item["code"] == "reporting_dates" for item in data["missing_evidence"])
    assert any("balance" in item.lower() for item in data["evidence_checklist"])
    assert data["readiness_score"] is not None
    assert data["risk_score"] is not None


def test_get_account_furnisher_dispute_draft(
    api_client: TestClient,
    manager_headers: dict[str, str],
    readonly_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    create = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    account_id = create.json()["id"]

    response = api_client.get(
        f"/api/v1/accounts/{account_id}/dispute-draft",
        headers=readonly_headers,
        params={"recipient_type": "furnisher"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["recipient_type"] == "furnisher"
    assert data["template_id"] == "furnisher-direct-dispute-v1"
    assert "Direct furnisher dispute" in data["subject"]
    assert "Fair Credit Reporting Act" in data["body"]
    assert "furnishing to equifax" in data["body"].lower()
    assert any("furnisher-reported tradeline" in item for item in data["evidence_checklist"])


def test_create_furnisher_dispute_letter_draft(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    create = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    account_id = create.json()["id"]

    response = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-draft/letters",
        headers=manager_headers,
        params={"recipient_type": "furnisher"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["recipient_type"] == "furnisher"
    assert data["template_id"] == "furnisher-direct-dispute-v1"
    assert data["status"] == "draft"


def test_create_account_dispute_draft_review_task_is_idempotent(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    create = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    account_id = create.json()["id"]

    first = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-draft/review-task",
        headers=manager_headers,
    )
    second = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-draft/review-task",
        headers=manager_headers,
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["id"] == first.json()["id"]
    assert first.json()["account_id"] == account_id
    assert first.json()["case_id"] == sample_case_id
    assert first.json()["priority"] == "high"
    assert first.json()["source_module"] == "accounts.dispute_draft"
    assert first.json()["source_event_id"] == account_id


def test_create_and_list_account_dispute_letter_drafts(
    api_client: TestClient,
    manager_headers: dict[str, str],
    readonly_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    create = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    account_id = create.json()["id"]

    created = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-draft/letters",
        headers=manager_headers,
    )
    listed = api_client.get(
        f"/api/v1/accounts/{account_id}/dispute-letters",
        headers=readonly_headers,
    )

    assert created.status_code == 200
    created_data = created.json()
    assert created_data["account_id"] == account_id
    assert created_data["case_id"] == sample_case_id
    assert created_data["status"] == "draft"
    assert created_data["template_id"] == "cra-tradeline-investigation-v1"
    assert created_data["generated_by"] == "rules"
    assert "Example Bank" in created_data["body"]
    assert created_data["disputed_items"]
    assert created_data["evidence_checklist"]

    assert listed.status_code == 200
    listed_data = listed.json()
    assert [item["id"] for item in listed_data] == [created_data["id"]]


def test_get_account_dispute_letter(
    api_client: TestClient,
    manager_headers: dict[str, str],
    readonly_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    create = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    account_id = create.json()["id"]

    created = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-draft/letters",
        headers=manager_headers,
    )
    letter_id = created.json()["id"]

    response = api_client.get(
        f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}",
        headers=readonly_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == letter_id
    assert data["account_id"] == account_id
    assert data["status"] == "draft"
    assert "Example Bank" in data["body"]
    assert data["disputed_items"]
    assert data["evidence_checklist"]
    assert data["compliance_notes"]


def test_export_account_dispute_letter_text(
    api_client: TestClient,
    manager_headers: dict[str, str],
    readonly_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    create = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    account_id = create.json()["id"]

    created = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-draft/letters",
        headers=manager_headers,
    )
    letter_id = created.json()["id"]

    response = api_client.get(
        f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/export",
        headers=readonly_headers,
        params={"format": "text"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert "attachment" in response.headers["content-disposition"]
    assert ".txt" in response.headers["content-disposition"]
    assert "Example Bank" in response.text
    assert "DISPUTED ITEMS" in response.text


def test_export_account_dispute_letter_pdf(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    create = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    account_id = create.json()["id"]

    created = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-draft/letters",
        headers=manager_headers,
    )
    letter_id = created.json()["id"]

    response = api_client.get(
        f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/export",
        headers=manager_headers,
        params={"format": "pdf"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")


def test_export_account_dispute_letter_not_found(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    create = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    account_id = create.json()["id"]

    response = api_client.get(
        f"/api/v1/accounts/{account_id}/dispute-letters/{uuid.uuid4()}/export",
        headers=manager_headers,
        params={"format": "text"},
    )

    assert response.status_code == 404


def test_get_account_dispute_letter_not_found(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    create = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    account_id = create.json()["id"]

    response = api_client.get(
        f"/api/v1/accounts/{account_id}/dispute-letters/{uuid.uuid4()}",
        headers=manager_headers,
    )

    assert response.status_code == 404


def test_create_account_dispute_letter_review_task_is_idempotent(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    create = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    account_id = create.json()["id"]

    letter = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-draft/letters",
        headers=manager_headers,
    )
    letter_id = letter.json()["id"]

    first = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/review-task",
        headers=manager_headers,
    )
    second = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/review-task",
        headers=manager_headers,
    )
    listed = api_client.get(
        f"/api/v1/accounts/{account_id}/dispute-letters",
        headers=manager_headers,
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["id"] == first.json()["id"]
    assert first.json()["account_id"] == account_id
    assert first.json()["case_id"] == sample_case_id
    assert first.json()["priority"] == "high"
    assert first.json()["source_module"] == "accounts.dispute_letter"
    assert first.json()["source_event_id"] == letter_id
    assert listed.json()[0]["status"] == "review"


def test_create_account_dispute_letter_review_task_not_found(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    create = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    account_id = create.json()["id"]

    response = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-letters/{uuid.uuid4()}/review-task",
        headers=manager_headers,
    )

    assert response.status_code == 404


def test_approve_account_dispute_letter(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    create = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    account_id = create.json()["id"]

    letter = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-draft/letters",
        headers=manager_headers,
    )
    letter_id = letter.json()["id"]

    review_task = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/review-task",
        headers=manager_headers,
    )
    first_approve = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/approve",
        headers=manager_headers,
    )
    second_approve = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/approve",
        headers=manager_headers,
    )

    assert review_task.status_code == 200
    assert first_approve.status_code == 200
    assert second_approve.status_code == 200
    assert first_approve.json()["status"] == "approved"
    assert second_approve.json()["id"] == first_approve.json()["id"]
    assert second_approve.json()["status"] == "approved"


def test_approve_account_dispute_letter_requires_review_status(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    create = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    account_id = create.json()["id"]

    letter = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-draft/letters",
        headers=manager_headers,
    )
    letter_id = letter.json()["id"]

    response = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/approve",
        headers=manager_headers,
    )

    assert response.status_code == 422


def test_send_account_dispute_letter(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    create = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    account_id = create.json()["id"]

    letter = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-draft/letters",
        headers=manager_headers,
    )
    letter_id = letter.json()["id"]

    api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/review-task",
        headers=manager_headers,
    )
    api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/approve",
        headers=manager_headers,
    )
    first_send = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/send",
        headers=manager_headers,
    )
    second_send = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/send",
        headers=manager_headers,
    )

    assert first_send.status_code == 200
    assert second_send.status_code == 200
    assert first_send.json()["status"] == "sent"
    assert first_send.json()["sent_at"] is not None
    assert second_send.json()["id"] == first_send.json()["id"]
    assert second_send.json()["status"] == "sent"
    assert second_send.json()["sent_at"] == first_send.json()["sent_at"]

    account = api_client.get(f"/api/v1/accounts/{account_id}", headers=manager_headers)
    assert account.status_code == 200
    account_data = account.json()
    assert account_data["dispute_status"] == "dispute_sent"
    assert account_data["last_dispute_date"] is not None
    assert account_data["dispute_round"] == 1
    assert account_data["cra_dispute"] is True

    tasks = api_client.get(
        "/api/v1/tasks",
        headers=manager_headers,
        params={"account_id": account_id},
    )
    assert tasks.status_code == 200
    followup_tasks = [
        item
        for item in tasks.json()["items"]
        if item["source_module"] == "accounts.dispute_letter_followup"
    ]
    assert len(followup_tasks) == 1
    followup = followup_tasks[0]
    assert followup["source_event_id"] == letter_id
    assert followup["case_id"] == sample_case_id
    assert followup["priority"] == "medium"
    assert "Track CRA response" in followup["title"]


def test_send_account_dispute_letter_requires_approved_status(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    create = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    account_id = create.json()["id"]

    letter = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-draft/letters",
        headers=manager_headers,
    )
    letter_id = letter.json()["id"]

    response = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/send",
        headers=manager_headers,
    )

    assert response.status_code == 422


def test_send_account_dispute_letter_followup_task_is_idempotent(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    create = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    account_id = create.json()["id"]

    letter = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-draft/letters",
        headers=manager_headers,
    )
    letter_id = letter.json()["id"]

    api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/review-task",
        headers=manager_headers,
    )
    api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/approve",
        headers=manager_headers,
    )
    api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/send",
        headers=manager_headers,
    )
    api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/send",
        headers=manager_headers,
    )

    tasks = api_client.get(
        "/api/v1/tasks",
        headers=manager_headers,
        params={"account_id": account_id},
    )
    assert tasks.status_code == 200
    followup_tasks = [
        item
        for item in tasks.json()["items"]
        if item["source_module"] == "accounts.dispute_letter_followup"
    ]
    assert len(followup_tasks) == 1
    assert followup_tasks[0]["source_event_id"] == letter_id


def test_void_account_dispute_letter(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    create = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    account_id = create.json()["id"]

    letter = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-draft/letters",
        headers=manager_headers,
    )
    letter_id = letter.json()["id"]

    first_void = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/void",
        headers=manager_headers,
    )
    second_void = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/void",
        headers=manager_headers,
    )

    assert first_void.status_code == 200
    assert second_void.status_code == 200
    assert first_void.json()["status"] == "void"
    assert second_void.json()["id"] == first_void.json()["id"]
    assert second_void.json()["status"] == "void"


def test_void_account_dispute_letter_from_approved(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    create = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    account_id = create.json()["id"]

    letter = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-draft/letters",
        headers=manager_headers,
    )
    letter_id = letter.json()["id"]

    api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/review-task",
        headers=manager_headers,
    )
    api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/approve",
        headers=manager_headers,
    )
    response = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/void",
        headers=manager_headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "void"


def test_void_account_dispute_letter_rejects_sent(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    create = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    account_id = create.json()["id"]

    letter = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-draft/letters",
        headers=manager_headers,
    )
    letter_id = letter.json()["id"]

    api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/review-task",
        headers=manager_headers,
    )
    api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/approve",
        headers=manager_headers,
    )
    api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/send",
        headers=manager_headers,
    )
    response = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/void",
        headers=manager_headers,
    )

    assert response.status_code == 422


def test_mark_account_awaiting_dispute_response(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    create = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    account_id = create.json()["id"]

    letter = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-draft/letters",
        headers=manager_headers,
    )
    letter_id = letter.json()["id"]

    api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/review-task",
        headers=manager_headers,
    )
    api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/approve",
        headers=manager_headers,
    )
    api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/send",
        headers=manager_headers,
    )
    first = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-awaiting-response",
        headers=manager_headers,
    )
    second = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-awaiting-response",
        headers=manager_headers,
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["dispute_status"] == "awaiting_response"
    assert second.json()["id"] == first.json()["id"]
    assert second.json()["dispute_status"] == "awaiting_response"
    assert first.json()["investigation_status"] == "pending"


def test_mark_account_awaiting_dispute_response_requires_dispute_sent(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    create = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    account_id = create.json()["id"]

    response = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-awaiting-response",
        headers=manager_headers,
    )

    assert response.status_code == 422


def _mark_account_awaiting_response(
    api_client: TestClient,
    manager_headers: dict[str, str],
    account_id: str,
) -> None:
    letter = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-draft/letters",
        headers=manager_headers,
    )
    letter_id = letter.json()["id"]
    api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/review-task",
        headers=manager_headers,
    )
    api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/approve",
        headers=manager_headers,
    )
    api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/send",
        headers=manager_headers,
    )
    api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-awaiting-response",
        headers=manager_headers,
    )


def test_record_account_dispute_response_received(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    create = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    account_id = create.json()["id"]
    _mark_account_awaiting_response(api_client, manager_headers, account_id)

    first = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-response-received",
        headers=manager_headers,
        json={"outcome": "corrected"},
    )
    second = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-response-received",
        headers=manager_headers,
        json={"outcome": "corrected"},
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["dispute_status"] == "corrected"
    assert first.json()["response_received"] is True
    assert first.json()["investigation_status"] == "completed"
    assert second.json()["id"] == first.json()["id"]


def test_record_account_dispute_response_received_supports_deleted(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    create = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    account_id = create.json()["id"]
    _mark_account_awaiting_response(api_client, manager_headers, account_id)

    response = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-response-received",
        headers=manager_headers,
        json={"outcome": "deleted"},
    )

    assert response.status_code == 200
    assert response.json()["dispute_status"] == "deleted"
    assert response.json()["response_received"] is True


def test_record_account_dispute_response_received_requires_awaiting_response(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    create = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    account_id = create.json()["id"]

    response = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-response-received",
        headers=manager_headers,
        json={"outcome": "verified"},
    )

    assert response.status_code == 422


def _backdate_last_dispute_date(
    api_client: TestClient,
    manager_headers: dict[str, str],
    account_id: str,
    *,
    days_ago: int,
) -> None:
    past_date = (date.today() - timedelta(days=days_ago)).isoformat()
    response = api_client.patch(
        f"/api/v1/accounts/{account_id}",
        headers=manager_headers,
        json={"last_dispute_date": past_date},
    )
    assert response.status_code == 200


def test_escalate_overdue_investigation_creates_task(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    create = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    account_id = create.json()["id"]
    _mark_account_awaiting_response(api_client, manager_headers, account_id)
    _backdate_last_dispute_date(api_client, manager_headers, account_id, days_ago=31)

    first = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-investigation-overdue",
        headers=manager_headers,
    )
    second = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-investigation-overdue",
        headers=manager_headers,
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["investigation_status"] == "overdue"
    assert second.json()["id"] == first.json()["id"]
    assert second.json()["investigation_status"] == "overdue"
    assert "Escalate overdue" in first.json()["ai_recommended_next_action"]

    tasks = api_client.get(
        "/api/v1/tasks",
        headers=manager_headers,
        params={"account_id": account_id},
    )
    assert tasks.status_code == 200
    overdue_tasks = [
        item
        for item in tasks.json()["items"]
        if item["source_module"] == "accounts.dispute_investigation_overdue"
    ]
    assert len(overdue_tasks) == 1
    assert overdue_tasks[0]["source_event_id"] == account_id
    assert overdue_tasks[0]["priority"] == "high"
    assert "Escalate overdue CRA investigation" in overdue_tasks[0]["title"]


def test_escalate_overdue_investigation_requires_deadline_passed(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    create = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    account_id = create.json()["id"]
    _mark_account_awaiting_response(api_client, manager_headers, account_id)

    response = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-investigation-overdue",
        headers=manager_headers,
    )

    assert response.status_code == 422


def test_get_account_does_not_auto_escalate_overdue_investigation(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    create = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    account_id = create.json()["id"]
    _mark_account_awaiting_response(api_client, manager_headers, account_id)
    _backdate_last_dispute_date(api_client, manager_headers, account_id, days_ago=31)

    response = api_client.get(f"/api/v1/accounts/{account_id}", headers=manager_headers)

    assert response.status_code == 200
    assert response.json()["investigation_status"] == "pending"

    escalated = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-investigation-overdue",
        headers=manager_headers,
    )
    assert escalated.status_code == 200
    assert escalated.json()["investigation_status"] == "overdue"


def test_get_account_not_found(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    response = api_client.get(f"/api/v1/accounts/{uuid.uuid4()}", headers=manager_headers)
    assert response.status_code == 404


def test_update_account(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    create = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    account_id = create.json()["id"]
    response = api_client.patch(
        f"/api/v1/accounts/{account_id}",
        headers=manager_headers,
        json={"payment_status": "charge_off", "account_status": "charge_off"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["payment_status"] == "charge_off"
    assert data["risk_score"] >= 50


def test_delete_account(
    api_client: TestClient,
    auth_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    create = api_client.post(
        "/api/v1/accounts",
        headers=auth_headers,
        json=sample_account_payload(sample_case_id),
    )
    account_id = create.json()["id"]
    delete = api_client.delete(f"/api/v1/accounts/{account_id}", headers=auth_headers)
    assert delete.status_code == 204
    get_response = api_client.get(f"/api/v1/accounts/{account_id}", headers=auth_headers)
    assert get_response.status_code == 404


def test_delete_account_forbidden_for_manager(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    create = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    account_id = create.json()["id"]
    response = api_client.delete(f"/api/v1/accounts/{account_id}", headers=manager_headers)
    assert response.status_code == 403


def test_list_case_accounts(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    response = api_client.get(
        f"/api/v1/cases/{sample_case_id}/accounts",
        headers=manager_headers,
    )
    assert response.status_code == 200
    assert response.json()["total"] >= 1


def test_intelligence_summary(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json=sample_account_payload(sample_case_id),
    )
    response = api_client.get(
        "/api/v1/accounts/intelligence/summary",
        headers=manager_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_accounts"] >= 1
    assert "accounts_by_bureau" in data
    assert "next_action_queue" in data


def test_accounts_require_auth(api_client: TestClient) -> None:
    response = api_client.get("/api/v1/accounts")
    assert response.status_code == 401
