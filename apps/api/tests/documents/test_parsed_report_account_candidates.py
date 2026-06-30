"""Parsed credit report account candidate endpoint tests."""

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
) -> dict[str, Any]:
    response = api_client.post(
        "/api/v1/documents",
        headers=headers,
        data={"title": "Parsed Report", "case_id": case_id},
        files={"file": ("report.pdf", b"%PDF-1.4 parsed report", "application/pdf")},
    )
    assert response.status_code == 201, response.text
    return response.json()


async def test_get_parsed_credit_report_account_candidates(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
    db_session: AsyncSession,
) -> None:
    document = _upload_pdf(api_client, manager_headers, case_id=sample_case_id)
    parsed_at = datetime(2026, 6, 1, tzinfo=UTC)
    db_session.add(
        DocumentParsedCreditReport(
            id=uuid.uuid4(),
            document_id=uuid.UUID(document["id"]),
            organization_id=uuid.UUID(document["organization_id"]),
            schema_version="1.0",
            bureau="equifax",
            parser_name="equifax",
            parser_confidence=0.99,
            parsed_report={
                "accounts": [
                    {
                        "creditor_name": "Summit Retail Bank",
                        "account_number_masked": "****1111",
                        "account_type": "Revolving",
                        "account_status": "Late 30 Days",
                        "payment_status": "Late 30 Days",
                        "balance": 150.0,
                    },
                    {
                        "creditor_name": "Metro Auto Finance",
                        "account_number_masked": "****2222",
                        "account_type": "Auto Loan",
                        "payment_status": "Pays As Agreed",
                        "balance": 9000,
                    },
                    {
                        "account_number_masked": "****3333",
                        "balance": 50,
                    },
                ]
            },
            is_partial=False,
            warnings=[],
            parsed_at=parsed_at,
            created_at=parsed_at,
            updated_at=parsed_at,
        )
    )
    await db_session.commit()

    response = api_client.get(
        f"/api/v1/documents/{document['id']}/parsed-credit-report/account-candidates",
        headers=manager_headers,
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["document_id"] == document["id"]
    assert data["bureau"] == "equifax"
    assert len(data["candidates"]) == 2

    first, second = data["candidates"]
    assert first == {
        "source_index": 0,
        "case_id": sample_case_id,
        "bureau": "equifax",
        "creditor_name": "Summit Retail Bank",
        "original_creditor": None,
        "account_number_masked": "****1111",
        "account_type": "credit_card",
        "account_status": "open",
        "payment_status": "late_30",
        "balance": "150.00",
        "past_due_amount": None,
        "remarks": "Imported from parsed credit report",
    }
    assert second["creditor_name"] == "Metro Auto Finance"
    assert second["account_type"] == "auto"
    assert second["payment_status"] == "current"
