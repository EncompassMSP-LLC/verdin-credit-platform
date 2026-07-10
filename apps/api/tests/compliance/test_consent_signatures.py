"""Signed consent upload, portal signing, and enforcement gate tests."""

import io
from collections.abc import Generator
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from api.core.feature_flags import get_feature_flags
from api.core.job_queue import JobMessage, JobType
from api.modules.documents.storage import (
    MemoryDocumentStorage,
    reset_document_storage,
    set_document_storage,
)
from tests.documents.conftest import sample_pdf_upload
from tests.helpers.client_payload import sample_client_payload


def _fake_enqueue(job_type: JobType, payload: dict | None = None) -> JobMessage:
    return JobMessage(job_type=job_type, payload=payload or {}, job_id="test-ocr-job")


@pytest.fixture(autouse=True)
def mock_ocr_enqueue() -> Generator[None]:
    with patch("api.modules.documents.service.enqueue_job", side_effect=_fake_enqueue):
        yield


@pytest.fixture(autouse=True)
def memory_storage() -> Generator[MemoryDocumentStorage]:
    storage = MemoryDocumentStorage()
    reset_document_storage()
    set_document_storage(storage)
    yield storage
    reset_document_storage()


def _create_client(api_client: TestClient, headers: dict[str, str]) -> str:
    response = api_client.post(
        "/api/v1/clients",
        headers=headers,
        json=sample_client_payload(
            display_name="Consent Client",
            email="consent-client@example.com",
        ),
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _create_case_for_client(
    api_client: TestClient,
    headers: dict[str, str],
    client_id: str,
) -> str:
    response = api_client.post(
        "/api/v1/cases",
        headers=headers,
        json={"title": "Consent Case", "client_id": client_id},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _upload_signed_consent(
    api_client: TestClient,
    headers: dict[str, str],
    *,
    client_id: str,
    case_id: str,
    consent_type: str,
    document_template_key: str,
    signer_name: str = "Jane Consumer",
) -> dict:
    response = api_client.post(
        "/api/v1/compliance/consents/upload",
        headers=headers,
        data={
            "client_id": client_id,
            "case_id": case_id,
            "consent_type": consent_type,
            "document_template_key": document_template_key,
            "signer_name": signer_name,
        },
        files={"file": ("signed-consent.pdf", sample_pdf_upload(), "application/pdf")},
    )
    assert response.status_code == 201, response.text
    return response.json()


def _grant_required_consents(
    api_client: TestClient,
    headers: dict[str, str],
    *,
    client_id: str,
    case_id: str,
) -> None:
    for template_key, consent_type in (
        ("croa_disclosure", "croa_services"),
        ("croa_service_agreement", "croa_services"),
        ("fcra_authorization", "fcra_dispute"),
    ):
        _upload_signed_consent(
            api_client,
            headers,
            client_id=client_id,
            case_id=case_id,
            consent_type=consent_type,
            document_template_key=template_key,
        )


def test_upload_signed_consent_record(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    client_id = _create_client(api_client, manager_headers)
    case_id = _create_case_for_client(api_client, manager_headers, client_id)

    created = _upload_signed_consent(
        api_client,
        manager_headers,
        client_id=client_id,
        case_id=case_id,
        consent_type="croa_services",
        document_template_key="croa_disclosure",
    )
    assert created["is_signed"] is True
    assert created["document_id"] is not None
    assert created["signature_method"] == "staff_upload"
    assert created["signer_name"] == "Jane Consumer"


def test_manual_consent_is_not_signed_without_document(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    client_id = _create_client(api_client, manager_headers)

    response = api_client.post(
        "/api/v1/compliance/consents",
        headers=manager_headers,
        json={
            "client_id": client_id,
            "consent_type": "croa_services",
            "source": "staff_ui",
        },
    )
    assert response.status_code == 201, response.text
    assert response.json()["is_signed"] is False


def test_get_client_consent_gaps(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    client_id = _create_client(api_client, manager_headers)
    case_id = _create_case_for_client(api_client, manager_headers, client_id)

    gaps = api_client.get(
        f"/api/v1/compliance/consents/gaps?client_id={client_id}",
        headers=manager_headers,
    )
    assert gaps.status_code == 200
    body = gaps.json()
    assert set(body["missing_template_keys"]) == {
        "croa_disclosure",
        "croa_service_agreement",
        "fcra_authorization",
    }
    assert set(body["missing_consent_types"]) == {"croa_services", "fcra_dispute"}

    _grant_required_consents(
        api_client,
        manager_headers,
        client_id=client_id,
        case_id=case_id,
    )

    gaps_after = api_client.get(
        f"/api/v1/compliance/consents/gaps?client_id={client_id}",
        headers=manager_headers,
    )
    assert gaps_after.status_code == 200
    assert gaps_after.json()["missing_template_keys"] == []
    assert gaps_after.json()["missing_consent_types"] == []


def test_mail_packet_export_blocked_without_signed_consents(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    client_id = _create_client(api_client, manager_headers)
    case_id = _create_case_for_client(api_client, manager_headers, client_id)

    account = api_client.post(
        "/api/v1/accounts",
        headers=manager_headers,
        json={
            "case_id": case_id,
            "creditor_name": "Example Bank",
            "bureau": "equifax",
            "account_type": "credit_card",
            "account_status": "open",
            "payment_status": "late_60",
            "account_number_masked": "****1234",
            "balance": "1500.00",
            "past_due_amount": "300.00",
        },
    )
    assert account.status_code == 201, account.text
    account_id = account.json()["id"]

    letter = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-draft/letters",
        headers=manager_headers,
    )
    assert letter.status_code == 201, letter.text
    letter_id = letter.json()["id"]

    blocked = api_client.get(
        f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/export",
        headers=manager_headers,
        params={"format": "mail-packet"},
    )
    assert blocked.status_code == 422
    detail = blocked.json()["detail"]
    assert "missing_consent_types" in detail

    _grant_required_consents(
        api_client,
        manager_headers,
        client_id=client_id,
        case_id=case_id,
    )

    allowed = api_client.get(
        f"/api/v1/accounts/{account_id}/dispute-letters/{letter_id}/export",
        headers=manager_headers,
        params={"format": "mail-packet"},
    )
    assert allowed.status_code == 200, allowed.text
    assert allowed.headers["content-type"] == "application/pdf"


@pytest.fixture
def portal_env(monkeypatch: pytest.MonkeyPatch) -> Generator[None]:
    monkeypatch.setenv("ENABLE_CLIENT_PORTAL", "true")
    get_feature_flags.cache_clear()
    yield
    get_feature_flags.cache_clear()


def test_portal_sign_consent(
    api_client: TestClient,
    manager_headers: dict[str, str],
    portal_env: None,
) -> None:
    client_id = _create_client(api_client, manager_headers)
    case_id = _create_case_for_client(api_client, manager_headers, client_id)

    provision = api_client.post(
        f"/api/v1/clients/{client_id}/portal-user",
        headers=manager_headers,
        json={"email": "portal-consent@example.com", "password": "password123"},
    )
    assert provision.status_code == 201, provision.text

    login = api_client.post(
        "/api/v1/portal/auth/login",
        json={"email": "portal-consent@example.com", "password": "password123"},
    )
    assert login.status_code == 200, login.text
    portal_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    requirements = api_client.get(
        f"/api/v1/portal/cases/{case_id}/consents",
        headers=portal_headers,
    )
    assert requirements.status_code == 200
    assert len(requirements.json()["items"]) == 3
    assert all(not item["is_signed"] for item in requirements.json()["items"])
    assert "legal_review_notice" in requirements.json()

    signature_png = io.BytesIO(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    for template_key in ("croa_disclosure", "croa_service_agreement", "fcra_authorization"):
        signed = api_client.post(
            f"/api/v1/portal/cases/{case_id}/consents/sign",
            headers=portal_headers,
            data={
                "template_key": template_key,
                "signer_name": "Jane Consumer",
                "attestation_accepted": "true",
            },
            files={"signature_file": ("signature.png", signature_png, "image/png")},
        )
        assert signed.status_code == 201, signed.text
        body = signed.json()
        assert body["is_signed"] is True
        assert body["signature_method"] == "portal_generated_document"
        assert body["document_template_key"] == template_key
        assert body["document_id"] is not None
        signature_png.seek(0)

    requirements_after = api_client.get(
        f"/api/v1/portal/cases/{case_id}/consents",
        headers=portal_headers,
    )
    assert requirements_after.status_code == 200
    assert all(item["is_signed"] for item in requirements_after.json()["items"])
