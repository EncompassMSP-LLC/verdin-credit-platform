"""Fallback classifier when no rule matches with sufficient confidence."""

from api.modules.documents.classification.base import ClassificationContext, ClassificationResult
from api.modules.documents.constants import ClassificationMethod, DocumentType


class UnknownClassifier:
    name = "unknown"

    def classify(self, context: ClassificationContext) -> ClassificationResult | None:
        del context
        return ClassificationResult(
            document_type=DocumentType.UNKNOWN,
            confidence_score=0.1,
            classification_method=ClassificationMethod.RULES,
            classifier_name=self.name,
        )
