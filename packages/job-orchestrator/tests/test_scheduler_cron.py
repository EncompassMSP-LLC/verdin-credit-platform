"""Scheduler cron evaluation tests."""

from datetime import UTC, datetime

from verdin_job_orchestrator import JobScheduler, JobType, ScheduledJob


def test_jobs_due_at_matches_cron_minute() -> None:
    scheduler = JobScheduler()
    scheduler.register(
        ScheduledJob(
            job_type=JobType.OVERDUE_INVESTIGATION_SCAN,
            cron_expression="0 6 * * *",
        ),
    )

    due = scheduler.jobs_due_at(datetime(2026, 7, 2, 6, 0, tzinfo=UTC))
    assert len(due) == 1
    assert due[0].job_type is JobType.OVERDUE_INVESTIGATION_SCAN

    not_due = scheduler.jobs_due_at(datetime(2026, 7, 2, 7, 0, tzinfo=UTC))
    assert not_due == []


def test_mark_triggered_prevents_duplicate_enqueue_same_minute() -> None:
    scheduler = JobScheduler()
    scheduler.register(
        ScheduledJob(
            job_type=JobType.OVERDUE_INVESTIGATION_SCAN,
            cron_expression="0 6 * * *",
        ),
    )
    at = datetime(2026, 7, 2, 6, 0, tzinfo=UTC)

    assert len(scheduler.jobs_due_at(at)) == 1
    scheduler.mark_triggered(JobType.OVERDUE_INVESTIGATION_SCAN, at)
    assert scheduler.jobs_due_at(at) == []
