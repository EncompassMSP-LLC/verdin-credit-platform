"""Client communication preferences helpers (LRP-209).

Staff-mediated tracking only. Never silently registers a phone with the National
Do Not Call Registry and never auto-transmits creditor/collector letters.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from api.modules.clients.models import (
    AttorneyRepresentationStatus,
    Client,
    ClientCommunicationPreferences,
    DncAssistanceStatus,
    PreferredCommunicationChannel,
)

OFFICIAL_DNC_REGISTRY_URL = "https://www.donotcall.gov/"

DNC_DISCLOSURE = (
    "Reduce many lawful telemarketing calls. This may not stop creditors, debt collectors, "
    "political calls, charities, surveys, or illegal callers. Registration is free via the "
    "official National Do Not Call Registry; online registration requires confirming an email "
    "within 72 hours. Lawful sales calls may take up to 31 days to stop after registration."
)

PREFERENCES_DISCLAIMER = (
    "Communication preferences and Do Not Call assistance are staff-mediated tracking aids. "
    "The platform never silently registers a phone number with the National Do Not Call "
    "Registry and never transmits cease-communication or collector opt-out letters without "
    "express client approval and staff review. Incomplete DNC registration is never shown as "
    "completed."
)


def append_preference_event(
    row: ClientCommunicationPreferences,
    *,
    action: str,
    actor_id: str | None,
    detail: str | None = None,
) -> None:
    events = list(row.preference_events or [])
    events.append(
        {
            "at": datetime.now(UTC).isoformat(),
            "action": action,
            "actor_id": actor_id,
            "detail": detail,
        }
    )
    row.preference_events = events[-50:]


def build_communication_request_draft(
    client: Client,
    prefs: ClientCommunicationPreferences,
) -> str:
    lines = [
        "DRAFT — Client-approved and staff-gated before any transmission",
        "",
        f"Re: Communication preferences for {client.display_name}",
        "",
        "Please honor the following communication preferences:",
        f"- Preferred channel: {prefs.preferred_channel.value}",
    ]
    if prefs.do_not_text:
        lines.append("- Do not send text messages (reply STOP / opt-out applies where required).")
    if prefs.do_not_email:
        lines.append("- Do not send email communications except as required by law.")
    if prefs.best_calling_hours:
        lines.append(f"- Best calling hours: {prefs.best_calling_hours}")
    if prefs.workplace_calls_prohibited:
        lines.append("- Do not call at my place of employment.")
    if prefs.attorney_representation_status == AttorneyRepresentationStatus.REPRESENTED:
        lines.append("- I am represented by an attorney; contact counsel as applicable.")
    if prefs.collector_opt_out_recorded:
        lines.append(
            "- A collector electronic-communication opt-out has been recorded in our file "
            "(tracking only — verify delivery separately)."
        )
    lines.extend(
        [
            "",
            "This draft does not constitute legal advice and has not been sent.",
        ]
    )
    return "\n".join(lines)


def default_preferences(
    *,
    organization_id: Any,
    client_id: Any,
) -> ClientCommunicationPreferences:
    return ClientCommunicationPreferences(
        organization_id=organization_id,
        client_id=client_id,
        preferred_channel=PreferredCommunicationChannel.MAIL,
        do_not_text=False,
        do_not_email=False,
        best_calling_hours=None,
        workplace_calls_prohibited=False,
        attorney_representation_status=AttorneyRepresentationStatus.UNKNOWN,
        collector_opt_out_recorded=False,
        collector_opt_out_recorded_at=None,
        dnc_assistance_requested=False,
        dnc_consent_attested=False,
        dnc_phone_ownership_confirmed=False,
        dnc_disclosure_acknowledged=False,
        dnc_phone_number=None,
        dnc_status=DncAssistanceStatus.NOT_STARTED,
        dnc_registry_opened_at=None,
        dnc_completed_at=None,
        dnc_followup_due_at=None,
        preference_events=[],
        notes=None,
    )


def followup_due_from(completed_at: datetime) -> datetime:
    return completed_at + timedelta(days=31)
