"""Worker pipeline routing for credit report parsing."""

from unittest.mock import MagicMock, patch
from uuid import uuid4

from worker.constants import JobType
from worker.jobs.classify import DocumentClassifyJob
from worker.base import JobContext


@patch("worker.jobs.classify.enqueue_job")
@patch("worker.jobs.classify.session_scope")
@patch("worker.jobs.classify.classify_document")
def test_classify_credit_report_enqueues_parse_job(
    mock_classify_document,
    mock_session_scope,
    mock_enqueue_job,
) -> None:
    document_id = uuid4()
    mock_session = MagicMock()
    mock_session_scope.return_value.__enter__.return_value = mock_session

    mock_classify_document.return_value = MagicMock(
        document_type=MagicMock(value="credit_report"),
        confidence_score=0.95,
        classification_method=MagicMock(value="rules"),
    )

    with (
        patch(
            "worker.jobs.classify.get_document_for_classification",
            return_value=MagicMock(
                ocr_text="Experian report",
                file_name="report.pdf",
                title="Report",
                mime_type="application/pdf",
                deleted_at=None,
            ),
        ),
        patch("worker.jobs.classify.save_classification"),
        patch("worker.jobs.classify.get_document_timeline_context", return_value=None),
    ):
        result = DocumentClassifyJob().run(
            JobContext(job_id="job-1", payload={"document_id": str(document_id)})
        )

    assert result.status.value == "completed"
    mock_enqueue_job.assert_called_once_with(
        JobType.DOCUMENT_CREDIT_REPORT_PARSE,
        {"document_id": str(document_id)},
    )


@patch("worker.jobs.classify.enqueue_job")
@patch("worker.jobs.classify.session_scope")
@patch("worker.jobs.classify.classify_document")
def test_classify_non_credit_report_enqueues_metadata_job(
    mock_classify_document,
    mock_session_scope,
    mock_enqueue_job,
) -> None:
    document_id = uuid4()
    mock_session = MagicMock()
    mock_session_scope.return_value.__enter__.return_value = mock_session

    mock_classify_document.return_value = MagicMock(
        document_type=MagicMock(value="bank_statement"),
        confidence_score=0.8,
        classification_method=MagicMock(value="rules"),
    )

    with (
        patch(
            "worker.jobs.classify.get_document_for_classification",
            return_value=MagicMock(
                ocr_text="Statement",
                file_name="statement.pdf",
                title="Statement",
                mime_type="application/pdf",
                deleted_at=None,
            ),
        ),
        patch("worker.jobs.classify.save_classification"),
        patch("worker.jobs.classify.get_document_timeline_context", return_value=None),
    ):
        DocumentClassifyJob().run(
            JobContext(job_id="job-2", payload={"document_id": str(document_id)})
        )

    mock_enqueue_job.assert_called_once_with(
        JobType.DOCUMENT_METADATA_EXTRACT,
        {"document_id": str(document_id)},
    )
