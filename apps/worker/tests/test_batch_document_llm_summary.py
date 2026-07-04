"""Worker batch document LLM summary tests."""

from unittest.mock import patch
from uuid import uuid4

from worker.batch_document_llm_summary import (
    BatchDocumentLlmSummaryResult,
    STATUS_COMPLETED,
)
from worker.jobs import batch_document_llm_summary  # noqa: F401 — register job
from worker.jobs.batch_document_llm_summary import BatchDocumentLlmSummaryJob
from worker.constants import JobType
from worker.registry import get_job


def test_batch_document_llm_summary_job_registered() -> None:
    job = get_job(JobType.BATCH_DOCUMENT_LLM_SUMMARY)
    assert isinstance(job, BatchDocumentLlmSummaryJob)


@patch("worker.jobs.batch_document_llm_summary.run_batch_document_llm_summary")
@patch("worker.jobs.batch_document_llm_summary.session_scope")
def test_batch_document_llm_summary_job_runs_processor(
    mock_session_scope,
    mock_run_batch,
) -> None:
    mock_session_scope.return_value.__enter__.return_value = object()
    mock_run_batch.return_value = BatchDocumentLlmSummaryResult(
        run_id=uuid4(),
        documents_succeeded=2,
        documents_failed=0,
        status=STATUS_COMPLETED,
    )

    job = BatchDocumentLlmSummaryJob()
    result = job.run(
        type(
            "Ctx",
            (),
            {
                "job_id": "job-1",
                "payload": {
                    "run_id": str(uuid4()),
                    "organization_id": str(uuid4()),
                    "document_ids": [str(uuid4())],
                    "performed_by_user_id": str(uuid4()),
                },
            },
        )()
    )

    assert result.status.value == "completed"
    mock_run_batch.assert_called_once()
