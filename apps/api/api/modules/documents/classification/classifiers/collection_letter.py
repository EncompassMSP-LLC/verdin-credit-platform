"""Collection letter classifier."""

from api.modules.documents.classification.base import ClassificationContext, ClassificationResult
from api.modules.documents.classification.helpers import keyword_match
from api.modules.documents.constants import DocumentType


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
