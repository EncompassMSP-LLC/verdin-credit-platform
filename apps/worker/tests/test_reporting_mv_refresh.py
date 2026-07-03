"""Worker reporting materialized view refresh tests."""

from unittest.mock import patch

from worker.jobs import reporting_mv_refresh  # noqa: F401 — register job
from worker.jobs.reporting_mv_refresh import ReportingMvRefreshJob
from worker.registry import get_job
from worker.constants import JobType
from worker.reporting_mv_refresh import ReportingMvRefreshResult


def test_reporting_mv_refresh_job_registered() -> None:
    job = get_job(JobType.REPORTING_MV_REFRESH)
    assert isinstance(job, ReportingMvRefreshJob)


@patch("worker.jobs.reporting_mv_refresh.run_reporting_mv_refresh")
@patch("worker.jobs.reporting_mv_refresh.session_scope")
def test_reporting_mv_refresh_job_runs_refresh(
    mock_session_scope,
    mock_run_refresh,
) -> None:
    mock_session_scope.return_value.__enter__.return_value = object()
    mock_run_refresh.return_value = ReportingMvRefreshResult(
        views_refreshed=3,
        status="completed",
    )

    job = ReportingMvRefreshJob()
    result = job.run(type("Ctx", (), {"job_id": "job-1", "payload": {}})())

    assert result.status.value == "completed"
    mock_run_refresh.assert_called_once()
