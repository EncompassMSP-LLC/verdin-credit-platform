"""Mortgage partner staff permissions (CRO operators managing partnerships)."""

from api.core.constants import UserRole
from api.modules.mortgage_partner.models import PartnerRole

# Staff (CRO) roles for managing the partnership scaffold
MORTGAGE_PARTNER_READ_ROLE = UserRole.CASE_MANAGER
MORTGAGE_PARTNER_WRITE_ROLE = UserRole.ADMIN

# Partnership-scoped capability matrix (edition overlay)
PARTNER_ROLE_PERMISSIONS: dict[PartnerRole, frozenset[str]] = {
    PartnerRole.LENDER_ADMIN: frozenset(
        {
            "partnership.view",
            "referrals.view",
            "referrals.manage",
            "members.view",
            "members.manage",
            "pipeline.view",
            "readiness.view",
            "readiness.export",
        }
    ),
    PartnerRole.LOAN_OFFICER: frozenset(
        {
            "partnership.view",
            "referrals.view",
            "referrals.manage",
            "members.view",
            "pipeline.view",
            "readiness.view",
            "readiness.export",
        }
    ),
    PartnerRole.CREDIT_OPS: frozenset(
        {
            "partnership.view",
            "referrals.view",
            "members.view",
            "pipeline.view",
            "readiness.view",
        }
    ),
    PartnerRole.UNDERWRITER_VIEW: frozenset(
        {
            "partnership.view",
            "referrals.view",
            "pipeline.view",
            "readiness.view",
            "readiness.export",
        }
    ),
    PartnerRole.READ_ONLY: frozenset(
        {
            "partnership.view",
            "referrals.view",
            "pipeline.view",
            "readiness.view",
        }
    ),
}


def partner_role_has_permission(role: PartnerRole, permission: str) -> bool:
    return permission in PARTNER_ROLE_PERMISSIONS.get(role, frozenset())
