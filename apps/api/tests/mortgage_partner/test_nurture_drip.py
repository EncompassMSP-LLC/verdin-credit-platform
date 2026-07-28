"""LRP-206 — partner nurture drip programs, enrollments, and processing."""

import uuid
from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.mortgage_partner.nurture_models import NurtureChannel, PartnerNurtureStep


def test_nurture_program_seed_enroll_process_idempotent(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
) -> None:
    programs = api_client.get(
        "/api/v1/mortgage-partner/nurture/programs",
        headers=admin_headers,
    )
    assert programs.status_code == 200, programs.text
    rows = programs.json()
    assert len(rows) == 1
    program = rows[0]
    assert program["name"] == "Lender partnership drip"
    assert program["enrollment_lifecycle_stage"] == "lead"
    assert len(program["steps"]) == 5
    assert program["steps"][0]["delay_days"] == 0

    created = api_client.post(
        "/api/v1/mortgage-partner/nurture/enrollments",
        headers=admin_headers,
        json={
            "program_id": program["id"],
            "contact_name": "Jordan Lee",
            "contact_email": "jordan.nurture@example.com",
            "contact_phone": "+15551213001",
            "marketing_opt_in": True,
            "tcpa_consent": False,
        },
    )
    assert created.status_code == 201, created.text
    enrollment = created.json()
    assert enrollment["status"] == "active"
    assert enrollment["current_step_order"] == 1
    enrollment_id = enrollment["id"]

    processed = api_client.post(
        "/api/v1/mortgage-partner/nurture/process",
        headers=admin_headers,
    )
    assert processed.status_code == 200, processed.text
    result = processed.json()
    assert result["processed_count"] >= 1
    run = next(r for r in result["runs"] if r["enrollment_id"] == enrollment_id)
    assert run["channel"] == "email"
    assert run["status"] in {"sent", "deferred_email_not_ready", "failed"}
    assert run["payload"]["claim_safety"]["auto_filing"] is False
    assert run["payload"]["step_order"] == 1

    # Idempotent — same enrollment+step does not create a second delivery row
    again = api_client.post(
        "/api/v1/mortgage-partner/nurture/process",
        headers=admin_headers,
    )
    assert again.status_code == 200, again.text
    deliveries = api_client.get(
        "/api/v1/mortgage-partner/nurture/deliveries",
        headers=admin_headers,
        params={"enrollment_id": enrollment_id},
    )
    assert deliveries.status_code == 200, deliveries.text
    step1 = [d for d in deliveries.json() if d["payload"].get("step_order") == 1]
    assert len(step1) == 1

    enrolled = api_client.get(
        "/api/v1/mortgage-partner/nurture/enrollments",
        headers=admin_headers,
    )
    assert enrolled.status_code == 200, enrolled.text
    current = next(e for e in enrolled.json() if e["id"] == enrollment_id)
    assert current["current_step_order"] == 2
    assert current["status"] == "active"
    assert current["next_run_at"] is not None

    status = api_client.get("/api/v1/mortgage-partner/status", headers=admin_headers)
    assert status.status_code == 200
    assert "partner_nurture_drip" in status.json()["capabilities"]


def test_nurture_requires_marketing_opt_in(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
) -> None:
    programs = api_client.get(
        "/api/v1/mortgage-partner/nurture/programs",
        headers=admin_headers,
    )
    assert programs.status_code == 200, programs.text
    program_id = programs.json()[0]["id"]

    rejected = api_client.post(
        "/api/v1/mortgage-partner/nurture/enrollments",
        headers=admin_headers,
        json={
            "program_id": program_id,
            "contact_name": "No Opt In",
            "contact_email": "no-opt@example.com",
            "marketing_opt_in": False,
        },
    )
    assert rejected.status_code == 400, rejected.text


def test_nurture_pause_resume_and_opt_out(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
) -> None:
    programs = api_client.get(
        "/api/v1/mortgage-partner/nurture/programs",
        headers=admin_headers,
    )
    program_id = programs.json()[0]["id"]
    created = api_client.post(
        "/api/v1/mortgage-partner/nurture/enrollments",
        headers=admin_headers,
        json={
            "program_id": program_id,
            "contact_name": "Pause Me",
            "contact_email": "pause@example.com",
            "marketing_opt_in": True,
        },
    )
    assert created.status_code == 201, created.text
    enrollment_id = created.json()["id"]

    paused = api_client.patch(
        f"/api/v1/mortgage-partner/nurture/enrollments/{enrollment_id}",
        headers=admin_headers,
        json={"status": "paused"},
    )
    assert paused.status_code == 200, paused.text
    assert paused.json()["status"] == "paused"
    assert paused.json()["next_run_at"] is None

    processed = api_client.post(
        "/api/v1/mortgage-partner/nurture/process",
        headers=admin_headers,
    )
    assert processed.status_code == 200, processed.text
    assert all(r["enrollment_id"] != enrollment_id for r in processed.json()["runs"])

    resumed = api_client.patch(
        f"/api/v1/mortgage-partner/nurture/enrollments/{enrollment_id}",
        headers=admin_headers,
        json={"status": "active"},
    )
    assert resumed.status_code == 200, resumed.text
    assert resumed.json()["status"] == "active"
    assert resumed.json()["next_run_at"] is not None

    opted_out = api_client.patch(
        f"/api/v1/mortgage-partner/nurture/enrollments/{enrollment_id}",
        headers=admin_headers,
        json={"marketing_opt_in": False},
    )
    assert opted_out.status_code == 200, opted_out.text
    assert opted_out.json()["status"] == "exited"
    assert opted_out.json()["exit_reason"] == "marketing_opt_out"


