"""Build merge-field context for consent document templates."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from typing import Any

from api.modules.auth.models import Organization
from api.modules.clients.address import format_client_mailing_address
from api.modules.clients.models import Client


def _add_business_days(start: date, days: int) -> date:
    current = start
    added = 0
    while added < days:
        current += timedelta(days=1)
        if current.weekday() < 5:
            added += 1
    return current


def default_merge_field_values(
    *,
    organization: Organization,
    client: Client,
    effective_date: date | None = None,
    overrides: dict[str, str] | None = None,
) -> dict[str, str]:
    effective = effective_date or datetime.now(UTC).date()
    cancellation_deadline = _add_business_days(effective, 3)
    authorization_expiration = effective.replace(year=effective.year + 1)

    values: dict[str, str] = {
        "organization_name": organization.name,
        "organization_address": "[Organization address — edit in Compliance → Consent templates]",
        "organization_phone": "[Organization phone]",
        "organization_email": "[Organization email]",
        "client_name": client.display_name,
        "client_address": format_client_mailing_address(client) or "[Client mailing address]",
        "client_email": client.email or "[Client email]",
        "client_phone": client.phone or "[Client phone]",
        "effective_date": effective.isoformat(),
        "cancellation_deadline_date": cancellation_deadline.isoformat(),
        "total_service_fee": "[Insert total fee or fee schedule]",
        "payment_terms": (
            "Fees are due according to the payment schedule in this agreement. "
            "No advance payment is collected before services are performed, except as "
            "permitted by applicable law and disclosed herein."
        ),
        "services_description": (
            "Review of consumer credit reports; identification of potentially inaccurate, "
            "incomplete, or unverifiable items; preparation and submission of dispute "
            "correspondence to consumer reporting agencies and data furnishers; and "
            "status updates related to dispute outcomes."
        ),
        "estimated_completion_time": "[Insert estimated completion timeline]",
        "guarantee_statement": (
            "Company does not guarantee deletion of any specific tradeline, a minimum credit "
            "score increase, or any particular bureau outcome."
        ),
        "state_law_notice": (
            "Georgia residents: additional rights may apply under Georgia consumer protection "
            "laws. Consult counsel to confirm required state disclosures."
        ),
        "governing_state": "Georgia",
        "dispute_resolution_clause": (
            "[Insert dispute resolution clause approved by counsel — e.g., mediation, "
            "arbitration, or court venue.]"
        ),
        "termination_notice_days": "30",
        "authorization_expiration": authorization_expiration.isoformat(),
        "client_date_of_birth": "[Date of birth]",
        "client_ssn_last4": "[Last 4 digits of SSN, if collected]",
        "client_prior_addresses": "[Prior addresses, if applicable]",
    }
    if overrides:
        values.update({key: str(value) for key, value in overrides.items() if value is not None})
    return values


def render_merge_fields(template_text: str, context: dict[str, str]) -> str:
    rendered = template_text
    for key, value in context.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    return rendered


def build_template_context(
    *,
    organization: Organization,
    client: Client,
    merge_field_defaults: dict[str, Any] | None = None,
    effective_date: date | None = None,
) -> dict[str, str]:
    overrides: dict[str, str] = {}
    if merge_field_defaults:
        overrides = {key: str(value) for key, value in merge_field_defaults.items()}
    return default_merge_field_values(
        organization=organization,
        client=client,
        effective_date=effective_date,
        overrides=overrides,
    )
