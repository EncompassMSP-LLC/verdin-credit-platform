"""Versioned API router for v1."""

from fastapi import APIRouter

from api.core.router import router as system_router
from api.modules.accounts.router import router as accounts_router
from api.modules.auth.router import router as auth_router
from api.modules.cases.router import router as cases_router

router = APIRouter()
router.include_router(system_router)
router.include_router(auth_router)
router.include_router(cases_router)
router.include_router(accounts_router)

__all__ = ["router"]
