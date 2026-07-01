"""Tests for overdue CRA investigation worker scan."""

from datetime import date, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

from worker.base import JobContext
from worker.constants import JobStatus, JobType
from worker.jobs.overdue_investigation_scan import OverdueInvestigationScanJob
from worker.overdue_investigations import (
    INVESTIGATION_STATUS_OVERDUE,
    INVESTIGATION_STATUS_PENDING,
    scan_and_escalate_overdue_investigations,
)


def test_overdue_investigation_scan_job_registered() -> None:
    from worker.registry import get_job

    job = get_job(JobType.OVERDUE_INVESTIGATION_SCAN)
    assert isinstance(job, OverdueInvestigationScanJob)


@patch(
    "worker.jobs.overdue_investigation_scan.scan_and_escalate_overdue_investigations"
)
@patch("worker.jobs.overdue_investigation_scan.session_scope")
def test_overdue_investigation_scan_job_runs_scan(
    mock_session_scope,
    mock_scan,
) -> None:
    mock_session = MagicMock()
    mock_session_scope.return_value.__enter__.return_value = mock_session
    mock_scan.return_value = SimpleNamespace(scanned=2, escalated=1, tasks_created=1)

    result = OverdueInvestigationScanJob().run(JobContext(job_id="job-1", payload={}))

    assert result.status == JobStatus.COMPLETED
    assert "Scanned 2 account(s)" in result.message
    mock_scan.assert_called_once_with(mock_session)


@patch(
    "worker.overdue_investigations.create_overdue_investigation_task", return_value=True
)
def test_scan_escalates_pending_account(mock_create_task) -> None:
    account_id = uuid4()
    account = {
        "id": account_id,
        "organization_id": uuid4(),
        "case_id": uuid4(),
        "creditor_name": "Example Bank",
        "dispute_status": "awaiting_response",
        "investigation_status": INVESTIGATION_STATUS_PENDING,
        "last_dispute_date": date.today() - timedelta(days=31),
    }
    session = MagicMock()
    session.execute.return_value.mappings.return_value.all.return_value = [account]

    with patch(
        "worker.overdue_investigations.list_eligible_accounts",
        return_value=[account],
    ):
        result = scan_and_escalate_overdue_investigations(session)

    assert result.scanned == 1
    assert result.escalated == 1
    assert result.tasks_created == 1
    mock_create_task.assert_called_once()
    assert session.execute.called


@patch(
    "worker.overdue_investigations.create_overdue_investigation_task",
    return_value=False,
)
def test_scan_idempotent_for_already_overdue(mock_create_task) -> None:
    account = {
        "id": uuid4(),
        "organization_id": uuid4(),
        "case_id": uuid4(),
        "creditor_name": "Example Bank",
        "dispute_status": "awaiting_response",
        "investigation_status": INVESTIGATION_STATUS_OVERDUE,
        "last_dispute_date": date.today() - timedelta(days=31),
    }
    session = MagicMock()

    with patch(
        "worker.overdue_investigations.list_eligible_accounts",
        return_value=[account],
    ):
        result = scan_and_escalate_overdue_investigations(session)

    assert result.scanned == 1
    assert result.escalated == 0
    assert result.tasks_created == 0
    mock_create_task.assert_called_once()
