"""Bulk import parsed credit report tradelines into accounts."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.documents.test_parsed_report_account_candidates import (
    _parsed_accounts,
    _seed_parsed_report,
    _upload_pdf,
)


async def test_import_parsed_credit_report_accounts(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
    db_session: AsyncSession,
) -> None:
    document = _upload_pdf(api_client, manager_headers, case_id=sample_case_id)
    await _seed_parsed_report(db_session, document, accounts=_parsed_accounts())

    response = api_client.post(
        f"/api/v1/documents/{document['id']}/parsed-credit-report/import-accounts",
        headers=manager_headers,
        json={"skip_existing": True},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["document_id"] == document["id"]
    assert data["case_id"] == sample_case_id
    assert len(data["imported"]) == 2
    assert data["skipped_indices"] == []

    second = api_client.post(
        f"/api/v1/documents/{document['id']}/parsed-credit-report/import-accounts",
        headers=manager_headers,
        json={"skip_existing": True},
    )
    assert second.status_code == 200, second.text
    second_data = second.json()
    assert second_data["imported"] == []
    assert sorted(second_data["skipped_indices"]) == [0, 1]

    case_accounts = api_client.get(
        f"/api/v1/cases/{sample_case_id}/accounts",
        headers=manager_headers,
    )
    assert case_accounts.status_code == 200
    assert case_accounts.json()["total"] == 2
