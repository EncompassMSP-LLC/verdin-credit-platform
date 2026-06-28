"""Database seed script for development."""

import asyncio
import uuid

from sqlalchemy import select

from api.auth.security import hash_password
from api.database.session import AsyncSessionLocal
from api.models import (
    Account,
    Case,
    CaseStatus,
    Organization,
    Task,
    TaskPriority,
    TaskStatus,
    User,
    UserRole,
)


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Organization).where(Organization.slug == "verdin-demo"))
        if result.scalar_one_or_none() is not None:
            print("Seed data already exists, skipping.")
            return

        org = Organization(
            id=uuid.uuid4(),
            name="Verdin Demo Organization",
            slug="verdin-demo",
            is_active=True,
        )
        session.add(org)
        await session.flush()

        owner = User(
            id=uuid.uuid4(),
            email="owner@verdin.demo",
            hashed_password=hash_password("changeme123"),
            first_name="Demo",
            last_name="Owner",
            role=UserRole.OWNER,
            organization_id=org.id,
            is_active=True,
        )
        admin = User(
            id=uuid.uuid4(),
            email="admin@verdin.demo",
            hashed_password=hash_password("changeme123"),
            first_name="Demo",
            last_name="Admin",
            role=UserRole.ADMIN,
            organization_id=org.id,
            is_active=True,
        )
        session.add_all([owner, admin])
        await session.flush()

        account = Account(
            id=uuid.uuid4(),
            name="Acme Corporation",
            account_number="ACC-001",
            email="contact@acme.example",
            organization_id=org.id,
            created_by_id=owner.id,
        )
        session.add(account)
        await session.flush()

        case = Case(
            id=uuid.uuid4(),
            title="Credit Review - Acme Corporation",
            description="Initial credit review for new account onboarding.",
            status=CaseStatus.OPEN,
            case_number="CASE-2026-001",
            organization_id=org.id,
            account_id=account.id,
            assigned_to_id=admin.id,
            created_by_id=owner.id,
        )
        session.add(case)
        await session.flush()

        task = Task(
            id=uuid.uuid4(),
            title="Review financial statements",
            description="Collect and review last 3 years of financial statements.",
            status=TaskStatus.PENDING,
            priority=TaskPriority.HIGH,
            case_id=case.id,
            assigned_to_id=admin.id,
            created_by_id=owner.id,
        )
        session.add(task)

        await session.commit()
        print("Seed data created successfully.")
        print(f"  Organization: {org.name} ({org.slug})")
        print("  Owner login:  owner@verdin.demo / changeme123")
        print("  Admin login:  admin@verdin.demo / changeme123")


if __name__ == "__main__":
    asyncio.run(seed())
