"""Versioned API router for v1."""

from fastapi import APIRouter

from api.core.router import router as system_router
from api.modules.accounts.router import router as accounts_router
from api.modules.auth.router import router as auth_router
from api.modules.cases.router import router as cases_router
from api.modules.clients.router import router as clients_router
from api.modules.dashboard.router import router as dashboard_router
from api.modules.documents.router import router as documents_router
from api.modules.notifications.router import router as notifications_router
from api.modules.tasks.router import router as tasks_router
from api.modules.timeline.router import router as timeline_router

router = APIRouter()
router.include_router(system_router)
router.include_router(auth_router)
router.include_router(cases_router)
router.include_router(clients_router)
router.include_router(dashboard_router)
router.include_router(accounts_router)
router.include_router(documents_router)
router.include_router(tasks_router)
router.include_router(notifications_router)
router.include_router(timeline_router)

__all__ = ["router"]
