"""API versioning tests."""

import os

os.environ.setdefault("SECRET_KEY", "test-secret-key-minimum-32-characters-long")

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_all_v1_auth_routes_under_version_prefix() -> None:
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    paths = response.json().get("paths", {})
    auth_paths = [p for p in paths if p.startswith("/auth/")]
    assert auth_paths
    assert "/auth/login" in paths
    assert "/auth/me" in paths


def test_api_versions_discovery() -> None:
    response = client.get("/api/versions")
    assert response.status_code == 200
    data = response.json()
    assert data["current"] == "v1"
    assert len(data["versions"]) >= 1
    v1 = next(v for v in data["versions"] if v["version"] == "v1")
    assert v1["prefix"] == "/api/v1"
    assert v1["status"] == "current"
    assert v1["docs"] == "/api/v1/docs"
    assert v1["openapi"] == "/api/v1/openapi.json"


def test_v1_openapi_documentation() -> None:
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"].endswith("(v1)")
    assert schema["servers"][0]["url"] == "/api/v1"
    assert "x-api-version" in schema["info"]
    assert schema["info"]["x-api-version"]["version"] == "v1"
    paths = schema.get("paths", {})
    assert "/health" in paths
    assert "/auth/login" in paths


def test_global_openapi_includes_versioning_metadata() -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "x-api-versioning" in schema["info"]
    assert schema["info"]["x-api-versioning"]["current"] == "v1"
    assert any(server["url"] == "/api/v1" for server in schema["servers"])


def test_root_lists_version_endpoints() -> None:
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["api_version"] == "v1"
    assert data["api_base"] == "/api/v1"
    assert data["api_versions"] == "/api/versions"
