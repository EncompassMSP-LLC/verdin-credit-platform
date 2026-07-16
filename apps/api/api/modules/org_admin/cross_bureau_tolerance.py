"""Resolve org-scoped cross-bureau monetary tolerance."""

from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.accounts.cross_bureau import DEFAULT_BALANCE_TOLERANCE
from api.modules.org_admin.dispute_settings_models import (
    DEFAULT_CROSS_BUREAU_BALANCE_TOLERANCE,
    OrganizationDisputeSettings,
)
from api.modules.org_admin.dispute_settings_repository import OrganizationDisputeSettingsRepository


async def resolve_cross_bureau_balance_tolerance(
    session: AsyncSession | None,
    organization_id: uuid.UUID,
) -> Decimal:
    """Return the org's configured tolerance, or the platform default when unset."""
    if session is None:
        return DEFAULT_BALANCE_TOLERANCE
    settings = await OrganizationDisputeSettingsRepository(session).get_by_organization(
        organization_id
    )
    if settings is None:
        return DEFAULT_CROSS_BUREAU_BALANCE_TOLERANCE
    return settings.cross_bureau_balance_tolerance


def default_dispute_settings_response(
    organization_id: uuid.UUID,
) -> OrganizationDisputeSettings:
    """In-memory defaults before a row is persisted."""
    return OrganizationDisputeSettings(
        organization_id=organization_id,
        cross_bureau_balance_tolerance=DEFAULT_CROSS_BUREAU_BALANCE_TOLERANCE,
    )
