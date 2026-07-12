"""Parsed credit report comparison endpoint tests."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.documents.parsed_report_models import DocumentParsedCreditReport


def _upload_pdf(
    api_client: TestClient,
    headers: dict[str, str],
    *,
    case_id: str,
    title: str,
    body: bytes,
) -> dict[str, Any]:
    response = api_client.post(
        "/api/v1/documents",
        headers=headers,
        data={"title": title, "case_id": case_id},
        files={"file": (f"{title.lower().replace(' ', '-')}.pdf", body, "application/pdf")},
    )
    assert response.status_code == 201, response.text
    return response.json()


async def _seed_parsed_report(
    db_session: AsyncSession,
    *,
    document: dict,
    parsed_at: datetime,
    accounts: list[dict[str, Any]],
    bureau: str = "equifax",
) -> None:
    db_session.add(
        DocumentParsedCreditReport(
            id=uuid.uuid4(),
            document_id=uuid.UUID(document["id"]),
            organization_id=uuid.UUID(document["organization_id"]),
            schema_version="1.0",
            bureau=bureau,
            parser_name=bureau,
            parser_confidence=0.99,
            parsed_report={"accounts": accounts},
            is_partial=False,
            warnings=[],
            parsed_at=parsed_at,
            created_at=parsed_at,
            updated_at=parsed_at,
        )
    )
    await db_session.commit()


async def test_compare_parsed_credit_report_to_previous_same_case_bureau(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
    db_session: AsyncSession,
) -> None:
    previous_document = _upload_pdf(
        api_client,
        manager_headers,
        case_id=sample_case_id,
        title="May Report",
        body=b"%PDF-1.4 may report",
    )
    current_document = _upload_pdf(
        api_client,
        manager_headers,
        case_id=sample_case_id,
        title="June Report",
        body=b"%PDF-1.4 june report",
    )

    await _seed_parsed_report(
        db_session,
        document=previous_document,
        parsed_at=datetime(2026, 5, 1, tzinfo=UTC),
        accounts=[
            {
                "creditor_name": "Summit Retail Bank",
                "account_number_masked": "****1111",
                "balance": 100.0,
                "payment_status": "Current",
            },
            {
                "creditor_name": "Metro Auto Finance",
                "account_number_masked": "****2222",
                "balance": 9000.0,
                "payment_status": "Current",
            },
            {
                "creditor_name": "Lakeside Credit Union",
                "account_number_masked": "****3333",
                "balance": 50.0,
                "payment_status": "Current",
            },
        ],
    )
    await _seed_parsed_report(
        db_session,
        document=current_document,
        parsed_at=datetime(2026, 6, 1, tzinfo=UTC),
        accounts=[
            {
                "creditor_name": "Summit Retail Bank",
                "account_number_masked": "****1111",
                "balance": 150.0,
                "payment_status": "Late 30 Days",
            },
            {
                "creditor_name": "Lakeside Credit Union",
                "account_number_masked": "****3333",
                "balance": 50.0,
                "payment_status": "Current",
            },
            {
                "creditor_name": "Northstar Recovery",
                "account_number_masked": "****4444",
                "balance": 640.0,
                "payment_status": "Collection",
            },
        ],
    )

    response = api_client.get(
        f"/api/v1/documents/{current_document['id']}/parsed-credit-report/comparison",
        headers=manager_headers,
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["document_id"] == current_document["id"]
    assert data["previous_document_id"] == previous_document["id"]
    assert data["summary"] == {
        "added": 1,
        "removed": 1,
        "changed": 1,
        "unchanged": 1,
    }

    changes = {change["change_type"]: change for change in data["account_changes"]}
    assert changes["changed"]["creditor_name"] == "Summit Retail Bank"
    assert changes["changed"]["previous_balance"] == 100.0
    assert changes["changed"]["current_balance"] == 150.0
    assert changes["changed"]["balance_delta"] == 50.0
    field_names = {diff["field"] for diff in changes["changed"]["field_diffs"]}
    assert "balance" in field_names
    assert "payment_status" in field_names
    assert changes["removed"]["creditor_name"] == "Metro Auto Finance"
    assert changes["added"]["creditor_name"] == "Northstar Recovery"


async def test_compare_parsed_credit_report_without_previous_marks_current_accounts_added(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
    db_session: AsyncSession,
) -> None:
    current_document = _upload_pdf(
        api_client,
        manager_headers,
        case_id=sample_case_id,
        title="First Report",
        body=b"%PDF-1.4 first report",
    )
    await _seed_parsed_report(
        db_session,
        document=current_document,
        parsed_at=datetime(2026, 6, 1, tzinfo=UTC),
        accounts=[
            {
                "creditor_name": "Summit Retail Bank",
                "account_number_masked": "****1111",
                "balance": 150.0,
                "payment_status": "Current",
            }
        ],
    )

    response = api_client.get(
        f"/api/v1/documents/{current_document['id']}/parsed-credit-report/comparison",
        headers=manager_headers,
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["previous_document_id"] is None
    assert data["summary"] == {"added": 1, "removed": 0, "changed": 0, "unchanged": 0}
    assert data["account_changes"][0]["change_type"] == "added"
