"""Secure message attachments (LRP-302B)."""

from __future__ import annotations

import io
import uuid

import pytest
from fastapi.testclient import TestClient

from api.core.feature_flags import get_feature_flags
from api.core.messaging import get_messaging_center_status
from api.modules.messaging.attachment_models import MessageAttachmentScanStatus
from api.modules.messaging.attachment_scan import sanitize_display_filename, scan_attachment_bytes
from tests.helpers.client_payload import sample_client_payload


@pytest.fixture
def portal_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_CLIENT_PORTAL", "true")
    get_feature_flags.cache_clear()
    yield
    get_feature_flags.cache_clear()


def _create_client(
    api_client: TestClient, headers: dict[str, str], *, email: str | None = None
) -> str:
    payload = sample_client_payload(display_name=f"Attach Client {uuid.uuid4().hex[:6]}")
    if email:
        payload["email"] = email
    response = api_client.post("/api/v1/clients", headers=headers, json=payload)
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _provision_and_login(
    api_client: TestClient,
    headers: dict[str, str],
    *,
    email: str,
) -> tuple[str, dict[str, str]]:
    client_id = _create_client(api_client, headers, email=email)
    provision = api_client.post(
        f"/api/v1/clients/{client_id}/portal-user",
        headers=headers,
        json={"email": email, "password": "password123", "send_invite": False},
    )
    assert provision.status_code == 201, provision.text
    login = api_client.post(
        "/api/v1/portal/auth/login",
        json={"email": email, "password": "password123"},
    )
    assert login.status_code == 200, login.text
    return client_id, {"Authorization": f"Bearer {login.json()['access_token']}"}


def _create_case(api_client: TestClient, headers: dict[str, str], client_id: str) -> str:
    response = api_client.post(
        "/api/v1/cases",
        headers=headers,
        json={"title": f"Attach Case {uuid.uuid4().hex[:6]}", "client_id": client_id},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _png_bytes() -> bytes:
    # Minimal valid 1x1 PNG
    return (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
        b"\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
    )


def test_sanitize_and_scan_policy() -> None:
    assert "../evil.exe" not in sanitize_display_filename("../evil.pdf")
    clean = scan_attachment_bytes(
        data=_png_bytes(),
        declared_mime="image/png",
        filename="photo.png",
        max_bytes=1024 * 1024,
        mode="policy",
    )
    assert clean.status is MessageAttachmentScanStatus.CLEAN

    rejected = scan_attachment_bytes(
        data=b"not-a-png",
        declared_mime="image/png",
        filename="photo.png",
        max_bytes=1024 * 1024,
        mode="policy",
    )
    assert rejected.status is MessageAttachmentScanStatus.REJECTED

    failed = scan_attachment_bytes(
        data=_png_bytes(),
        declared_mime="image/png",
        filename="photo.png",
        max_bytes=1024 * 1024,
        mode="required",
    )
    assert failed.status is MessageAttachmentScanStatus.FAILED


def test_attachment_support_capability() -> None:
    status = get_messaging_center_status()
    assert "attachment_support" in status.capabilities
    assert "attachment_support" not in status.deferred_capabilities


def test_portal_attach_send_download_and_isolation(
    api_client: TestClient,
    manager_headers: dict[str, str],
    portal_enabled: None,
) -> None:
    email_a = f"attach-a-{uuid.uuid4().hex[:8]}@example.com"
    email_b = f"attach-b-{uuid.uuid4().hex[:8]}@example.com"
    client_a, portal_a = _provision_and_login(api_client, manager_headers, email=email_a)
    _client_b, portal_b = _provision_and_login(api_client, manager_headers, email=email_b)
    case_a = _create_case(api_client, manager_headers, client_a)

    upload = api_client.post(
        f"/api/v1/portal/cases/{case_a}/messages/attachments",
        headers=portal_a,
        files={"file": ("note.png", io.BytesIO(_png_bytes()), "image/png")},
    )
    assert upload.status_code == 201, upload.text
    attachment = upload.json()
    assert attachment["scan_status"] == "clean"
    assert attachment["downloadable"] is True
    attachment_id = attachment["id"]

    # Pending/rejected cannot download until associated — drafts also blocked.
    blocked_draft = api_client.get(
        f"/api/v1/portal/cases/{case_a}/messages/attachments/{attachment_id}/download",
        headers=portal_a,
    )
    assert blocked_draft.status_code == 404

    send = api_client.post(
        f"/api/v1/portal/cases/{case_a}/messages",
        headers=portal_a,
        json={
            "body": "Here is a file",
            "attachment_ids": [attachment_id],
            "idempotency_key": f"msg-{uuid.uuid4().hex}",
        },
    )
    assert send.status_code == 201, send.text
    message = send.json()
    assert len(message["attachments"]) == 1
    assert message["attachments"][0]["id"] == attachment_id

    key = f"idem-{uuid.uuid4().hex}"
    first = api_client.post(
        f"/api/v1/portal/cases/{case_a}/messages",
        headers=portal_a,
        json={"body": "Idempotent body", "idempotency_key": key},
    )
    second = api_client.post(
        f"/api/v1/portal/cases/{case_a}/messages",
        headers=portal_a,
        json={"body": "Idempotent body changed", "idempotency_key": key},
    )
    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] == second.json()["id"]
    assert second.json()["body"] == "Idempotent body"

    download = api_client.get(
        f"/api/v1/portal/cases/{case_a}/messages/attachments/{attachment_id}/download",
        headers=portal_a,
    )
    assert download.status_code == 200
    assert download.content.startswith(b"\x89PNG")

    stolen = api_client.get(
        f"/api/v1/portal/cases/{case_a}/messages/attachments/{attachment_id}/download",
        headers=portal_b,
    )
    assert stolen.status_code == 404

    # Cannot reassociate already-linked attachment
    reuse = api_client.post(
        f"/api/v1/portal/cases/{case_a}/messages",
        headers=portal_a,
        json={"body": "Reuse", "attachment_ids": [attachment_id]},
    )
    assert reuse.status_code == 409


def test_staff_attach_and_unsupported_type(
    api_client: TestClient,
    manager_headers: dict[str, str],
    portal_enabled: None,
) -> None:
    email = f"attach-staff-{uuid.uuid4().hex[:8]}@example.com"
    client_id, _portal = _provision_and_login(api_client, manager_headers, email=email)
    case_id = _create_case(api_client, manager_headers, client_id)

    bad = api_client.post(
        f"/api/v1/cases/{case_id}/message-thread/attachments",
        headers=manager_headers,
        files={"file": ("evil.exe", io.BytesIO(b"MZ\x90\x00fake"), "application/octet-stream")},
    )
    assert bad.status_code == 422

    good = api_client.post(
        f"/api/v1/cases/{case_id}/message-thread/attachments",
        headers=manager_headers,
        files={"file": ("proof.png", io.BytesIO(_png_bytes()), "image/png")},
    )
    assert good.status_code == 201, good.text
    attachment_id = good.json()["id"]

    send = api_client.post(
        f"/api/v1/cases/{case_id}/message-thread/messages",
        headers=manager_headers,
        json={"body": "Staff file", "attachment_ids": [attachment_id]},
    )
    assert send.status_code == 201, send.text
    assert len(send.json()["attachments"]) == 1

    download = api_client.get(
        f"/api/v1/cases/{case_id}/message-thread/attachments/{attachment_id}/download",
        headers=manager_headers,
    )
    assert download.status_code == 200
