"""Pytest configuration for the end-to-end workflow suite.

Responsibilities:

* Put ``apps/api`` on ``sys.path`` so the suite can seed an organization and
  user via the real ORM models (there is no public sign-up endpoint).
* Provide an HTTP client bound to the running API (``E2E_BASE_URL``).
* Skip (or fail, in CI) cleanly when the stack is not reachable.
* Flush diagnostic artifacts when a test fails.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Generator
from pathlib import Path

import pytest

# --- Path / environment bootstrap (must run before importing `api`) ----------
_REPO_ROOT = Path(__file__).resolve().parents[2]
_API_ROOT = _REPO_ROOT / "apps" / "api"
if str(_API_ROOT) not in sys.path:
    sys.path.insert(0, str(_API_ROOT))

os.environ.setdefault("SECRET_KEY", "e2e-secret-key-minimum-32-characters-long")
os.environ.setdefault(
    "DATABASE_URL_SYNC",
    "postgresql://verdin:verdin@localhost:5432/verdin_credit_test",
)

import httpx  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import Session, sessionmaker  # noqa: E402

import api.models  # noqa: F401, E402 — register all ORM mappers
from tests.e2e.fixtures.organization import (  # noqa: E402
    OrganizationRecord,
    create_organization,
    delete_organization,
)
from tests.e2e.fixtures.users import UserRecord, create_owner_user  # noqa: E402
from tests.e2e.helpers.artifacts import ArtifactCollector  # noqa: E402

ARTIFACT_DIR = Path(__file__).resolve().parent / "_artifacts"
HEALTH_PATH = "/api/v1/health"


def _base_url() -> str:
    return os.environ.get("E2E_BASE_URL", "http://localhost:8000").rstrip("/")


def _database_url_sync() -> str:
    return os.environ["DATABASE_URL_SYNC"]


@pytest.fixture(scope="session")
def base_url() -> str:
    return _base_url()


@pytest.fixture(scope="session")
def require_api(base_url: str) -> None:
    """Ensure the API is reachable.

    In CI (``E2E_REQUIRE=1``) an unreachable API is a hard failure. Locally it
    skips the suite so contributors without a running stack are not blocked.
    """
    try:
        response = httpx.get(f"{base_url}{HEALTH_PATH}", timeout=5.0)
        response.raise_for_status()
    except (httpx.HTTPError, OSError) as exc:
        message = f"API not reachable at {base_url}{HEALTH_PATH}: {exc}"
        if os.environ.get("E2E_REQUIRE"):
            pytest.fail(message)
        pytest.skip(message)


@pytest.fixture(scope="session")
def db_session_factory() -> Generator[sessionmaker[Session]]:
    engine = create_engine(_database_url_sync(), pool_pre_ping=True, future=True)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    try:
        yield factory
    finally:
        engine.dispose()


@pytest.fixture(scope="session")
def organization(
    require_api: None,
    db_session_factory: sessionmaker[Session],
) -> Generator[OrganizationRecord]:
    with db_session_factory() as session:
        org = create_organization(session)
    yield org
    with db_session_factory() as session:
        try:
            delete_organization(session, org.id)
        except Exception:  # noqa: BLE001 — teardown is best-effort
            session.rollback()


@pytest.fixture(scope="session")
def owner(
    db_session_factory: sessionmaker[Session],
    organization: OrganizationRecord,
) -> UserRecord:
    with db_session_factory() as session:
        return create_owner_user(session, organization.id)


@pytest.fixture
def http(base_url: str) -> Generator[httpx.Client]:
    with httpx.Client(base_url=base_url, timeout=30.0) as client:
        yield client


@pytest.fixture
def artifacts(request: pytest.FixtureRequest) -> Generator[ArtifactCollector]:
    collector = ArtifactCollector(request.node.name, ARTIFACT_DIR)
    request.node.stash[_ARTIFACTS_KEY] = collector
    yield collector


_ARTIFACTS_KEY = pytest.StashKey[ArtifactCollector]()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        collector = item.stash.get(_ARTIFACTS_KEY, None)
        if collector is not None:
            written = collector.dump()
            if written is not None:
                report.sections.append(
                    ("E2E artifacts", f"Diagnostic artifacts written to {written}")
                )
