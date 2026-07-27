"""Organization context dependency chain (authenticate → resolve org → flags)."""

import uuid
from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import Organization, OrganizationType, User
from api.modules.org_context.models import OrgDemoFeature
from api.modules.org_context.schemas import OrganizationContextResponse
from api.modules.org_context.service import OrgContextService


@dataclass(frozen=True, slots=True)
class ResolvedOrganizationContext:
    """Request-scoped organization + feature flags after authentication."""

    user: User
    organization: Organization
    feature_flags: dict[str, bool]
    demo_capabilities_allowed: bool

    @property
    def organization_id(self) -> uuid.UUID:
        return self.organization.id

    @property
    def organization_type(self) -> OrganizationType:
        return self.organization.organization_type

    def is_feature_enabled(self, feature: OrgDemoFeature) -> bool:
        return self.feature_flags.get(feature.value, False)


async def get_org_context_service(
    db: AsyncSession = Depends(get_db),
) -> OrgContextService:
    return OrgContextService.from_session(db)


async def get_organization_context(
    current_user: User = Depends(get_current_user),
    service: OrgContextService = Depends(get_org_context_service),
) -> ResolvedOrganizationContext:
    """
    Authenticate → resolve organization → load feature flags.

    Downstream handlers receive a fully resolved org context; production orgs
    never get demo_capabilities_allowed=True.
    """
    ctx = await service.build_context(current_user)
    org = await service.get_organization(ctx.organization_id)
    if org is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    return ResolvedOrganizationContext(
        user=current_user,
        organization=org,
        feature_flags=ctx.feature_flags,
        demo_capabilities_allowed=ctx.demo_capabilities_allowed,
    )


async def get_organization_context_response(
    current_user: User = Depends(get_current_user),
    service: OrgContextService = Depends(get_org_context_service),
) -> OrganizationContextResponse:
    return await service.build_context(current_user)
