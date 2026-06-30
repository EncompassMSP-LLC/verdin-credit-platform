"""Credit account intelligence engine — Sprint 2 Epic 2.

Revision ID: 003_credit_accounts
Revises: 002_expand_cases
Create Date: 2026-06-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "003_credit_accounts"
down_revision: str | None = "002_expand_cases"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint("cases_account_id_fkey", "cases", type_="foreignkey")
    op.drop_column("cases", "account_id")
    op.drop_index("ix_accounts_account_number", table_name="accounts")
    op.drop_table("accounts")

    op.execute(
        "CREATE TYPE account_bureau AS ENUM ("
        "'equifax', 'experian', 'transunion', 'innovis', 'unknown'"
        ")"
    )
    op.execute(
        "CREATE TYPE tradeline_account_type AS ENUM ("
        "'mortgage', 'auto', 'credit_card', 'collection', 'personal_loan', "
        "'student_loan', 'medical', 'utility', 'telecom', 'other'"
        ")"
    )
    op.execute(
        "CREATE TYPE tradeline_account_status AS ENUM ("
        "'open', 'closed', 'collection', 'charge_off', 'repossession', "
        "'foreclosure', 'transferred', 'paid', 'settled', 'deleted', 'unknown'"
        ")"
    )
    op.execute(
        "CREATE TYPE tradeline_payment_status AS ENUM ("
        "'current', 'late_30', 'late_60', 'late_90', 'late_120', "
        "'charge_off', 'collection', 'repossession', 'foreclosure', 'unknown'"
        ")"
    )
    op.execute(
        "CREATE TYPE tradeline_dispute_status AS ENUM ("
        "'not_started', 'evidence_needed', 'ready_for_dispute', 'dispute_sent', "
        "'awaiting_response', 'verified', 'corrected', 'deleted', 'escalated', "
        "'monitoring'"
        ")"
    )
    op.execute(
        "CREATE TYPE tradeline_investigation_status AS ENUM ("
        "'none', 'pending', 'completed', 'overdue', 'escalated'"
        ")"
    )

    op.create_table(
        "accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "bureau",
            postgresql.ENUM(
                "equifax",
                "experian",
                "transunion",
                "innovis",
                "unknown",
                name="account_bureau",
                create_type=False,
            ),
            nullable=False,
            server_default="unknown",
        ),
        sa.Column("creditor_name", sa.String(255), nullable=False),
        sa.Column("original_creditor", sa.String(255), nullable=True),
        sa.Column("account_number_masked", sa.String(50), nullable=True),
        sa.Column(
            "account_type",
            postgresql.ENUM(
                "mortgage",
                "auto",
                "credit_card",
                "collection",
                "personal_loan",
                "student_loan",
                "medical",
                "utility",
                "telecom",
                "other",
                name="tradeline_account_type",
                create_type=False,
            ),
            nullable=False,
            server_default="other",
        ),
        sa.Column(
            "account_status",
            postgresql.ENUM(
                "open",
                "closed",
                "collection",
                "charge_off",
                "repossession",
                "foreclosure",
                "transferred",
                "paid",
                "settled",
                "deleted",
                "unknown",
                name="tradeline_account_status",
                create_type=False,
            ),
            nullable=False,
            server_default="unknown",
        ),
        sa.Column(
            "payment_status",
            postgresql.ENUM(
                "current",
                "late_30",
                "late_60",
                "late_90",
                "late_120",
                "charge_off",
                "collection",
                "repossession",
                "foreclosure",
                "unknown",
                name="tradeline_payment_status",
                create_type=False,
            ),
            nullable=False,
            server_default="unknown",
        ),
        sa.Column("balance", sa.Numeric(12, 2), nullable=True),
        sa.Column("high_balance", sa.Numeric(12, 2), nullable=True),
        sa.Column("credit_limit", sa.Numeric(12, 2), nullable=True),
        sa.Column("monthly_payment", sa.Numeric(12, 2), nullable=True),
        sa.Column("past_due_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("date_opened", sa.Date(), nullable=True),
        sa.Column("date_reported", sa.Date(), nullable=True),
        sa.Column("date_last_activity", sa.Date(), nullable=True),
        sa.Column("date_first_delinquency", sa.Date(), nullable=True),
        sa.Column("estimated_removal_date", sa.Date(), nullable=True),
        sa.Column("responsibility", sa.String(50), nullable=True),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column(
            "dispute_status",
            postgresql.ENUM(
                "not_started",
                "evidence_needed",
                "ready_for_dispute",
                "dispute_sent",
                "awaiting_response",
                "verified",
                "corrected",
                "deleted",
                "escalated",
                "monitoring",
                name="tradeline_dispute_status",
                create_type=False,
            ),
            nullable=False,
            server_default="not_started",
        ),
        sa.Column("dispute_round", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "investigation_status",
            postgresql.ENUM(
                "none",
                "pending",
                "completed",
                "overdue",
                "escalated",
                name="tradeline_investigation_status",
                create_type=False,
            ),
            nullable=False,
            server_default="none",
        ),
        sa.Column("last_dispute_date", sa.Date(), nullable=True),
        sa.Column("next_eligible_dispute_date", sa.Date(), nullable=True),
        sa.Column("response_received", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("cra_dispute", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("furnisher_dispute", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("cfpb_dispute", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("ai_summary", sa.Text(), nullable=True),
        sa.Column("ai_recommended_next_action", sa.Text(), nullable=True),
        sa.Column("risk_score", sa.Integer(), nullable=True),
        sa.Column("readiness_score", sa.Integer(), nullable=True),
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
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_accounts_case_id", "accounts", ["case_id"])
    op.create_index("ix_accounts_bureau", "accounts", ["bureau"])
    op.create_index("ix_accounts_account_type", "accounts", ["account_type"])
    op.create_index("ix_accounts_account_status", "accounts", ["account_status"])
    op.create_index("ix_accounts_dispute_status", "accounts", ["dispute_status"])
    op.create_index("ix_accounts_risk_score", "accounts", ["risk_score"])
    op.create_index("ix_accounts_readiness_score", "accounts", ["readiness_score"])


def downgrade() -> None:
    op.drop_index("ix_accounts_readiness_score", table_name="accounts")
    op.drop_index("ix_accounts_risk_score", table_name="accounts")
    op.drop_index("ix_accounts_dispute_status", table_name="accounts")
    op.drop_index("ix_accounts_account_status", table_name="accounts")
    op.drop_index("ix_accounts_account_type", table_name="accounts")
    op.drop_index("ix_accounts_bureau", table_name="accounts")
    op.drop_index("ix_accounts_case_id", table_name="accounts")
    op.drop_table("accounts")

    op.execute("DROP TYPE tradeline_investigation_status")
    op.execute("DROP TYPE tradeline_dispute_status")
    op.execute("DROP TYPE tradeline_payment_status")
    op.execute("DROP TYPE tradeline_account_status")
    op.execute("DROP TYPE tradeline_account_type")
    op.execute("DROP TYPE account_bureau")

    op.create_table(
        "accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("account_number", sa.String(100), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
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
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_accounts_account_number", "accounts", ["account_number"])
    op.add_column(
        "cases",
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "cases_account_id_fkey",
        "cases",
        "accounts",
        ["account_id"],
        ["id"],
    )
