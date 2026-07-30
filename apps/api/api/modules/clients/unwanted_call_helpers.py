"""Unwanted-call complaint helpers (LRP-209A).

Advisory tracking + staff-gated draft text only. Never auto-submits complaints
and never draws legal conclusions or liability determinations.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from api.modules.clients.models import (
    AttorneyRepresentationStatus,
    Client,
    ClientCommunicationPreferences,
    DncAssistanceStatus,
)
from api.modules.clients.unwanted_call_models import (
    UnwantedCallChannel,
    UnwantedCallComplaintTarget,
    UnwantedCallIncident,
    UnwantedCallPartyType,
)

UNWANTED_CALL_DISCLAIMER = (
    "Unwanted-call incidents are staff-mediated tracking and draft aids only. "
    "Eligibility guidance is advisory and does not determine liability, TCPA "
    "violations, or legal outcomes. The platform never auto-submits complaints to "
    "the FTC, CFPB, state agencies, carriers, or the National Do Not Call Registry."
)


def snapshot_communication_preferences(
    prefs: ClientCommunicationPreferences | None,
) -> dict[str, Any]:
    if prefs is None:
        return {}
    return {
        "preferred_channel": prefs.preferred_channel.value,
        "do_not_text": prefs.do_not_text,
        "do_not_email": prefs.do_not_email,
        "best_calling_hours": prefs.best_calling_hours,
        "workplace_calls_prohibited": prefs.workplace_calls_prohibited,
        "attorney_representation_status": prefs.attorney_representation_status.value,
        "collector_opt_out_recorded": prefs.collector_opt_out_recorded,
        "dnc_assistance_requested": prefs.dnc_assistance_requested,
        "dnc_consent_attested": prefs.dnc_consent_attested,
        "dnc_phone_ownership_confirmed": prefs.dnc_phone_ownership_confirmed,
        "dnc_disclosure_acknowledged": prefs.dnc_disclosure_acknowledged,
        "dnc_phone_number": prefs.dnc_phone_number,
        "dnc_status": prefs.dnc_status.value,
        "dnc_completed_at": prefs.dnc_completed_at.isoformat() if prefs.dnc_completed_at else None,
        "dnc_followup_due_at": (
            prefs.dnc_followup_due_at.isoformat() if prefs.dnc_followup_due_at else None
        ),
    }


def build_eligibility_guidance(
    *,
    prefs: ClientCommunicationPreferences | None,
    called_at: datetime,
    party_type: UnwantedCallPartyType,
    channel: UnwantedCallChannel,
) -> dict[str, Any]:
    codes: list[str] = []
    notes: list[str] = []

    if prefs is None:
        codes.append("prefs_missing")
        notes.append("No communication preferences on file yet — capture prefs before advising.")
    else:
        if prefs.dnc_status == DncAssistanceStatus.COMPLETED and prefs.dnc_completed_at:
            if called_at >= prefs.dnc_completed_at:
                codes.append("call_after_dnc_completed")
                notes.append(
                    "Call occurred on or after staff-recorded DNC completion — review registry "
                    "timing (often up to 31 days for lawful sales calls)."
                )
            else:
                codes.append("call_before_dnc_completed")
                notes.append("Call occurred before staff-recorded DNC completion.")
        elif prefs.dnc_assistance_requested:
            codes.append("dnc_assistance_in_progress")
            notes.append("DNC assistance is in progress but not marked completed.")
        else:
            codes.append("dnc_not_started")
            notes.append("National DNC assistance has not been completed in-file.")

        if prefs.workplace_calls_prohibited:
            codes.append("workplace_calls_prohibited")
            notes.append("Client preference prohibits workplace calls.")

        if prefs.attorney_representation_status == AttorneyRepresentationStatus.REPRESENTED:
            codes.append("attorney_represented")
            notes.append(
                "Client marked as attorney-represented — route through counsel as applicable."
            )

        if prefs.collector_opt_out_recorded and party_type == UnwantedCallPartyType.COLLECTOR:
            codes.append("collector_opt_out_on_file")
            notes.append("Collector electronic-communication opt-out is recorded in-file.")

    if channel == UnwantedCallChannel.SMS:
        codes.append("sms_channel")
        notes.append("SMS/text channel — consider STOP / opt-out documentation separately.")

    if party_type == UnwantedCallPartyType.TELEMARKETER:
        codes.append("telemarketer_party")
        notes.append(
            "Telemarketer party — National DNC rules may be more relevant than creditor calls."
        )
    elif party_type in {UnwantedCallPartyType.CREDITOR, UnwantedCallPartyType.COLLECTOR}:
        codes.append("creditor_or_collector_party")
        notes.append(
            "Creditor/collector calls may continue despite DNC registration — use cease-comm / "
            "collector workflows as staff-gated drafts only."
        )

    summary = (
        "Advisory checklist only — staff should review facts with the client before any "
        "external complaint. No automatic eligibility determination."
    )
    return {
        "codes": codes,
        "notes": notes,
        "summary": summary,
        "disclaimer": UNWANTED_CALL_DISCLAIMER,
    }


def build_unwanted_call_complaint_draft(
    *,
    client: Client,
    incident: UnwantedCallIncident,
) -> str:
    party = incident.creditor_or_collector_name or incident.party_type.value
    lines = [
        "DRAFT — Staff-gated complaint narrative (never auto-submitted)",
        "",
        f"Consumer: {client.display_name}",
        f"Call date/time (UTC): {incident.called_at.isoformat()}",
        f"Channel: {incident.channel.value}",
        f"Party type: {incident.party_type.value}",
        f"Party name: {party}",
    ]
    if incident.caller_number:
        lines.append(f"Caller number: {incident.caller_number}")
    if incident.called_number:
        lines.append(f"Number called: {incident.called_number}")
    if incident.complaint_target != UnwantedCallComplaintTarget.NONE:
        lines.append(
            f"Intended complaint target (staff selection): {incident.complaint_target.value}"
        )
    if incident.notes:
        lines.extend(["", "Staff notes:", incident.notes])
    guidance = incident.eligibility_guidance or {}
    note_items = guidance.get("notes") if isinstance(guidance, dict) else None
    if isinstance(note_items, list) and note_items:
        lines.extend(["", "Advisory eligibility notes:"])
        for item in note_items:
            lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "This draft does not constitute legal advice and has not been filed with any agency.",
            UNWANTED_CALL_DISCLAIMER,
        ]
    )
    return "\n".join(lines)
