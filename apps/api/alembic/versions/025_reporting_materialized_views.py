"""Reporting materialized views for bureau and team metrics.

Revision ID: 025_reporting_materialized_views
Revises: 024_portal_push_notifications
Create Date: 2026-07-03
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "025_reporting_materialized_views"
down_revision: str | None = "024_portal_push_notifications"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_BUREAU_ACCOUNT_MV = "mv_bureau_account_counts"
_BUREAU_SENT_LETTERS_MV = "mv_bureau_sent_letter_counts"
_TEAM_PRODUCTIVITY_MV = "mv_team_member_productivity"


def upgrade() -> None:
    op.execute("CREATE TYPE reporting_mv_trigger_source AS ENUM ('manual', 'scheduled')")
    op.execute("CREATE TYPE reporting_mv_refresh_status AS ENUM ('completed', 'failed')")

    op.create_table(
        "reporting_mv_refresh_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "trigger_source",
            postgresql.ENUM(
                "manual",
                "scheduled",
                name="reporting_mv_trigger_source",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            postgresql.ENUM(
                "completed",
                "failed",
                name="reporting_mv_refresh_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("views_refreshed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
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
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_reporting_mv_refresh_runs_organization_id",
        "reporting_mv_refresh_runs",
        ["organization_id"],
    )
    op.create_index(
        "ix_reporting_mv_refresh_runs_started_at",
        "reporting_mv_refresh_runs",
        ["started_at"],
    )

    op.execute(
        f"""
        CREATE MATERIALIZED VIEW {_BUREAU_ACCOUNT_MV} AS
        SELECT
            a.organization_id,
            a.bureau::text AS bureau,
            a.dispute_status::text AS dispute_status,
            COUNT(*)::integer AS account_count
        FROM accounts a
        WHERE a.deleted_at IS NULL
        GROUP BY a.organization_id, a.bureau, a.dispute_status
        """
    )
    op.execute(
        f"""
        CREATE UNIQUE INDEX ux_mv_bureau_account_counts
        ON {_BUREAU_ACCOUNT_MV} (organization_id, bureau, dispute_status)
        """
    )

    op.execute(
        f"""
        CREATE MATERIALIZED VIEW {_BUREAU_SENT_LETTERS_MV} AS
        SELECT
            dl.organization_id,
            a.bureau::text AS bureau,
            COUNT(*)::integer AS sent_letter_count
        FROM dispute_letters dl
        JOIN accounts a ON a.id = dl.account_id
        WHERE dl.deleted_at IS NULL
          AND dl.status = 'sent'
          AND a.deleted_at IS NULL
        GROUP BY dl.organization_id, a.bureau
        """
    )
    op.execute(
        f"""
        CREATE UNIQUE INDEX ux_mv_bureau_sent_letter_counts
        ON {_BUREAU_SENT_LETTERS_MV} (organization_id, bureau)
        """
    )

    op.execute(
        f"""
        CREATE MATERIALIZED VIEW {_TEAM_PRODUCTIVITY_MV} AS
        SELECT
            u.organization_id,
            u.id AS user_id,
            COALESCE(ot.open_tasks, 0)::integer AS open_tasks,
            COALESCE(ct.completed_tasks_30d, 0)::integer AS completed_tasks_30d,
            COALESCE(oc.assigned_open_cases, 0)::integer AS assigned_open_cases,
            COALESCE(cc.closed_cases_30d, 0)::integer AS closed_cases_30d
        FROM users u
        LEFT JOIN (
            SELECT
                organization_id,
                assigned_user_id AS user_id,
                COUNT(*)::integer AS open_tasks
            FROM tasks
            WHERE deleted_at IS NULL
              AND assigned_user_id IS NOT NULL
              AND status IN ('open', 'in_progress', 'blocked')
            GROUP BY organization_id, assigned_user_id
        ) ot ON ot.organization_id = u.organization_id AND ot.user_id = u.id
        LEFT JOIN (
            SELECT
                organization_id,
                completed_by_id AS user_id,
                COUNT(*)::integer AS completed_tasks_30d
            FROM tasks
            WHERE deleted_at IS NULL
              AND completed_by_id IS NOT NULL
              AND status = 'completed'
              AND completed_at IS NOT NULL
              AND completed_at >= NOW() - INTERVAL '30 days'
            GROUP BY organization_id, completed_by_id
        ) ct ON ct.organization_id = u.organization_id AND ct.user_id = u.id
        LEFT JOIN (
            SELECT
                organization_id,
                assigned_to_id AS user_id,
                COUNT(*)::integer AS assigned_open_cases
            FROM cases
            WHERE deleted_at IS NULL
              AND assigned_to_id IS NOT NULL
              AND status NOT IN ('closed', 'resolved')
            GROUP BY organization_id, assigned_to_id
        ) oc ON oc.organization_id = u.organization_id AND oc.user_id = u.id
        LEFT JOIN (
            SELECT
                organization_id,
                assigned_to_id AS user_id,
                COUNT(*)::integer AS closed_cases_30d
            FROM cases
            WHERE deleted_at IS NULL
              AND assigned_to_id IS NOT NULL
              AND status IN ('closed', 'resolved')
              AND closed_at IS NOT NULL
              AND closed_at >= NOW() - INTERVAL '30 days'
            GROUP BY organization_id, assigned_to_id
        ) cc ON cc.organization_id = u.organization_id AND cc.user_id = u.id
        WHERE u.deleted_at IS NULL
          AND u.is_active = TRUE
          AND u.organization_id IS NOT NULL
        """
    )
    op.execute(
        f"""
        CREATE UNIQUE INDEX ux_mv_team_member_productivity
        ON {_TEAM_PRODUCTIVITY_MV} (organization_id, user_id)
        """
    )

    for view_name in (
        _BUREAU_ACCOUNT_MV,
        _BUREAU_SENT_LETTERS_MV,
        _TEAM_PRODUCTIVITY_MV,
    ):
        op.execute(f"REFRESH MATERIALIZED VIEW {view_name}")


def downgrade() -> None:
    op.execute(f"DROP MATERIALIZED VIEW IF EXISTS {_TEAM_PRODUCTIVITY_MV}")
    op.execute(f"DROP MATERIALIZED VIEW IF EXISTS {_BUREAU_SENT_LETTERS_MV}")
    op.execute(f"DROP MATERIALIZED VIEW IF EXISTS {_BUREAU_ACCOUNT_MV}")
    op.drop_index(
        "ix_reporting_mv_refresh_runs_started_at",
        table_name="reporting_mv_refresh_runs",
    )
    op.drop_index(
        "ix_reporting_mv_refresh_runs_organization_id",
        table_name="reporting_mv_refresh_runs",
    )
    op.drop_table("reporting_mv_refresh_runs")
    op.execute("DROP TYPE reporting_mv_refresh_status")
    op.execute("DROP TYPE reporting_mv_trigger_source")
