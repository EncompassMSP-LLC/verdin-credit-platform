"""Worker pipeline routing for credit report parsing."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

from worker.base import JobContext
from worker.constants import JobType
from worker.jobs.classify import DocumentClassifyJob
from worker.jobs.credit_report_parse import DocumentCreditReportParseJob


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


@patch("worker.jobs.credit_report_parse.enqueue_job")
@patch("worker.jobs.credit_report_parse.session_scope")
@patch("worker.jobs.credit_report_parse.parse_credit_report")
def test_credit_report_parse_creates_review_task(
    mock_parse_credit_report,
    mock_session_scope,
    mock_enqueue_job,
) -> None:
    document_id = uuid4()
    organization_id = uuid4()
    case_id = uuid4()
    account_id = uuid4()
    parsed_report_id = uuid4()
    mock_session = MagicMock()
    mock_session.execute.return_value.one_or_none.return_value = SimpleNamespace(
        confidence_score=0.94,
        organization_id=organization_id,
        document_type="credit_report",
    )
    mock_session_scope.return_value.__enter__.return_value = mock_session

    parsed = MagicMock()
    parsed.bureau.value = "experian"
    parsed.schema_version = "1.0"
    parsed.metadata = MagicMock(
        parser_name="experian",
        is_partial=False,
        warnings=(),
        field_confidence={"parser.layout_confidence": 0.91},
    )
    parsed.as_dict.return_value = {
        "bureau": "experian",
        "accounts": [{"creditor_name": "Verdin Bank"}],
    }
    mock_parse_credit_report.return_value = parsed

    with (
        patch(
            "worker.jobs.credit_report_parse.get_document_for_classification",
            return_value=MagicMock(
                ocr_text="Experian credit report",
                file_name="report.pdf",
                title="Report",
                mime_type="application/pdf",
                deleted_at=None,
            ),
        ),
        patch(
            "worker.jobs.credit_report_parse.upsert_parsed_credit_report",
            return_value=parsed_report_id,
        ),
        patch(
            "worker.jobs.credit_report_parse.get_document_timeline_context",
            return_value=SimpleNamespace(
                id=document_id,
                organization_id=organization_id,
                case_id=case_id,
                account_id=account_id,
                title="Report",
            ),
        ),
        patch("worker.jobs.credit_report_parse.append_timeline_event"),
        patch(
            "worker.jobs.credit_report_parse.create_parsed_report_review_task"
        ) as mock_create_task,
    ):
        result = DocumentCreditReportParseJob().run(
            JobContext(job_id="job-3", payload={"document_id": str(document_id)})
        )

    assert result.status.value == "completed"
    mock_create_task.assert_called_once_with(
        mock_session,
        organization_id=organization_id,
        case_id=case_id,
        account_id=account_id,
        document_id=document_id,
        document_title="Report",
        parsed_report_id=parsed_report_id,
        parsed_report={
            "bureau": "experian",
            "accounts": [{"creditor_name": "Verdin Bank"}],
        },
    )
    mock_enqueue_job.assert_called_once_with(
        JobType.DOCUMENT_METADATA_EXTRACT,
        {"document_id": str(document_id)},
    )
