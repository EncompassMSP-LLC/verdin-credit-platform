"""API tests for issue evidence vault links (LRP-208A)."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException
from fastapi.testclient import TestClient

from api.modules.documents.schemas import (
    CaseLitigationStrengthResponse,
    LitigationStrengthIssue,
    LitigationStrengthSummary,
)
from tests.documents.conftest import sample_pdf_upload


def _upload_doc(
    api_client: TestClient,
    headers: dict[str, str],
    case_id: str,
    *,
    title: str = "Evidence PDF",
) -> str:
    filename, file_obj, content_type = sample_pdf_upload()
    response = api_client.post(
        "/api/v1/documents",
        headers=headers,
        data={"title": title, "case_id": case_id},
        files={"file": (filename, file_obj, content_type)},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_create_list_delete_issue_evidence_link(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    document_id = _upload_doc(api_client, manager_headers, sample_case_id)
    source_id = "cross_bureau:capital one:4242:dofd_mismatch"

    create = api_client.post(
        f"/api/v1/cases/{sample_case_id}/issue-evidence-links",
        headers=manager_headers,
        json={
            "source_id": source_id,
            "document_id": document_id,
            "role": "supporting",
            "note": "Bank statement supporting DOFD",
        },
    )
    assert create.status_code == 201, create.text
    body = create.json()
    assert body["source_id"] == source_id
    assert body["document_id"] == document_id
    assert body["role"] == "supporting"
    assert body["document_title"] == "Evidence PDF"
    link_id = body["id"]

    listed = api_client.get(
        f"/api/v1/cases/{sample_case_id}/issue-evidence-links",
        headers=manager_headers,
    )
    assert listed.status_code == 200, listed.text
    items = listed.json()["items"]
    assert len(items) == 1
    assert items[0]["id"] == link_id

    filtered = api_client.get(
        f"/api/v1/cases/{sample_case_id}/issue-evidence-links",
        headers=manager_headers,
        params={"source_id": source_id},
    )
    assert filtered.status_code == 200
    assert len(filtered.json()["items"]) == 1

    dup = api_client.post(
        f"/api/v1/cases/{sample_case_id}/issue-evidence-links",
        headers=manager_headers,
        json={"source_id": source_id, "document_id": document_id},
    )
    assert dup.status_code == 409

    deleted = api_client.delete(
        f"/api/v1/cases/{sample_case_id}/issue-evidence-links/{link_id}",
        headers=manager_headers,
    )
    assert deleted.status_code == 204

    after = api_client.get(
        f"/api/v1/cases/{sample_case_id}/issue-evidence-links",
        headers=manager_headers,
    )
    assert after.status_code == 200
    assert after.json()["items"] == []


def test_issue_evidence_link_emits_timeline_events(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    document_id = _upload_doc(api_client, manager_headers, sample_case_id, title="Timeline Ev")
    source_id = "cross_bureau:timeline:dofd"

    create = api_client.post(
        f"/api/v1/cases/{sample_case_id}/issue-evidence-links",
        headers=manager_headers,
        json={"source_id": source_id, "document_id": document_id, "role": "supporting"},
    )
    assert create.status_code == 201, create.text
    link_id = create.json()["id"]

    linked = api_client.get(
        "/api/v1/timeline",
        headers=manager_headers,
        params={
            "case_id": sample_case_id,
            "event_type": "ISSUE_EVIDENCE_LINKED",
            "source_id": source_id,
        },
    )
    assert linked.status_code == 200, linked.text
    assert linked.json()["total"] >= 1
    item = linked.json()["items"][0]
    assert item["metadata"]["source_id"] == source_id
    assert item["metadata"]["link_id"] == link_id
    assert item["document_id"] == document_id

    deleted = api_client.delete(
        f"/api/v1/cases/{sample_case_id}/issue-evidence-links/{link_id}",
        headers=manager_headers,
    )
    assert deleted.status_code == 204

    removed = api_client.get(
        "/api/v1/timeline",
        headers=manager_headers,
        params={
            "case_id": sample_case_id,
            "event_type": "ISSUE_EVIDENCE_REMOVED",
            "source_id": source_id,
        },
    )
    assert removed.status_code == 200
    assert removed.json()["total"] >= 1


def test_issue_evidence_link_rejects_foreign_case_document(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    other_case = api_client.post(
        "/api/v1/cases",
        headers=manager_headers,
        json={"title": "Other Case", "client_name": "Other"},
    )
    assert other_case.status_code == 201
    other_case_id = other_case.json()["id"]
    document_id = _upload_doc(api_client, manager_headers, other_case_id, title="Wrong case")

    response = api_client.post(
        f"/api/v1/cases/{sample_case_id}/issue-evidence-links",
        headers=manager_headers,
        json={
            "source_id": "metro2:experian:rule#0@aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            "document_id": document_id,
        },
    )
    assert response.status_code == 422
    assert "same case" in response.json()["detail"].lower()


def test_explainability_includes_associated_documents(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    source_id = "cross_bureau:x:dofd"
    document_id = _upload_doc(api_client, manager_headers, sample_case_id, title="Linked Stmt")
    linked = api_client.post(
        f"/api/v1/cases/{sample_case_id}/issue-evidence-links",
        headers=manager_headers,
        json={"source_id": source_id, "document_id": document_id, "role": "primary"},
    )
    assert linked.status_code == 201, linked.text

    strength = CaseLitigationStrengthResponse(
        case_id=uuid.UUID(sample_case_id),
        summary=LitigationStrengthSummary(
            issues_scored=1,
            high_priority=1,
            medium_priority=0,
            low_priority=0,
            top_score=98,
            average_score=98.0,
        ),
        issues=[
            LitigationStrengthIssue(
                source_kind="cross_bureau",
                source_id=source_id,
                rule_id="cross_bureau.dofd_mismatch",
                score=98,
                rank=1,
                title="DOFD mismatch",
                rationale="Conflicting DOFD across bureaus.",
                severity="high",
                bureau=None,
                creditor_name="Capital One",
                account_number_masked="****4242",
                match_key="capital one:4242",
                factors=["dofd_mismatch"],
            )
        ],
    )
    with (
        patch(
            "api.modules.documents.service.DocumentService.get_case_litigation_strength",
            new_callable=AsyncMock,
            return_value=strength,
        ),
        patch(
            "api.modules.documents.service.DocumentService.get_case_compliance_evidence_links",
            new_callable=AsyncMock,
            side_effect=HTTPException(status_code=404, detail="No evidence"),
        ),
    ):
        response = api_client.get(
            f"/api/v1/cases/{sample_case_id}/issue-explainability",
            headers=manager_headers,
        )

    assert response.status_code == 200, response.text
    card = response.json()["cards"][0]
    assert len(card["associated_documents"]) == 1
    assert card["associated_documents"][0]["document_id"] == document_id
    assert card["associated_documents"][0]["role"] == "primary"
    assert card["associated_documents"][0]["title"] == "Linked Stmt"
