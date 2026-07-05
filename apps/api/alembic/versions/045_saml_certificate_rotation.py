"""Admin-gated SAML certificate rotation audit table.

Revision ID: 045_saml_certificate_rotation
Revises: 044_agent_external_tool_calling
Create Date: 2026-07-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "045_saml_certificate_rotation"
down_revision: str | None = "044_agent_external_tool_calling"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE saml_certificate_rotation_status AS ENUM "
        "('pending_approval', 'rotated', 'rejected', 'failed')"
    )

    op.create_table(
        "saml_certificate_rotation_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("metadata_upload_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_id", sa.String(length=500), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending_approval",
                "rotated",
                "rejected",
                "failed",
                name="saml_certificate_rotation_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("rotation_summary", sa.Text(), nullable=False),
        sa.Column("requested_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rotated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(
            ["metadata_upload_id"],
            ["saml_federation_metadata_uploads.id"],
        ),
        sa.ForeignKeyConstraint(["requested_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["approved_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_saml_certificate_rotation_runs_org_requested",
        "saml_certificate_rotation_runs",
        ["organization_id", "requested_at"],
    )
    op.create_index(
        "ix_saml_certificate_rotation_runs_metadata_upload",
        "saml_certificate_rotation_runs",
        ["metadata_upload_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_saml_certificate_rotation_runs_metadata_upload",
        table_name="saml_certificate_rotation_runs",
    )
    op.drop_index(
        "ix_saml_certificate_rotation_runs_org_requested",
        table_name="saml_certificate_rotation_runs",
    )
    op.drop_table("saml_certificate_rotation_runs")
    op.execute("DROP TYPE saml_certificate_rotation_status")
