"""Medical collection classifier."""

from api.modules.documents.classification.base import ClassificationContext, ClassificationResult
from api.modules.documents.classification.helpers import keyword_match
from api.modules.documents.constants import DocumentType


class MedicalCollectionClassifier:
    name = "medical_collection"

    _KEYWORDS = (
        "medical collection",
        "hospital",
        "patient account",
        "medical bill",
        "healthcare",
        "physician",
        "medical services",
        "patient responsibility",
    )

    def classify(self, context: ClassificationContext) -> ClassificationResult | None:
        return keyword_match(
            context,
            classifier_name=self.name,
            document_type=DocumentType.MEDICAL_COLLECTION,
            keywords=self._KEYWORDS,
            base_confidence=0.6,
        )
