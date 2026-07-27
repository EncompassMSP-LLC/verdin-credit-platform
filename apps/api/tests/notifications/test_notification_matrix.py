"""Notification matrix v1 tests (LRP-202)."""

from fastapi.testclient import TestClient

from api.modules.notifications.notification_matrix import (
    NotificationMatrixEvent,
    list_matrix_events,
)


def test_matrix_catalog_includes_referral_events() -> None:
    events = {definition.event for definition in list_matrix_events()}
    assert NotificationMatrixEvent.REFERRAL_SUBMITTED in events
    assert NotificationMatrixEvent.REFERRAL_ASSIGNED in events
    assert NotificationMatrixEvent.READINESS_REPORT_AVAILABLE in events
    assert NotificationMatrixEvent.SLA_BREACH_REFERRAL_ACK in events


def test_get_notification_matrix(
    api_client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    response = api_client.get("/api/v1/notifications/matrix", headers=admin_headers)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["schema_version"] == "notification-matrix.v1"
    assert body["sms_requires_tcpa_consent"] is True
    assert body["claim_safety"]["auto_filing"] is False
    assert len(body["events"]) >= 10
    referral = next(e for e in body["events"] if e["event"] == "referral_submitted")
    audiences = {route["audience"] for route in referral["routes"]}
    assert "partner_success" in audiences
    assert "borrower" in audiences

    empty = api_client.get(
        "/api/v1/notifications/matrix/dispatches",
        headers=admin_headers,
        params={"event_key": "website_contact"},
    )
    assert empty.status_code == 200
    assert empty.json() == []
