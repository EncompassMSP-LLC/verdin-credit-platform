"""Document entity resolution worker job."""

from uuid import UUID

import structlog
from verdin_entity_resolution import (
    AccountCandidate,
    CaseCandidate,
    ResolutionContext,
    resolve_entities,
)

from worker.base import BaseJob, JobContext, JobResult
from worker.constants import JobStatus, JobType
from worker.db import session_scope
from worker.metadata_documents import (
    get_document_for_metadata,
    get_metadata_for_resolution,
    link_document_account,
    list_accounts,
    list_cases,
    replace_resolutions,
)
from worker.registry import register_job

logger = structlog.get_logger(__name__)


def _parse_document_id(payload: dict) -> UUID:
    raw = payload.get("document_id")
    if not raw:
        raise ValueError("document_id is required")
    return UUID(str(raw))


@register_job
class DocumentEntityResolveJob(BaseJob):
    job_type = JobType.DOCUMENT_ENTITY_RESOLVE

    def run(self, context: JobContext) -> JobResult:
        try:
            document_id = _parse_document_id(context.payload)
        except ValueError as exc:
            return JobResult(status=JobStatus.FAILED, message=str(exc))

        with session_scope() as session:
            document = get_document_for_metadata(session, document_id)
            if document is None:
                return JobResult(status=JobStatus.FAILED, message="Document not found")
            if document.deleted_at is not None:
                return JobResult(
                    status=JobStatus.CANCELLED, message="Document was deleted"
                )

            metadata = get_metadata_for_resolution(session, document_id)
            if metadata is None or metadata.metadata_status != "extracted":
                return JobResult(
                    status=JobStatus.FAILED,
                    message="Metadata must be extracted before entity resolution",
                )

            cases = list_cases(session, document.organization_id)
            accounts = list_accounts(
                session, document.case_id, document.organization_id
            )

            resolution_context = ResolutionContext(
                organization_id=str(document.organization_id),
                document_case_id=str(document.case_id),
                metadata={
                    "consumer_name": metadata.consumer_name,
                    "bureau": metadata.bureau,
                    "creditor": metadata.creditor,
                    "collection_agency": metadata.collection_agency,
                    "account_number_masked": metadata.account_number_masked,
                    "report_date": (
                        metadata.report_date.isoformat()
                        if metadata.report_date
                        else None
                    ),
                    "open_date": metadata.open_date.isoformat()
                    if metadata.open_date
                    else None,
                    "balance": metadata.balance,
                    "payment_status": metadata.payment_status,
                    "addresses": metadata.addresses,
                    "phone_numbers": metadata.phone_numbers,
                    "ssn_masked": metadata.ssn_masked,
                },
                cases=tuple(
                    CaseCandidate(
                        id=str(case.id),
                        client_name=case.client_name,
                        case_number=case.case_number,
                    )
                    for case in cases
                ),
                accounts=tuple(
                    AccountCandidate(
                        id=str(account.id),
                        creditor_name=account.creditor_name,
                        account_number_masked=account.account_number_masked,
                        bureau=account.bureau,
                        balance=account.balance,
                    )
                    for account in accounts
                ),
            )

            results = resolve_entities(resolution_context)
            resolution_rows = [
                {
                    "entity_type": result.entity_type.value,
                    "matched_entity_id": (
                        UUID(result.matched_entity_id)
                        if result.matched_entity_id
                        else None
                    ),
                    "confidence_score": result.confidence_score,
                    "resolution_status": result.resolution_status.value,
                    "resolution_method": result.resolution_method.value,
                    "reasoning": result.reasoning,
                    "candidate_entity_ids": list(result.candidate_entity_ids),
                }
                for result in results
            ]
            replace_resolutions(session, document, resolution_rows)

            account_resolution = next(
                (row for row in resolution_rows if row["entity_type"] == "account"),
                None,
            )
            if (
                account_resolution is not None
                and account_resolution["resolution_status"] == "matched"
                and account_resolution["matched_entity_id"] is not None
            ):
                link_document_account(
                    session,
                    document_id,
                    account_resolution["matched_entity_id"],
                )

        logger.info(
            "document_entities_resolved",
            job_id=context.job_id,
            document_id=str(document_id),
            resolution_count=len(results),
        )
        return JobResult(
            status=JobStatus.COMPLETED,
            message="Entities resolved",
            data={"resolution_count": len(results)},
        )
