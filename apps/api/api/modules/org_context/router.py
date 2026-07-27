"""Organization context + demo-capability endpoints (LRP-109)."""

from fastapi import APIRouter, Depends, HTTPException, status

from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.org_context.dependencies import get_org_context_service
from api.modules.org_context.models import OrgDemoFeature
from api.modules.org_context.schemas import (
    DemoSampleBorrowersRequest,
    DemoSampleBorrowersResponse,
    OrganizationContextResponse,
    OrganizationFeatureFlagUpsert,
)
from api.modules.org_context.service import OrgContextService

router = APIRouter(prefix="/org-context", tags=["Organization Context"])


@router.get("", response_model=OrganizationContextResponse)
async def get_organization_context(
    current_user: User = Depends(get_current_user),
    service: OrgContextService = Depends(get_org_context_service),
) -> OrganizationContextResponse:
    """Resolve organization type and per-org feature flags for the caller."""
    return await service.build_context(current_user)


@router.put("/feature-flags", response_model=OrganizationContextResponse)
async def upsert_organization_feature_flag(
    payload: OrganizationFeatureFlagUpsert,
    current_user: User = Depends(get_current_user),
    service: OrgContextService = Depends(get_org_context_service),
) -> OrganizationContextResponse:
    """Admin-only upsert of an organization feature flag (demo flags blocked on PRODUCTION)."""
    return await service.upsert_feature_flag(current_user, payload)


@router.post(
    "/demo/sample-borrowers",
    response_model=DemoSampleBorrowersResponse,
    status_code=201,
)
async def generate_sample_borrowers(
    payload: DemoSampleBorrowersRequest,
    current_user: User = Depends(get_current_user),
    service: OrgContextService = Depends(get_org_context_service),
) -> DemoSampleBorrowersResponse:
    """
    Generate sample borrowers for DEMO/INTERNAL/PARTNER orgs with the flag enabled.

    Always 403 for PRODUCTION organizations.
    """
    return await service.generate_sample_borrowers(current_user, payload)


@router.post("/demo/fake-credit-report", status_code=501)
async def generate_fake_credit_report(
    current_user: User = Depends(get_current_user),
    service: OrgContextService = Depends(get_org_context_service),
) -> None:
    """Guardrail: rejects PRODUCTION; otherwise deferred to dedicated demo seed scripts."""
    await service.assert_demo_feature(current_user, OrgDemoFeature.FAKE_CREDIT_REPORTS)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Fake credit report generation is reserved for dedicated demo seed scripts",
    )
