"""Credit report classifier."""

from verdin_document_classification.base import ClassificationContext, ClassificationResult
from verdin_document_classification.constants import DocumentType
from verdin_document_classification.helpers import keyword_match

_CONSENT_EXCLUDE_MARKERS = (
    "signed —",
    "signed -",
    "signed-consent-",
    "croa disclosure",
    "fcra dispute authorization",
    "credit repair services agreement",
    "credit repair organizations act",
)


class CreditReportClassifier:
    name = "credit_report"

    _KEYWORDS = (
        "credit report",
        "consumer credit",
        "tradeline",
        "equifax",
        "experian",
        "transunion",
        "fico",
        "vantage score",
        "account number",
        "date of birth",
    )

    def classify(self, context: ClassificationContext) -> ClassificationResult | None:
        text = context.searchable_text()
        if any(marker in text for marker in _CONSENT_EXCLUDE_MARKERS):
            return None
        return keyword_match(
            context,
            classifier_name=self.name,
            document_type=DocumentType.CREDIT_REPORT,
            keywords=self._KEYWORDS,
            base_confidence=0.65,
        )
