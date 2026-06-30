"""Identity document classifier."""

from verdin_document_classification.base import ClassificationContext, ClassificationResult
from verdin_document_classification.constants import DocumentType
from verdin_document_classification.helpers import keyword_match


class IdentityDocumentClassifier:
    name = "identity_document"

    _KEYWORDS = (
        "driver license",
        "driver's license",
        "identification card",
        "state id",
        "passport",
        "date of birth",
        "identification document",
        "photo id",
    )

    def classify(self, context: ClassificationContext) -> ClassificationResult | None:
        return keyword_match(
            context,
            classifier_name=self.name,
            document_type=DocumentType.IDENTITY_DOCUMENT,
            keywords=self._KEYWORDS,
            base_confidence=0.6,
        )
