"""Organization bootstrap.

There is no public organization-creation endpoint (organizations are
provisioned out-of-band), so the E2E suite seeds a dedicated, isolated
organization directly in the database before exercising the HTTP API. Using a
unique slug per run keeps parallel/repeat runs from colliding and scopes every
dashboard metric to this test's data only.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session

from api.modules.auth.models import Organization


@dataclass(slots=True)
class OrganizationRecord:
    id: uuid.UUID
    name: str
    slug: str


def create_organization(session: Session) -> OrganizationRecord:
    suffix = uuid.uuid4().hex[:8]
    org = Organization(
        id=uuid.uuid4(),
        name=f"E2E Lifecycle Org {suffix}",
        slug=f"e2e-lifecycle-{suffix}",
        is_active=True,
    )
    session.add(org)
    session.commit()
    return OrganizationRecord(id=org.id, name=org.name, slug=org.slug)


def delete_organization(session: Session, organization_id: uuid.UUID) -> None:
    """Best-effort teardown of all rows created under the test organization."""
    org = session.get(Organization, organization_id)
    if org is not None:
        session.delete(org)
        session.commit()
