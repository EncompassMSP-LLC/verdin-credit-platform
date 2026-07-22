"""Versioned API router for v1."""

from fastapi import APIRouter

from api.core.router import router as system_router
from api.modules.accounts.router import router as accounts_router
from api.modules.auth.router import router as auth_router
from api.modules.billing.router import router as billing_router
from api.modules.cases.router import router as cases_router
from api.modules.client_portal.cases_router import router as client_portal_cases_router
from api.modules.client_portal.consents_router import router as client_portal_consents_router
from api.modules.client_portal.documents_router import router as client_portal_documents_router
from api.modules.client_portal.identity_theft_router import (
    router as client_portal_identity_theft_router,
)
from api.modules.client_portal.messaging_router import router as client_portal_messaging_router
from api.modules.client_portal.push_router import router as client_portal_push_router
from api.modules.client_portal.router import router as client_portal_router
from api.modules.clients.router import router as clients_router
from api.modules.compliance.router import router as compliance_router
from api.modules.dashboard.router import router as dashboard_router
from api.modules.documents.router import router as documents_router
from api.modules.enrollment.router import router as enrollment_router
from api.modules.enterprise.router import router as enterprise_router
from api.modules.llm.router import router as llm_router
from api.modules.messaging.router import router as messaging_router
from api.modules.mortgage_partner.router import router as mortgage_partner_router
from api.modules.notifications.router import router as notifications_router
from api.modules.org_admin.router import router as org_admin_router
from api.modules.reporting.router import router as reporting_router
from api.modules.tasks.router import router as tasks_router
from api.modules.timeline.router import router as timeline_router

router = APIRouter()
router.include_router(system_router)
router.include_router(auth_router)
router.include_router(cases_router)
router.include_router(clients_router)
router.include_router(enrollment_router)
router.include_router(compliance_router)
router.include_router(client_portal_router)
router.include_router(client_portal_cases_router)
router.include_router(client_portal_consents_router)
router.include_router(client_portal_identity_theft_router)
router.include_router(client_portal_documents_router)
router.include_router(client_portal_messaging_router)
router.include_router(client_portal_push_router)
router.include_router(dashboard_router)
router.include_router(accounts_router)
router.include_router(documents_router)
router.include_router(tasks_router)
router.include_router(notifications_router)
router.include_router(timeline_router)
router.include_router(enterprise_router)
router.include_router(org_admin_router)
router.include_router(mortgage_partner_router)
router.include_router(billing_router)
router.include_router(messaging_router)
router.include_router(llm_router)
router.include_router(reporting_router)

__all__ = ["router"]
