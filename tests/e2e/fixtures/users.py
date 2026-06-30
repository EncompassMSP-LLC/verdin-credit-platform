"""User bootstrap for the E2E organization.

Seeds an Owner user (full RBAC) directly in the database so the suite can
authenticate over HTTP and exercise every write path in the workflow.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session

from api.core.constants import UserRole
from api.core.security import hash_password
from api.modules.auth.models import User

DEFAULT_PASSWORD = "E2ePassw0rd!"


@dataclass(slots=True)
class UserRecord:
    id: uuid.UUID
    email: str
    password: str
    role: str


def create_owner_user(
    session: Session,
    organization_id: uuid.UUID,
    *,
    password: str = DEFAULT_PASSWORD,
) -> UserRecord:
    # Use a non-reserved domain: EmailStr (email-validator) rejects special-use
    # TLDs such as .test / .example / .invalid / .localhost.
    suffix = uuid.uuid4().hex[:8]
    email = f"e2e-owner-{suffix}@verdin-e2e.com"
    user = User(
        id=uuid.uuid4(),
        email=email,
        hashed_password=hash_password(password),
        first_name="E2E",
        last_name="Owner",
        role=UserRole.OWNER,
        organization_id=organization_id,
        is_active=True,
    )
    session.add(user)
    session.commit()
    return UserRecord(
        id=user.id, email=email, password=password, role=UserRole.OWNER.value
    )
