"""Guard document_metadata.payment_status column width for bureau narratives."""

from api.modules.documents.metadata_models import DocumentMetadata


def test_document_metadata_payment_status_accepts_bureau_narratives() -> None:
    column = DocumentMetadata.__table__.c.payment_status
    assert column.type.length == 255
