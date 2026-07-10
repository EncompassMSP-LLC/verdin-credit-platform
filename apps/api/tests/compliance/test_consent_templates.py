"""Unit tests for consent document template rendering."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from api.modules.auth.models import Organization
from api.modules.clients.models import Client, ClientStatus
from api.modules.compliance.consent_templates.context import (
    build_template_context,
    render_merge_fields,
)
from api.modules.compliance.consent_templates.defaults import DEFAULT_TEMPLATE_BY_KEY
from api.modules.compliance.consent_templates.keys import ConsentDocumentTemplateKey
from api.modules.compliance.consent_templates.renderer import build_consent_pdf_bytes


def _organization() -> Organization:
    return Organization(id=uuid.uuid4(), name="Demo Credit Repair LLC", slug="demo-credit")


def _client() -> Client:
    return Client(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        display_name="Jane Consumer",
        email="jane@example.com",
        phone="555-0100",
        mailing_address_line1="789 Peachtree St",
        mailing_city="Atlanta",
        mailing_state="GA",
        mailing_postal_code="30308",
        status=ClientStatus.ACTIVE,
    )


def test_render_merge_fields_includes_mailing_address() -> None:
    context = build_template_context(organization=_organization(), client=_client())
    assert context["client_address"] == "789 Peachtree St\nAtlanta, GA 30308"


def test_render_merge_fields_replaces_known_tokens() -> None:
    context = build_template_context(organization=_organization(), client=_client())
    body = DEFAULT_TEMPLATE_BY_KEY[ConsentDocumentTemplateKey.CROA_DISCLOSURE].body_text
    rendered = render_merge_fields(body, context)
    assert "Jane Consumer" in rendered
    assert "Demo Credit Repair LLC" in rendered
    assert "{{client_name}}" not in rendered


def test_build_consent_pdf_bytes_returns_pdf_header() -> None:
    context = build_template_context(organization=_organization(), client=_client())
    body = render_merge_fields(
        DEFAULT_TEMPLATE_BY_KEY[ConsentDocumentTemplateKey.FCRA_AUTHORIZATION].body_text,
        context,
    )
    pdf_bytes = build_consent_pdf_bytes(
        title="FCRA Authorization",
        body_text=body,
        signer_name="Jane Consumer",
        signed_at_label=datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC"),
    )
    assert pdf_bytes.startswith(b"%PDF")
