"""Signed consent / disclosure classifier.

Portal CROA/FCRA consent PDFs mention Equifax/Experian/TransUnion and "credit
report" language, so they must outrank the credit-report classifier.
"""

from verdin_document_classification.base import ClassificationContext, ClassificationResult
from verdin_document_classification.constants import ClassificationMethod, DocumentType
from verdin_document_classification.helpers import keyword_match


class SignedConsentClassifier:
    name = "signed_consent"

    _KEYWORDS = (
        "croa disclosure",
        "credit repair organizations act",
        "credit repair services agreement",
        "fcra dispute authorization",
        "fair credit reporting act authorization",
        "notice of cancellation",
        "signed consent",
        "consumer authorization",
        "portal consent",
    )

    def classify(self, context: ClassificationContext) -> ClassificationResult | None:
        title = (context.title or "").strip().lower()
        file_name = (context.file_name or "").strip().lower()

        if title.startswith("signed —") or title.startswith("signed -"):
            return ClassificationResult(
                document_type=DocumentType.SIGNED_CONSENT,
                confidence_score=0.99,
                classification_method=ClassificationMethod.RULES,
                classifier_name=self.name,
            )
        if file_name.startswith("signed-consent-"):
            return ClassificationResult(
                document_type=DocumentType.SIGNED_CONSENT,
                confidence_score=0.99,
                classification_method=ClassificationMethod.RULES,
                classifier_name=self.name,
            )

        return keyword_match(
            context,
            classifier_name=self.name,
            document_type=DocumentType.SIGNED_CONSENT,
            keywords=self._KEYWORDS,
            base_confidence=0.9,
            per_match_boost=0.03,
            max_confidence=0.98,
        )
