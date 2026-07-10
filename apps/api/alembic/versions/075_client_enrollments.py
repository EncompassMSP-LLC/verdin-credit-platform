"""Client self-enrollment audit table.

Revision ID: 075_client_enrollments
Revises: 074_client_mailing_address
Create Date: 2026-07-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "075_client_enrollments"
down_revision: str | None = "074_client_mailing_address"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE client_enrollment_status AS ENUM "
        "('pending_payment', 'completed', 'failed', 'cancelled')"
    )
    op.create_table(
        "client_enrollments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending_payment",
                "completed",
                "failed",
                "cancelled",
                name="client_enrollment_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("mailing_address_line1", sa.String(length=255), nullable=False),
        sa.Column("mailing_address_line2", sa.String(length=255), nullable=True),
        sa.Column("mailing_city", sa.String(length=100), nullable=False),
        sa.Column("mailing_state", sa.String(length=50), nullable=False),
        sa.Column("mailing_postal_code", sa.String(length=20), nullable=False),
        sa.Column("stripe_checkout_session_id", sa.String(length=255), nullable=True),
        sa.Column("stripe_payment_status", sa.String(length=50), nullable=True),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("portal_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"]),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["portal_user_id"], ["client_portal_users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stripe_checkout_session_id"),
    )
    op.create_index(
        "ix_client_enrollments_organization_id", "client_enrollments", ["organization_id"]
    )
    op.create_index("ix_client_enrollments_status", "client_enrollments", ["status"])
    op.create_index("ix_client_enrollments_email", "client_enrollments", ["email"])


def downgrade() -> None:
    op.drop_index("ix_client_enrollments_email", table_name="client_enrollments")
    op.drop_index("ix_client_enrollments_status", table_name="client_enrollments")
    op.drop_index("ix_client_enrollments_organization_id", table_name="client_enrollments")
    op.drop_table("client_enrollments")
    op.execute("DROP TYPE client_enrollment_status")
