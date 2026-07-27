"""Organization type + per-org demo feature flags (LRP-109 / LRP-108 depth).

Revision ID: 100_organization_type_flags
Revises: 099_partner_contacts
Create Date: 2026-07-27
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "100_organization_type_flags"
down_revision: str | None = "099_partner_contacts"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

organization_type = postgresql.ENUM(
    "demo",
    "internal",
    "partner",
    "production",
    name="organization_type",
    create_type=False,
)
org_demo_feature = postgresql.ENUM(
    "demo_data",
    "demo_notifications",
    "sample_borrowers",
    "fake_credit_reports",
    "training_mode",
    name="org_demo_feature",
    create_type=False,
)


def upgrade() -> None:
    organization_type.create(op.get_bind(), checkfirst=True)
    org_demo_feature.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "organizations",
        sa.Column(
            "organization_type",
            organization_type,
            nullable=False,
            server_default="production",
        ),
    )
    op.create_index("ix_organizations_organization_type", "organizations", ["organization_type"])

    # Known demo seed org → DEMO; leave all others PRODUCTION (safe default).
    op.execute(
        sa.text(
            "UPDATE organizations SET organization_type = 'demo' "
            "WHERE slug = 'verdin-demo' AND deleted_at IS NULL"
        )
    )

    op.create_table(
        "organization_feature_flags",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("feature", org_demo_feature, nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["updated_by_id"], ["users.id"]),
        sa.UniqueConstraint(
            "organization_id", "feature", name="uq_organization_feature_flags_org_feature"
        ),
    )
    op.create_index(
        "ix_organization_feature_flags_organization_id",
        "organization_feature_flags",
        ["organization_id"],
    )

    # Enable demo flags for the seed demo org only.
    op.execute(
        sa.text(
            """
            INSERT INTO organization_feature_flags (id, organization_id, feature, enabled)
            SELECT gen_random_uuid(), o.id, f.feature, true
            FROM organizations o
            CROSS JOIN (
                VALUES
                    ('demo_data'::org_demo_feature),
                    ('demo_notifications'::org_demo_feature),
                    ('sample_borrowers'::org_demo_feature),
                    ('training_mode'::org_demo_feature)
            ) AS f(feature)
            WHERE o.slug = 'verdin-demo' AND o.deleted_at IS NULL
            """
        )
    )


def downgrade() -> None:
    op.drop_index(
        "ix_organization_feature_flags_organization_id",
        table_name="organization_feature_flags",
    )
    op.drop_table("organization_feature_flags")
    op.drop_index("ix_organizations_organization_type", table_name="organizations")
    op.drop_column("organizations", "organization_type")
    org_demo_feature.drop(op.get_bind(), checkfirst=True)
    organization_type.drop(op.get_bind(), checkfirst=True)
