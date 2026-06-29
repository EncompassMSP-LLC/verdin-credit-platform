"""Bankruptcy filing classifier."""

from verdin_document_classification.base import ClassificationContext, ClassificationResult
from verdin_document_classification.helpers import keyword_match
from verdin_document_classification.constants import DocumentType


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
