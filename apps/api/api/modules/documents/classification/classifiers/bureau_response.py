"""Bureau response classifier."""

from api.modules.documents.classification.base import ClassificationContext, ClassificationResult
from api.modules.documents.classification.helpers import keyword_match
from api.modules.documents.constants import DocumentType


class BureauResponseClassifier:
    name = "bureau_response"

    _KEYWORDS = (
        "bureau response",
        "investigation results",
        "dispute results",
        "results of investigation",
        "consumer disclosure",
        "furnisher response",
        "re-investigation",
    )

    def classify(self, context: ClassificationContext) -> ClassificationResult | None:
        return keyword_match(
            context,
            classifier_name=self.name,
            document_type=DocumentType.BUREAU_RESPONSE,
            keywords=self._KEYWORDS,
            base_confidence=0.6,
        )
