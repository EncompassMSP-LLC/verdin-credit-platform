"""Worker OCR → classification enqueue tests."""

from contextlib import contextmanager
from unittest.mock import patch
from uuid import uuid4

from worker.base import JobContext, JobResult
from worker.constants import JobStatus, JobType
from worker.documents import DocumentRecord
from worker.jobs.ocr import OcrJob


def test_ocr_completion_enqueues_classification() -> None:
    document_id = uuid4()
    document = DocumentRecord(
        id=document_id,
        storage_key="org/case/doc/file.pdf",
        mime_type="application/pdf",
        version_number=1,
        processing_status="processing",
        deleted_at=None,
    )

    @contextmanager
    def fake_session_scope():
        yield object()

    with (
        patch("worker.jobs.ocr.enqueue_job") as mock_enqueue,
        patch("worker.jobs.ocr.session_scope", fake_session_scope),
        patch("worker.jobs.ocr.get_document", return_value=document),
        patch("worker.jobs.ocr.mark_processing"),
        patch("worker.jobs.ocr._process_document") as mock_process,
        patch("worker.jobs.ocr.save_ocr_success"),
        patch("worker.jobs.ocr.save_ocr_failure"),
    ):
        mock_process.return_value = JobResult(
            status=JobStatus.COMPLETED,
            message="ok",
            data={"text": "sample", "version_number": 1},
        )
        job = OcrJob()
        job.run(JobContext(job_id="j1", payload={"document_id": str(document_id)}))

    mock_enqueue.assert_called_once_with(
        JobType.DOCUMENT_CLASSIFY,
        {"document_id": str(document_id)},
    )
