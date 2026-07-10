"""Resolve consent document templates and render signed PDFs."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.auth.models import Organization
from api.modules.clients.models import Client
from api.modules.compliance.consent_template_repository import ConsentDocumentTemplateRepository
from api.modules.compliance.consent_templates.context import (
    build_template_context,
    render_merge_fields,
)
from api.modules.compliance.consent_templates.defaults import DEFAULT_TEMPLATE_BY_KEY
from api.modules.compliance.consent_templates.keys import ConsentDocumentTemplateKey
from api.modules.compliance.consent_templates.renderer import build_consent_pdf_bytes
from api.modules.compliance.models import ConsentDocumentTemplate, ConsentTemplateReviewStatus


@dataclass(frozen=True, slots=True)
class ResolvedConsentTemplate:
    template_key: ConsentDocumentTemplateKey
    title: str
    body_text: str
    rendered_body: str
    legal_review_status: str
    is_customized: bool


class ConsentTemplateService:
    def __init__(self, template_repo: ConsentDocumentTemplateRepository) -> None:
        self._templates = template_repo

    @classmethod
    def from_session(cls, session: AsyncSession) -> ConsentTemplateService:
        return cls(ConsentDocumentTemplateRepository(session))

    async def resolve_template(
        self,
        *,
        organization_id: uuid.UUID,
        template_key: ConsentDocumentTemplateKey | str,
        organization: Organization,
        client: Client,
    ) -> ResolvedConsentTemplate:
        key = ConsentDocumentTemplateKey(str(template_key))
        default = DEFAULT_TEMPLATE_BY_KEY[key]
        stored = await self._templates.get_by_key(
            organization_id=organization_id,
            template_key=key.value,
        )

        title = stored.title if stored else default.title
        body_text = stored.body_text if stored else default.body_text
        merge_defaults = stored.merge_field_defaults if stored else None
        legal_review_status = (
            stored.legal_review_status if stored else ConsentTemplateReviewStatus.DRAFT.value
        )
        context = build_template_context(
            organization=organization,
            client=client,
            merge_field_defaults=merge_defaults,
        )
        rendered_body = render_merge_fields(body_text, context)
        return ResolvedConsentTemplate(
            template_key=key,
            title=title,
            body_text=body_text,
            rendered_body=rendered_body,
            legal_review_status=legal_review_status,
            is_customized=stored is not None,
        )

    async def list_resolved_templates(
        self,
        *,
        organization_id: uuid.UUID,
        organization: Organization,
        client: Client,
    ) -> list[ResolvedConsentTemplate]:
        items: list[ResolvedConsentTemplate] = []
        for template_key in ConsentDocumentTemplateKey:
            items.append(
                await self.resolve_template(
                    organization_id=organization_id,
                    template_key=template_key,
                    organization=organization,
                    client=client,
                )
            )
        return items

    async def upsert_org_template(
        self,
        *,
        organization_id: uuid.UUID,
        template_key: ConsentDocumentTemplateKey,
        title: str,
        body_text: str,
        merge_field_defaults: dict[str, str] | None,
        legal_review_status: str,
        user_id: uuid.UUID,
    ) -> ConsentDocumentTemplate:
        stored = await self._templates.get_by_key(
            organization_id=organization_id,
            template_key=template_key.value,
        )
        now = datetime.now(UTC)
        if stored is None:
            stored = ConsentDocumentTemplate(
                organization_id=organization_id,
                template_key=template_key.value,
                title=title,
                body_text=body_text,
                merge_field_defaults=merge_field_defaults,
                legal_review_status=legal_review_status,
                created_by_id=user_id,
                updated_by_id=user_id,
            )
            return await self._templates.create(stored)

        stored.title = title
        stored.body_text = body_text
        stored.merge_field_defaults = merge_field_defaults
        stored.legal_review_status = legal_review_status
        stored.updated_by_id = user_id
        stored.updated_at = now
        return await self._templates.save(stored)

    def render_signed_pdf(
        self,
        resolved: ResolvedConsentTemplate,
        *,
        signer_name: str,
        signed_at: datetime | None = None,
    ) -> bytes:
        signed_label = (signed_at or datetime.now(UTC)).strftime("%Y-%m-%d %H:%M UTC")
        return build_consent_pdf_bytes(
            title=resolved.title,
            body_text=resolved.rendered_body,
            signer_name=signer_name,
            signed_at_label=signed_label,
        )

    def render_preview_pdf(self, resolved: ResolvedConsentTemplate) -> bytes:
        return build_consent_pdf_bytes(
            title=resolved.title,
            body_text=resolved.rendered_body,
        )

    async def list_org_templates(
        self,
        *,
        organization_id: uuid.UUID,
    ) -> list[ConsentDocumentTemplate]:
        return await self._templates.list_for_organization(organization_id=organization_id)

    async def get_org_template_row(
        self,
        *,
        organization_id: uuid.UUID,
        template_key: ConsentDocumentTemplateKey,
    ) -> ConsentDocumentTemplate | None:
        return await self._templates.get_by_key(
            organization_id=organization_id,
            template_key=template_key.value,
        )