async def test_nurture_sms_requires_tcpa_consent(
    api_client: TestClient,
    db_session: AsyncSession,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
) -> None:
    programs = api_client.get(
        "/api/v1/mortgage-partner/nurture/programs",
        headers=admin_headers,
    )
    assert programs.status_code == 200, programs.text
    program = programs.json()[0]
    step_id = uuid.UUID(program["steps"][0]["id"])

    step = await db_session.get(PartnerNurtureStep, step_id)
    assert step is not None
    step.channel = NurtureChannel.SMS
    await db_session.commit()

    created = api_client.post(
        "/api/v1/mortgage-partner/nurture/enrollments",
        headers=admin_headers,
        json={
            "program_id": program["id"],
            "contact_name": "SMS Lead",
            "contact_phone": "+15551213099",
            "marketing_opt_in": True,
            "tcpa_consent": False,
        },
    )
    assert created.status_code == 201, created.text
    enrollment_id = created.json()["id"]

    processed = api_client.post(
        "/api/v1/mortgage-partner/nurture/process",
        headers=admin_headers,
    )
    assert processed.status_code == 200, processed.text
    run = next(r for r in processed.json()["runs"] if r["enrollment_id"] == enrollment_id)
    assert run["channel"] == "sms"
    assert run["status"] == "deferred_tcpa_consent"


def test_nurture_timing_holds_future_steps(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
) -> None:
    programs = api_client.get(
        "/api/v1/mortgage-partner/nurture/programs",
        headers=admin_headers,
    )
    program = programs.json()[0]
    created = api_client.post(
        "/api/v1/mortgage-partner/nurture/enrollments",
        headers=admin_headers,
        json={
            "program_id": program["id"],
            "contact_name": "Timing Check",
            "contact_email": "timing@example.com",
            "marketing_opt_in": True,
        },
    )
    assert created.status_code == 201, created.text
    enrollment_id = created.json()["id"]

    first = api_client.post(
        "/api/v1/mortgage-partner/nurture/process",
        headers=admin_headers,
    )
    assert first.status_code == 200, first.text
    assert any(r["enrollment_id"] == enrollment_id for r in first.json()["runs"])

    enrollments = api_client.get(
        "/api/v1/mortgage-partner/nurture/enrollments",
        headers=admin_headers,
    )
    current = next(e for e in enrollments.json() if e["id"] == enrollment_id)
    assert current["current_step_order"] == 2
    next_run = datetime.fromisoformat(current["next_run_at"].replace("Z", "+00:00"))
    assert next_run > datetime.now(UTC) + timedelta(hours=12)

    second = api_client.post(
        "/api/v1/mortgage-partner/nurture/process",
        headers=admin_headers,
    )
    assert second.status_code == 200, second.text
    assert all(r["enrollment_id"] != enrollment_id for r in second.json()["runs"])


def test_nurture_tenant_isolation(
    api_client: TestClient,
    mortgage_partner_enabled: None,
    admin_headers: dict[str, str],
    other_admin_headers: dict[str, str],
) -> None:
    programs = api_client.get(
        "/api/v1/mortgage-partner/nurture/programs",
        headers=admin_headers,
    )
    program_id = programs.json()[0]["id"]
    created = api_client.post(
        "/api/v1/mortgage-partner/nurture/enrollments",
        headers=admin_headers,
        json={
            "program_id": program_id,
            "contact_name": "Org A Lead",
            "contact_email": "orga@example.com",
            "marketing_opt_in": True,
        },
    )
    assert created.status_code == 201, created.text
    enrollment_id = created.json()["id"]

    other_list = api_client.get(
        "/api/v1/mortgage-partner/nurture/enrollments",
        headers=other_admin_headers,
    )
    assert other_list.status_code == 200, other_list.text
    assert all(row["id"] != enrollment_id for row in other_list.json())

    other_patch = api_client.patch(
        f"/api/v1/mortgage-partner/nurture/enrollments/{enrollment_id}",
        headers=other_admin_headers,
        json={"status": "exited", "exit_reason": "cross_tenant"},
    )
    assert other_patch.status_code == 404, other_patch.text
