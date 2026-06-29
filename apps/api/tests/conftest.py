"""Shared pytest configuration and fixtures.

Environment variables are configured before any ``api`` import so that
``pydantic-settings`` reads the test database during module import.
"""

import os

os.environ.setdefault("SECRET_KEY", "test-secret-key-minimum-32-characters-long")
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://verdin:verdin@localhost:5432/verdin_credit_test",
)
os.environ.setdefault(
    "DATABASE_URL_SYNC",
    "postgresql://verdin:verdin@localhost:5432/verdin_credit_test",
)

from collections.abc import AsyncGenerator, Generator  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool  # noqa: E402

import api.models  # noqa: F401, E402 — register all ORM mappers
from api.core.config import get_settings  # noqa: E402
from api.database.session import get_db  # noqa: E402
from main import app  # noqa: E402


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession]:
    """Yield an isolated async session backed by a per-test ``NullPool`` engine.

    pytest-asyncio (``asyncio_mode = "auto"``) creates a fresh event loop for
    each test. A pooled asyncpg connection created in one test's loop would be
    reused in a later test whose loop is already closed, raising
    ``RuntimeError: Event loop is closed``. Building a ``NullPool`` engine inside
    the fixture guarantees every test gets brand-new connections on the current
    running loop and disposes them in teardown, so no connection ever crosses an
    event loop boundary.
    """
    engine = create_async_engine(get_settings().database_url, poolclass=NullPool)
    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
    session = session_factory()
    try:
        yield session
        await session.rollback()
    finally:
        await session.close()
        await engine.dispose()


@pytest.fixture
def api_client(db_session: AsyncSession) -> Generator[TestClient]:
    """Provide a ``TestClient`` whose requests share the test's async session."""

    async def override_get_db() -> AsyncGenerator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.pop(get_db, None)
