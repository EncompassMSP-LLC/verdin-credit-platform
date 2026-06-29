"""Court record classifier."""

from api.modules.documents.classification.base import ClassificationContext, ClassificationResult
from api.modules.documents.classification.helpers import keyword_match
from api.modules.documents.constants import DocumentType


class CourtRecordClassifier:
    name = "court_record"

    _KEYWORDS = (
        "court record",
        "court filing",
        "judgment",
        "summons",
        "complaint",
        "civil action",
        "superior court",
        "district court",
        "case number",
    )

    def classify(self, context: ClassificationContext) -> ClassificationResult | None:
        return keyword_match(
            context,
            classifier_name=self.name,
            document_type=DocumentType.COURT_RECORD,
            keywords=self._KEYWORDS,
            base_confidence=0.6,
        )
