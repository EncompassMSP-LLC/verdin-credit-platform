"""Organization context + demo capability guardrails."""

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.audit import apply_audit_on_create, apply_audit_on_update
from api.core.config import get_settings
from api.core.constants import UserRole
from api.core.permissions import has_permission
from api.modules.auth.models import Organization, OrganizationType, User
from api.modules.clients.models import Client, ClientStatus
from api.modules.org_context.models import OrganizationFeatureFlag, OrgDemoFeature
from api.modules.org_context.repository import OrgContextRepository
from api.modules.org_context.schemas import (
    DemoSampleBorrowersRequest,
    DemoSampleBorrowersResponse,
    OrganizationContextResponse,
    OrganizationFeatureFlagUpsert,
)


class OrgContextService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = OrgContextRepository(session)

    @classmethod
    def from_session(cls, session: AsyncSession) -> "OrgContextService":
        return cls(session)

    def _require_organization_id(self, user: User) -> uuid.UUID:
        if user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to an organization",
            )
        return user.organization_id

    async def get_organization(self, organization_id: uuid.UUID) -> Organization | None:
        return await self._repo.get_organization(organization_id)

    async def _require_organization(self, organization_id: uuid.UUID) -> Organization:
        org = await self.get_organization(organization_id)
        if org is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )
        return org

    async def build_context(self, user: User) -> OrganizationContextResponse:
        org_id = self._require_organization_id(user)
        org = await self._require_organization(org_id)
        settings = get_settings()
        flags = await self._repo.list_feature_flags(org_id)
        flag_map = {feature.value: False for feature in OrgDemoFeature}
        for row in flags:
            flag_map[row.feature.value] = row.enabled
        return OrganizationContextResponse(
            organization_id=org.id,
            name=org.name,
            slug=org.slug,
            organization_type=org.organization_type,
            is_active=org.is_active,
            feature_flags=flag_map,
            demo_capabilities_allowed=self.demo_capabilities_allowed(org),
            allow_demo_orgs=settings.allow_demo_orgs,
            enable_sample_data=settings.enable_sample_data,
            enable_demo_login=settings.enable_demo_login,
            created_at=org.created_at,
        )

    def demo_capabilities_allowed(self, org: Organization) -> bool:
        settings = get_settings()
        if org.organization_type == OrganizationType.PRODUCTION:
            return False
        if not settings.allow_demo_orgs:
            return False
        if org.organization_type == OrganizationType.DEMO:
            return True
        if org.organization_type in (OrganizationType.INTERNAL, OrganizationType.PARTNER):
            return settings.enable_sample_data
        return False

    async def assert_demo_feature(self, user: User, feature: OrgDemoFeature) -> Organization:
        """Reject demo-only operations for PRODUCTION or when the org flag is off."""
        org_id = self._require_organization_id(user)
        org = await self._require_organization(org_id)

        if org.organization_type == OrganizationType.PRODUCTION:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Demo operation '{feature.value}' is blocked for production organizations"
                ),
            )

        if not self.demo_capabilities_allowed(org):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Demo capabilities are disabled by server configuration",
            )

        flag = await self._repo.get_feature_flag(org_id, feature)
        if flag is None or not flag.enabled:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Organization feature '{feature.value}' is not enabled",
            )
        return org

    async def upsert_feature_flag(
        self, user: User, payload: OrganizationFeatureFlagUpsert
    ) -> OrganizationContextResponse:
        if not has_permission(user.role, UserRole.ADMIN):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin role required to manage organization feature flags",
            )
        org_id = self._require_organization_id(user)
        org = await self._require_organization(org_id)

        if (
            org.organization_type == OrganizationType.PRODUCTION
            and payload.enabled
            and payload.feature
            in {
                OrgDemoFeature.DEMO_DATA,
                OrgDemoFeature.SAMPLE_BORROWERS,
                OrgDemoFeature.FAKE_CREDIT_REPORTS,
                OrgDemoFeature.DEMO_NOTIFICATIONS,
            }
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot enable demo features on a production organization",
            )

        existing = await self._repo.get_feature_flag(org_id, payload.feature)
        if existing is None:
            row = OrganizationFeatureFlag(
                id=uuid.uuid4(),
                organization_id=org_id,
                feature=payload.feature,
                enabled=payload.enabled,
            )
            apply_audit_on_create(row, user.id)
            await self._repo.upsert_feature_flag(row)
        else:
            existing.enabled = payload.enabled
            apply_audit_on_update(existing, user.id)
            await self._repo.save_feature_flag(existing)

        await self._session.commit()
        return await self.build_context(user)

    async def generate_sample_borrowers(
        self, user: User, payload: DemoSampleBorrowersRequest
    ) -> DemoSampleBorrowersResponse:
        if not has_permission(user.role, UserRole.CASE_MANAGER):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Case manager role required to generate sample borrowers",
            )
        org = await self.assert_demo_feature(user, OrgDemoFeature.SAMPLE_BORROWERS)
        settings = get_settings()
        if not settings.enable_sample_data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="ENABLE_SAMPLE_DATA is false",
            )

        created_ids: list[uuid.UUID] = []
        for idx in range(payload.count):
            client = Client(
                id=uuid.uuid4(),
                organization_id=org.id,
                display_name=f"Sample Borrower {idx + 1}",
                email=f"sample.borrower.{uuid.uuid4().hex[:8]}@demo.local",
                phone="555-0100",
                mailing_address_line1="100 Demo Way",
                mailing_city="Austin",
                mailing_state="TX",
                mailing_postal_code="78701",
                status=ClientStatus.ACTIVE,
                notes="Generated by demo sample-borrowers API — not production data",
            )
            apply_audit_on_create(client, user.id)
            self._session.add(client)
            created_ids.append(client.id)

        await self._session.commit()
        return DemoSampleBorrowersResponse(
            created_client_ids=created_ids,
            organization_id=org.id,
        )
