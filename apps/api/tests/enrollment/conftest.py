"""Fixtures for client enrollment tests."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

import api.models  # noqa: F401
from api.modules.auth.models import Organization


@pytest.fixture
async def test_org(db_session: AsyncSession) -> Organization:
    org = Organization(
        id=uuid.uuid4(),
        name="Ultimate Credit Repair LLC",
        slug="verdin-demo",
        is_active=True,
    )
    db_session.add(org)
    await db_session.commit()
    return org
