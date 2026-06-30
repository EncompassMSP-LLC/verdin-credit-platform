"""Court record classifier."""

from verdin_document_classification.base import ClassificationContext, ClassificationResult
from verdin_document_classification.constants import DocumentType
from verdin_document_classification.helpers import keyword_match


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
