"""Application exception hierarchy."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api.core.responses import ErrorResponse


class VerdinError(Exception):
    """Base exception for application errors."""

    def __init__(self, message: str, code: str | None = None) -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class NotFoundError(VerdinError):
    """Resource not found."""


class UnauthorizedError(VerdinError):
    """Authentication required or invalid."""


class ForbiddenError(VerdinError):
    """Insufficient permissions."""


class ConflictError(VerdinError):
    """Resource conflict (e.g. duplicate)."""


class ValidationError(VerdinError):
    """Business rule validation failure."""


_STATUS_MAP: dict[type[VerdinError], int] = {
    NotFoundError: 404,
    UnauthorizedError: 401,
    ForbiddenError: 403,
    ConflictError: 409,
    ValidationError: 422,
}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(VerdinError)
    async def verdin_error_handler(_request: Request, exc: VerdinError) -> JSONResponse:
        status_code = _STATUS_MAP.get(type(exc), 400)
        body = ErrorResponse(detail=exc.message, code=exc.code)
        headers = {"WWW-Authenticate": "Bearer"} if isinstance(exc, UnauthorizedError) else None
        return JSONResponse(
            status_code=status_code,
            content=body.model_dump(),
            headers=headers,
        )
