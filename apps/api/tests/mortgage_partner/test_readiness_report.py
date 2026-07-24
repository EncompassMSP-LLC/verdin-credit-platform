"""Tests for Mortgage Partner Readiness Report (slice 4)."""

from fastapi.testclient import TestClient

from api.modules.auth.models import Organization
from api.modules.clients.models import Client

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_partnership(
    api_client: TestClient,
    headers: dict[str, str],
    partner_org: Organization,
) -> str:
    resp = api_client.post(
        "/api/v1/mortgage-partner/partnerships",
        headers=headers,
        json={
            "partner_organization_id": str(partner_org.id),
            "display_name": "Readiness Test Lender",
            "partner_type": "lender",
            "status": "active",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def _create_referral(
    api_client: TestClient,
    headers: dict[str, str],
    partnership_id: str,
    client_id: str,
    case_id: str | None = None,
) -> str:
    body: dict = {"client_id": client_id}
    if case_id:
        body["case_id"] = case_id
    resp = api_client.post(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals",
        headers=headers,
        json=body,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def _create_case_with_account(
    api_client: TestClient,
    headers: dict[str, str],
    client_id: str,
) -> str:
    from tests.accounts.conftest import sample_account_payload

    case_resp = api_client.post(
        "/api/v1/cases",
        headers=headers,
        json={"title": "Readiness Test Case", "client_id": client_id},
    )
    assert case_resp.status_code == 201, case_resp.text
    case_id = case_resp.json()["id"]

    api_client.post(
        "/api/v1/accounts",
        headers=headers,
        json=sample_account_payload(case_id),
    )
    return case_id


def _publish_run(
    api_client: TestClient,
    headers: dict[str, str],
    case_id: str,
) -> str:
    run = api_client.post(
        f"/api/v1/cases/{case_id}/credit-analysis/runs",
        headers=headers,
    )
    assert run.status_code == 201, run.text
    return run.json()["id"]


# ---------------------------------------------------------------------------
# Status endpoint reflects readiness capabilities
# ---------------------------------------------------------------------------


def test_status_includes_readiness_capabilities(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
) -> None:
    resp = api_client.get("/api/v1/mortgage-partner/status", headers=admin_headers)
    assert resp.status_code == 200, resp.text
    caps = resp.json()["capabilities"]
    assert "partner_readiness_report" in caps
    assert "partner_readiness_export" in caps


# ---------------------------------------------------------------------------
# Readiness report — requires a linked case + published run
# ---------------------------------------------------------------------------


def test_readiness_report_requires_case(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
    partner_org: Organization,
    client_record: Client,
) -> None:
    """Referral without a case_id → 404."""
    partnership_id = _create_partnership(api_client, admin_headers, partner_org)
    referral_id = _create_referral(api_client, admin_headers, partnership_id, str(client_record.id))

    resp = api_client.get(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals/{referral_id}/readiness-report",
        headers=admin_headers,
    )
    assert resp.status_code == 404


def test_readiness_report_no_run_404(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
    partner_org: Organization,
    client_record: Client,
) -> None:
    """Referral linked to a case but no published run → 404."""
    partnership_id = _create_partnership(api_client, admin_headers, partner_org)

    case_resp = api_client.post(
        "/api/v1/cases",
        headers=admin_headers,
        json={"title": "No Run Case", "client_id": str(client_record.id)},
    )
    assert case_resp.status_code == 201, case_resp.text
    case_id = case_resp.json()["id"]

    referral_id = _create_referral(
        api_client, admin_headers, partnership_id, str(client_record.id), case_id
    )

    resp = api_client.get(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals/{referral_id}/readiness-report",
        headers=admin_headers,
    )
    assert resp.status_code == 404


def test_readiness_report_full_flow(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
    partner_org: Organization,
    client_record: Client,
) -> None:
    """Full happy path: partnership → referral with case → published run → readiness report."""
    partnership_id = _create_partnership(api_client, admin_headers, partner_org)
    case_id = _create_case_with_account(api_client, admin_headers, str(client_record.id))
    _publish_run(api_client, admin_headers, case_id)

    referral_id = _create_referral(
        api_client, admin_headers, partnership_id, str(client_record.id), case_id
    )

    resp = api_client.get(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals/{referral_id}/readiness-report",
        headers=admin_headers,
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["referral_id"] == referral_id
    assert body["case_id"] == case_id
    assert 0 <= body["mortgage_readiness_score"] <= 100
    assert body["band"] in {"building", "progressing", "near_ready", "lending_ready"}
    assert "disclaimer" in body
    assert "Lending Readiness" in body["disclaimer"]
    # Must not contain approval/guarantee language
    disclaimer = body["disclaimer"].lower()
    assert "guarantee" not in disclaimer or "not a guarantee" in disclaimer
    assert isinstance(body["dimensions"], list)
    assert isinstance(body["blockers"], list)
    assert isinstance(body["priority_tasks"], list)
    assert body["docs_status"] == "unknown"
    assert body["formula_version"]
    assert body["score_version"]


def test_readiness_report_audit_logged(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
    partner_org: Organization,
    client_record: Client,
) -> None:
    """Accessing a readiness report should log a readiness_view audit entry."""
    partnership_id = _create_partnership(api_client, admin_headers, partner_org)
    case_id = _create_case_with_account(api_client, admin_headers, str(client_record.id))
    _publish_run(api_client, admin_headers, case_id)
    referral_id = _create_referral(
        api_client, admin_headers, partnership_id, str(client_record.id), case_id
    )

    # Access the report
    api_client.get(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals/{referral_id}/readiness-report",
        headers=admin_headers,
    )

    audits = api_client.get("/api/v1/mortgage-partner/access-audits", headers=admin_headers)
    assert audits.status_code == 200, audits.text
    actions = [a["action"] for a in audits.json()]
    assert "readiness_view" in actions


# ---------------------------------------------------------------------------
# Readiness report export
# ---------------------------------------------------------------------------


def test_readiness_export_text(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
    partner_org: Organization,
    client_record: Client,
) -> None:
    partnership_id = _create_partnership(api_client, admin_headers, partner_org)
    case_id = _create_case_with_account(api_client, admin_headers, str(client_record.id))
    _publish_run(api_client, admin_headers, case_id)
    referral_id = _create_referral(
        api_client, admin_headers, partnership_id, str(client_record.id), case_id
    )

    export = api_client.get(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals/{referral_id}/readiness-report/export",
        headers=admin_headers,
        params={"format": "text"},
    )
    assert export.status_code == 200, export.text
    assert export.headers["content-type"].startswith("text/plain")
    assert "DISCLAIMER" in export.text
    assert "Lending Readiness" in export.text


def test_readiness_export_pdf(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
    partner_org: Organization,
    client_record: Client,
) -> None:
    partnership_id = _create_partnership(api_client, admin_headers, partner_org)
    case_id = _create_case_with_account(api_client, admin_headers, str(client_record.id))
    _publish_run(api_client, admin_headers, case_id)
    referral_id = _create_referral(
        api_client, admin_headers, partnership_id, str(client_record.id), case_id
    )

    export = api_client.get(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals/{referral_id}/readiness-report/export",
        headers=admin_headers,
        params={"format": "pdf"},
    )
    assert export.status_code == 200, export.text
    assert export.headers["content-type"] == "application/pdf"
    assert export.content[:4] == b"%PDF"


def test_readiness_export_audit_logged(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
    partner_org: Organization,
    client_record: Client,
) -> None:
    partnership_id = _create_partnership(api_client, admin_headers, partner_org)
    case_id = _create_case_with_account(api_client, admin_headers, str(client_record.id))
    _publish_run(api_client, admin_headers, case_id)
    referral_id = _create_referral(
        api_client, admin_headers, partnership_id, str(client_record.id), case_id
    )

    api_client.get(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals/{referral_id}/readiness-report/export",
        headers=admin_headers,
        params={"format": "text"},
    )

    audits = api_client.get("/api/v1/mortgage-partner/access-audits", headers=admin_headers)
    actions = [a["action"] for a in audits.json()]
    assert "readiness_export" in actions


# ---------------------------------------------------------------------------
# List readiness reports for a partnership
# ---------------------------------------------------------------------------


def test_list_readiness_reports_empty(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
    partner_org: Organization,
) -> None:
    """Partnership with no referrals → empty list."""
    partnership_id = _create_partnership(api_client, admin_headers, partner_org)

    resp = api_client.get(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/readiness-reports",
        headers=admin_headers,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json() == []


def test_list_readiness_reports_with_run(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
    partner_org: Organization,
    client_record: Client,
) -> None:
    """Partnership with a referral that has a published run → one summary returned."""
    partnership_id = _create_partnership(api_client, admin_headers, partner_org)
    case_id = _create_case_with_account(api_client, admin_headers, str(client_record.id))
    _publish_run(api_client, admin_headers, case_id)
    _create_referral(api_client, admin_headers, partnership_id, str(client_record.id), case_id)

    resp = api_client.get(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/readiness-reports",
        headers=admin_headers,
    )
    assert resp.status_code == 200, resp.text
    items = resp.json()
    assert len(items) == 1
    item = items[0]
    assert 0 <= item["mortgage_readiness_score"] <= 100
    assert item["band"] in {"building", "progressing", "near_ready", "lending_ready"}
    assert "disclaimer" in item


# ---------------------------------------------------------------------------
# Isolation: another org cannot see reports
# ---------------------------------------------------------------------------


def test_readiness_report_cross_org_404(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
    other_admin_headers: dict[str, str],
    partner_org: Organization,
    client_record: Client,
) -> None:
    """Other org cannot access readiness report for a different CRO's referral."""
    partnership_id = _create_partnership(api_client, admin_headers, partner_org)
    case_id = _create_case_with_account(api_client, admin_headers, str(client_record.id))
    _publish_run(api_client, admin_headers, case_id)
    referral_id = _create_referral(
        api_client, admin_headers, partnership_id, str(client_record.id), case_id
    )

    resp = api_client.get(
        f"/api/v1/mortgage-partner/partnerships/{partnership_id}/referrals/{referral_id}/readiness-report",
        headers=other_admin_headers,
    )
    assert resp.status_code == 404
