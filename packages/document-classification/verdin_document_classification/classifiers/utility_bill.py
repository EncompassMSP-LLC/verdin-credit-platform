"""Utility bill classifier."""

from verdin_document_classification.base import ClassificationContext, ClassificationResult
from verdin_document_classification.helpers import keyword_match
from verdin_document_classification.constants import DocumentType


class UtilityBillClassifier:
    name = "utility_bill"

    _KEYWORDS = (
        "utility bill",
        "electric",
        "gas bill",
        "water bill",
        "service period",
        "kwh",
        "meter reading",
        "utility company",
    )

    def classify(self, context: ClassificationContext) -> ClassificationResult | None:
        return keyword_match(
            context,
            classifier_name=self.name,
            document_type=DocumentType.UTILITY_BILL,
            keywords=self._KEYWORDS,
            base_confidence=0.55,
        )
