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
from sqlalchemy import text  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool  # noqa: E402

import api.models  # noqa: F401, E402 — register all ORM mappers
from api.core.config import get_settings  # noqa: E402
from api.database.base import Base  # noqa: E402
from api.database.session import get_db  # noqa: E402
from main import app  # noqa: E402

# A single ``NullPool`` engine for the whole test session. NullPool never reuses
# a connection, so every checkout opens a brand-new asyncpg connection bound to
# whichever event loop is currently running. This is essential because the sync
# ``TestClient`` runs the ASGI app in its own portal event loop, while the
# pytest-asyncio fixtures run in a separate loop — a pooled connection would be
# shared across loops and raise "attached to a different loop" / "Event loop is
# closed". Creating the engine object here does not open any connection.
_test_engine = create_async_engine(get_settings().database_url, poolclass=NullPool)
TestSessionLocal = async_sessionmaker(
    _test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def _truncate_all_tables() -> None:
    table_names = ", ".join(f'"{table.name}"' for table in Base.metadata.sorted_tables)
    if not table_names:
        return
    async with _test_engine.begin() as conn:
        await conn.execute(text(f"TRUNCATE TABLE {table_names} RESTART IDENTITY CASCADE"))


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession]:
    """Yield a session used by fixtures to seed data.

    Seed fixtures must ``commit`` (not just ``flush``) so the committed rows are
    visible to the request-scoped sessions the app opens on its own event loop.
    On teardown every table is truncated so each test starts from a clean state
    instead of relying on transactional rollback (which cannot span the two event
    loops involved). Only tests that touch the database depend on this fixture,
    so database-free tests never open a connection.
    """
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await _truncate_all_tables()


@pytest.fixture
def api_client(db_session: AsyncSession) -> Generator[TestClient]:
    """Provide a ``TestClient`` backed by request-scoped database sessions.

    Each request opens its own session on the TestClient's event loop and commits
    on success, mirroring the production ``get_db`` dependency. Sessions are never
    shared across event loops, which avoids asyncpg's cross-loop errors.
    """

    async def override_get_db() -> AsyncGenerator[AsyncSession]:
        async with TestSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.pop(get_db, None)
