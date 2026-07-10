"""Database seed script for development."""

import asyncio
import uuid
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select

import api.models  # noqa: F401 — register all ORM mappers
from api.core.audit import apply_audit_on_create
from api.core.constants import UserRole
from api.core.security import hash_password
from api.database.session import AsyncSessionLocal
from api.modules.accounts.intelligence import apply_account_intelligence
from api.modules.accounts.models import (
    Account,
    AccountBureau,
    AccountStatus,
    AccountType,
    PaymentStatus,
)
from api.modules.auth.models import Organization, User
from api.modules.billing.models import OrganizationBillingAccount, SubscriptionStatus
from api.modules.cases.models import Case, CasePriority, CaseStage, CaseStatus
from api.modules.tasks.models import Task, TaskPriority, TaskStatus


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Organization).where(Organization.slug == "verdin-demo")
        )
        if result.scalar_one_or_none() is not None:
            print("Seed data already exists, skipping.")
            return

        org = Organization(
            id=uuid.uuid4(),
            name="Ultimate Credit Repair LLC",
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
        case_manager = User(
            id=uuid.uuid4(),
            email="manager@verdin.demo",
            hashed_password=hash_password("changeme123"),
            first_name="Demo",
            last_name="Manager",
            role=UserRole.CASE_MANAGER,
            organization_id=org.id,
            is_active=True,
        )
        session.add_all([owner, admin, case_manager])
        await session.flush()

        now = datetime.now(UTC)
        case = Case(
            id=uuid.uuid4(),
            title="Credit Review - Acme Corporation",
            client_name="Acme Corporation",
            client_email="contact@acme.example",
            summary="Initial credit review for new account onboarding.",
            status=CaseStatus.OPEN,
            stage=CaseStage.INTAKE,
            priority=CasePriority.HIGH,
            case_number="CASE-2026-001",
            organization_id=org.id,
            assigned_to_id=case_manager.id,
            opened_at=now,
        )
        apply_audit_on_create(case, owner.id)
        session.add(case)
        await session.flush()

        account = Account(
            id=uuid.uuid4(),
            organization_id=org.id,
            case_id=case.id,
            bureau=AccountBureau.EQUIFAX,
            creditor_name="Example National Bank",
            original_creditor="Example National Bank",
            account_number_masked="****4521",
            account_type=AccountType.CREDIT_CARD,
            account_status=AccountStatus.OPEN,
            payment_status=PaymentStatus.LATE_60,
            balance=Decimal("2450.00"),
            past_due_amount=Decimal("420.00"),
            date_opened=date(2019, 3, 15),
            date_reported=date(2026, 5, 1),
        )
        apply_account_intelligence(account)
        apply_audit_on_create(account, owner.id)
        session.add(account)

        task = Task(
            id=uuid.uuid4(),
            organization_id=org.id,
            title="Review financial statements",
            description="Collect and review last 3 years of financial statements.",
            status=TaskStatus.OPEN,
            priority=TaskPriority.HIGH,
            case_id=case.id,
            assigned_user_id=admin.id,
        )
        apply_audit_on_create(task, owner.id)
        session.add(task)

        session.add(
            OrganizationBillingAccount(
                organization_id=org.id,
                stripe_customer_id=f"cus_pilot_{uuid.uuid4().hex[:12]}",
                stripe_subscription_id=f"sub_pilot_{uuid.uuid4().hex[:12]}",
                subscription_status=SubscriptionStatus.ACTIVE,
                price_id="price_pilot_demo_monthly",
                current_period_end=datetime.now(UTC) + timedelta(days=25),
            )
        )

        await session.commit()
        print("Seed data created successfully.")
        print(f"  Organization: {org.name} ({org.slug})")
        print("  Owner login:         owner@verdin.demo / changeme123")
        print("  Admin login:         admin@verdin.demo / changeme123")
        print("  Case manager login:  manager@verdin.demo / changeme123")


if __name__ == "__main__":
    asyncio.run(seed())
