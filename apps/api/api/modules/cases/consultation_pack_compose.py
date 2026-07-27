"""Compose draft consultation-completed pack artifacts (LRP-204)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from api.modules.accounts.credit_analysis import ADVISORY_DISCLAIMER
from api.modules.accounts.credit_analysis_run_models import CreditAnalysisRun
from api.modules.cases.models import Case

SCHEMA_VERSION = "consultation-pack.v1"

_BAND_LABELS = {
    "building": "Building",
    "progressing": "Progressing",
    "near_ready": "Near Ready",
    "lending_ready": "Lending Ready",
}


def compose_consultation_pack(
    *,
    case: Case,
    run: CreditAnalysisRun | None,
    client_display_name: str | None = None,
) -> dict[str, Any]:
    """Build draft advisory artifacts for staff review. Never transmits."""
    now = datetime.now(UTC).isoformat()
    payload = run.payload if run is not None else {}
    band = run.band if run is not None else None
    band_label = _BAND_LABELS.get(band or "", band.replace("_", " ").title() if band else "N/A")
    blockers = list(payload.get("blockers") or [])
    dimensions = list(payload.get("dimensions") or [])

    readiness_snapshot = {
        "title": "Advisory Readiness Score snapshot",
        "status": "draft" if run is not None else "missing_readiness",
        "band": band,
        "band_label": band_label,
        "credit_analysis_run_id": str(run.id) if run is not None else None,
        "generated_at": run.generated_at.isoformat() if run is not None else None,
        "disclaimer": ADVISORY_DISCLAIMER,
        "dimensions": dimensions,
        "blockers": blockers,
        "notes": (
            "Band is the borrower-facing source of truth. Numeric scores are staff-only."
            if run is not None
            else "Publish a Lending Readiness run before packaging a full readiness snapshot."
        ),
    }

    timeline_items: list[dict[str, str]] = [
        {
            "at": case.opened_at.isoformat() if case.opened_at else now,
            "title": "Case opened",
            "detail": f"{case.title} · stage {case.stage.value}",
        },
    ]
    if run is not None:
        timeline_items.append(
            {
                "at": (run.published_at or run.generated_at).isoformat(),
                "title": "Readiness report published",
                "detail": f"Advisory band: {band_label}",
            }
        )
    timeline_items.append(
        {
            "at": now,
            "title": "Consultation completed pack drafted",
            "detail": "Staff-gated draft artifacts ready for review (not sent).",
        }
    )
    timeline = {
        "title": "Illustrative readiness timeline",
        "status": "draft",
        "disclaimer": (
            "Illustrative milestones for staff/partner conversation only — "
            "not a guarantee of timing, approval, or funding."
        ),
        "items": timeline_items,
    }

    action_plan = {
        "title": "Action plan / tasks",
        "status": "draft",
        "items": [
            {
                "id": b.get("id"),
                "title": b.get("title"),
                "impact": b.get("impact"),
                "action": b.get("action"),
            }
            for b in blockers
        ]
        or [
            {
                "id": "baseline-review",
                "title": "Review readiness with borrower",
                "impact": "Align on next documentation and dispute steps.",
                "action": "Confirm portal checklist tasks with the borrower.",
            }
        ],
        "notes": "Portal checklist items should stay in sync with published readiness blockers.",
    }

    borrower = client_display_name or case.client_name or "Borrower"
    status_report = {
        "title": "Status report stub",
        "status": "draft",
        "body": (
            f"Status update for {borrower} (case: {case.title}).\n\n"
            f"Current case stage: {case.stage.value.replace('_', ' ')}.\n"
            f"Advisory readiness band: {band_label}.\n\n"
            "This stub is for staff editing before any partner share. It is not an "
            "underwriting decision and does not guarantee loan approval or terms.\n\n"
            f"{ADVISORY_DISCLAIMER}"
        ),
    }

    partner_notification = {
        "title": "Partner notification draft",
        "status": "draft_never_sent",
        "channel": "email",
        "subject": f"Consultation completed — {borrower} (advisory update)",
        "body": (
            f"Hello,\n\n"
            f"The consultation for {borrower} is marked complete and a draft readiness "
            f"pack is ready for staff review.\n\n"
            f"Advisory readiness band: {band_label}.\n"
            f"Case stage: {case.stage.value.replace('_', ' ')}.\n\n"
            "This message is a draft only and was not sent automatically. "
            "Review and send manually if your partnership policy requires an update.\n\n"
            f"{ADVISORY_DISCLAIMER}\n"
        ),
        "send_policy": "Staff must explicitly review and send; never auto-transmitted.",
    }

    return {
        "schema_version": SCHEMA_VERSION,
        "disclaimer": ADVISORY_DISCLAIMER,
        "case_id": str(case.id),
        "case_title": case.title,
        "artifacts": {
            "readiness_snapshot": readiness_snapshot,
            "timeline": timeline,
            "action_plan": action_plan,
            "status_report": status_report,
            "partner_notification": partner_notification,
        },
        "send_guardrails": {
            "auto_transmit": False,
            "partner_notification_sent": False,
            "requires_staff_review": True,
        },
    }
