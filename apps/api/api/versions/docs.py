"""Version-scoped OpenAPI and documentation endpoints."""

from fastapi import FastAPI, HTTPException
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, JSONResponse

from api.core.config import Settings
from api.versions.openapi import _build_api_description, _server_description
from api.versions.registry import get_registered_versions, get_version_by_name


def register_version_docs(app: FastAPI, settings: Settings) -> None:
    for api_version in get_registered_versions():
        _register_version_doc_routes(app, settings, api_version)


def _register_version_doc_routes(app: FastAPI, settings: Settings, api_version) -> None:
    version = api_version.version
    prefix = api_version.prefix
    openapi_path = f"{prefix}/openapi.json"
    docs_path = f"{prefix}/docs"
    redoc_path = f"{prefix}/redoc"
    title = f"{settings.app_name} — {version}"

    async def version_openapi() -> JSONResponse:
        schema = _build_version_openapi(settings, version)
        return JSONResponse(schema)

    async def version_swagger_ui() -> HTMLResponse:
        return get_swagger_ui_html(openapi_url=openapi_path, title=title)

    async def version_redoc() -> HTMLResponse:
        return get_redoc_html(openapi_url=openapi_path, title=title)

    app.add_api_route(
        openapi_path,
        version_openapi,
        methods=["GET"],
        include_in_schema=False,
        name=f"openapi_{version}",
    )
    app.add_api_route(
        docs_path,
        version_swagger_ui,
        methods=["GET"],
        include_in_schema=False,
        name=f"docs_{version}",
    )
    app.add_api_route(
        redoc_path,
        version_redoc,
        methods=["GET"],
        include_in_schema=False,
        name=f"redoc_{version}",
    )


def _build_version_openapi(settings: Settings, version: str) -> dict:
    api_version = get_version_by_name(version)
    if api_version is None:
        raise HTTPException(status_code=404, detail=f"API version '{version}' not found")

    prefix = api_version.prefix
    if not api_version.router.routes:
        raise HTTPException(status_code=404, detail=f"No routes registered for '{version}'")

    schema = get_openapi(
        title=f"{settings.app_name} ({version})",
        version=settings.app_version,
        description=_build_api_description(settings, [api_version]),
        routes=api_version.router.routes,
    )

    schema["servers"] = [
        {
            "url": prefix,
            "description": _server_description(api_version),
        }
    ]

    schema["info"]["x-api-version"] = {
        "version": api_version.version,
        "prefix": api_version.prefix,
        "status": api_version.status,
        "deprecated": api_version.deprecated,
    }

    return schema
