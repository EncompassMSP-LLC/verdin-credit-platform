"""Account management endpoint tests."""

import uuid

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
    assert any("balance" in item.lower() for item in data["evidence_checklist"])
    assert data["readiness_score"] is not None
    assert data["risk_score"] is not None


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
