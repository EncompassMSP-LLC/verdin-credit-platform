"""Document classification endpoint tests."""

from unittest.mock import patch

from fastapi.testclient import TestClient
from verdin_document_classification import (
    ClassificationMethod,
    ClassificationResult,
    DocumentType,
)

from tests.documents.conftest import sample_pdf_upload


def test_classify_endpoint_persists_result(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    filename, file_obj, content_type = sample_pdf_upload()
    create = api_client.post(
        "/api/v1/documents",
        headers=manager_headers,
        data={"title": "Equifax Pull", "case_id": sample_case_id},
        files={"file": (filename, file_obj, content_type)},
    )
    document_id = create.json()["id"]

    with patch("api.modules.documents.service.run_document_classification") as mock_classify:
        mock_classify.return_value = ClassificationResult(
            document_type=DocumentType.CREDIT_REPORT,
            confidence_score=0.85,
            classification_method=ClassificationMethod.RULES,
            classifier_name="credit_report",
        )
        response = api_client.post(
            f"/api/v1/documents/{document_id}/classify",
            headers=manager_headers,
        )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["document_type"] == "credit_report"
    assert data["classification_method"] == "rules"
    assert data["confidence_score"] == 0.85


def test_get_classification(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    filename, file_obj, content_type = sample_pdf_upload()
    create = api_client.post(
        "/api/v1/documents",
        headers=manager_headers,
        data={"title": "Classify Me", "case_id": sample_case_id},
        files={"file": (filename, file_obj, content_type)},
    )
    document_id = create.json()["id"]

    with patch("api.modules.documents.service.run_document_classification") as mock_classify:
        mock_classify.return_value = ClassificationResult(
            document_type=DocumentType.UTILITY_BILL,
            confidence_score=0.8,
            classification_method=ClassificationMethod.RULES,
            classifier_name="utility_bill",
        )
        api_client.post(f"/api/v1/documents/{document_id}/classify", headers=manager_headers)

    response = api_client.get(
        f"/api/v1/documents/{document_id}/classification",
        headers=manager_headers,
    )
    assert response.status_code == 200
    assert response.json()["document_type"] == "utility_bill"
