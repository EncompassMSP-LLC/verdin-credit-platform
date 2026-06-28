"""OpenAPI schema customization for versioned APIs."""

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from api.core.config import Settings
from api.versions.registry import get_registered_versions


def configure_openapi(app: FastAPI, settings: Settings) -> None:
    def custom_openapi() -> dict:
        if app.openapi_schema:
            return app.openapi_schema

        registered = get_registered_versions()
        active_versions = [v for v in registered if v.router.routes]

        openapi_schema = get_openapi(
            title=settings.app_name,
            version=settings.app_version,
            description=_build_api_description(settings, active_versions),
            routes=app.routes,
        )

        openapi_schema["servers"] = [
            {
                "url": api_version.prefix,
                "description": _server_description(api_version),
            }
            for api_version in active_versions
        ]

        openapi_schema["info"]["x-api-versioning"] = {
            "strategy": "url-path",
            "current": next(
                (v.version for v in active_versions if v.status == "current"),
                active_versions[0].version if active_versions else None,
            ),
            "versions": [
                {
                    "version": api_version.version,
                    "prefix": api_version.prefix,
                    "status": api_version.status,
                    "deprecated": api_version.deprecated,
                    "sunset": api_version.sunset,
                    "description": api_version.description,
                    "openapi": f"{api_version.prefix}/openapi.json",
                    "docs": f"{api_version.prefix}/docs",
                }
                for api_version in registered
            ],
            "discovery": "/api/versions",
        }

        openapi_schema["tags"] = _merge_tags(openapi_schema.get("tags", []), active_versions)

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi  # type: ignore[method-assign]


def _build_api_description(settings: Settings, versions: list) -> str:
    version_lines = "\n".join(
        f"- **{v.version}** (`{v.prefix}`) — {v.description}" for v in versions
    )
    return (
        f"{settings.app_name} — production-grade credit operations platform.\n\n"
        "## API Versioning\n\n"
        "All business endpoints are versioned under `/api/{{version}}`. "
        "Multiple API versions may run side by side during migration periods.\n\n"
        f"### Active versions\n\n{version_lines}\n\n"
        "Use `GET /api/versions` to discover supported versions at runtime."
    )


def _server_description(api_version) -> str:
    label = f"API {api_version.version}"
    if api_version.status == "current":
        return f"{label} (current)"
    if api_version.deprecated:
        return f"{label} (deprecated)"
    return f"{label} ({api_version.status})"


def _merge_tags(existing_tags: list[dict], versions: list) -> list[dict]:
    version_tag_names = {f"API {v.version}" for v in versions}
    filtered = [tag for tag in existing_tags if tag.get("name") not in version_tag_names]
    version_tags = [
        {
            "name": f"API {v.version}",
            "description": f"Routes served under `{v.prefix}`.",
        }
        for v in versions
    ]
    return version_tags + filtered
