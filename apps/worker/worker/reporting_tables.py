"""Reflected reporting tables for worker materialized view refresh."""

from sqlalchemy import Column, DateTime, Integer, MetaData, Table, Text
from sqlalchemy.dialects.postgresql import UUID

metadata = MetaData()

reporting_mv_refresh_runs_table = Table(
    "reporting_mv_refresh_runs",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("organization_id", UUID(as_uuid=True)),
    Column("trigger_source", Text, nullable=False),
    Column("status", Text, nullable=False),
    Column("views_refreshed", Integer, nullable=False),
    Column("started_at", DateTime(timezone=True), nullable=False),
    Column("completed_at", DateTime(timezone=True), nullable=False),
    Column("error_message", Text),
    Column("created_at", DateTime(timezone=True)),
    Column("updated_at", DateTime(timezone=True)),
)

REPORTING_MATERIALIZED_VIEWS: tuple[str, ...] = (
    "mv_bureau_account_counts",
    "mv_bureau_sent_letter_counts",
    "mv_team_member_productivity",
)
