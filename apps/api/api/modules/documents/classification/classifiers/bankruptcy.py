"""Bankruptcy filing classifier."""

from api.modules.documents.classification.base import ClassificationContext, ClassificationResult
from api.modules.documents.classification.helpers import keyword_match
from api.modules.documents.constants import DocumentType


class BankruptcyClassifier:
    name = "bankruptcy"

    _KEYWORDS = (
        "bankruptcy",
        "chapter 7",
        "chapter 13",
        "petition for bankruptcy",
        "discharge order",
        "trustee",
        "bankruptcy court",
    )

    def classify(self, context: ClassificationContext) -> ClassificationResult | None:
        return keyword_match(
            context,
            classifier_name=self.name,
            document_type=DocumentType.BANKRUPTCY,
            keywords=self._KEYWORDS,
            base_confidence=0.65,
        )
