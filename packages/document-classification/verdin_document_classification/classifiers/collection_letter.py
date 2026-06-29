"""Collection letter classifier."""

from verdin_document_classification.base import ClassificationContext, ClassificationResult
from verdin_document_classification.helpers import keyword_match
from verdin_document_classification.constants import DocumentType


class CollectionLetterClassifier:
    name = "collection_letter"

    _KEYWORDS = (
        "collection agency",
        "debt collector",
        "amount due",
        "past due",
        "pay this amount",
        "collection letter",
        "attempt to collect",
        "validation of debt",
    )

    def classify(self, context: ClassificationContext) -> ClassificationResult | None:
        return keyword_match(
            context,
            classifier_name=self.name,
            document_type=DocumentType.COLLECTION_LETTER,
            keywords=self._KEYWORDS,
            base_confidence=0.6,
        )
