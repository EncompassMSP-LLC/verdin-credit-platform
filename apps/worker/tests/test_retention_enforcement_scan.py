"""Tests for retention enforcement worker job."""

from unittest.mock import MagicMock, patch
from uuid import uuid4

from worker.base import JobContext
from worker.constants import JobStatus, JobType
from worker.jobs import retention_enforcement_scan  # noqa: F401 — register job
from worker.jobs.retention_enforcement_scan import RetentionEnforcementScanJob
from worker.registry import get_job
from worker.retention_enforcement import RetentionEnforcementScanResult


def test_retention_enforcement_scan_job_registered() -> None:
    job = get_job(JobType.RETENTION_ENFORCEMENT_SCAN)
    assert isinstance(job, RetentionEnforcementScanJob)


@patch("worker.jobs.retention_enforcement_scan.run_retention_enforcement_scan")
@patch("worker.jobs.retention_enforcement_scan.session_scope")
def test_retention_enforcement_scan_job_runs_scan(
    mock_session_scope: MagicMock,
    mock_run_scan: MagicMock,
) -> None:
    session = MagicMock()
    mock_session_scope.return_value.__enter__.return_value = session
    mock_run_scan.return_value = RetentionEnforcementScanResult(
        organizations_processed=2,
        policies_processed=3,
        items_enforced=5,
    )

    job = RetentionEnforcementScanJob()
    result = job.run(JobContext(job_id="job-1", payload={}))

    mock_run_scan.assert_called_once_with(session, organization_id=None)
    assert result.status is JobStatus.COMPLETED
    assert "5 item(s)" in (result.message or "")


@patch("worker.jobs.retention_enforcement_scan.run_retention_enforcement_scan")
@patch("worker.jobs.retention_enforcement_scan.session_scope")
def test_retention_enforcement_scan_job_scoped_to_organization(
    mock_session_scope: MagicMock,
    mock_run_scan: MagicMock,
) -> None:
    org_id = uuid4()
    session = MagicMock()
    mock_session_scope.return_value.__enter__.return_value = session
    mock_run_scan.return_value = RetentionEnforcementScanResult(
        organizations_processed=1,
        policies_processed=1,
        items_enforced=0,
    )

    job = RetentionEnforcementScanJob()
    job.run(JobContext(job_id="job-2", payload={"organization_id": str(org_id)}))

    mock_run_scan.assert_called_once_with(session, organization_id=org_id)
