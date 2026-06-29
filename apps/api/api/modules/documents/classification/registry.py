"""Classifier registry — evaluates all classifiers and picks the best result."""

from api.modules.documents.classification.base import (
    ClassificationContext,
    ClassificationResult,
    DocumentClassifier,
)
from api.modules.documents.classification.classifiers import (
    BankruptcyClassifier,
    BureauResponseClassifier,
    CollectionLetterClassifier,
    CourtRecordClassifier,
    CreditReportClassifier,
    IdentityDocumentClassifier,
    MedicalCollectionClassifier,
    ProofOfAddressClassifier,
    UnknownClassifier,
    UtilityBillClassifier,
)
from api.modules.documents.constants import DocumentType

_MIN_CONFIDENCE = 0.5

_CLASSIFIERS: tuple[DocumentClassifier, ...] = (
    CreditReportClassifier(),
    BureauResponseClassifier(),
    CollectionLetterClassifier(),
    IdentityDocumentClassifier(),
    ProofOfAddressClassifier(),
    BankruptcyClassifier(),
    CourtRecordClassifier(),
    MedicalCollectionClassifier(),
    UtilityBillClassifier(),
)

_UNKNOWN = UnknownClassifier()


def list_classifiers() -> tuple[DocumentClassifier, ...]:
    return _CLASSIFIERS


def classify_document(context: ClassificationContext) -> ClassificationResult:
    """Run every registered classifier and return the highest-confidence result."""
    best: ClassificationResult | None = None

    for classifier in _CLASSIFIERS:
        result = classifier.classify(context)
        if result is None:
            continue
        if best is None or result.confidence_score > best.confidence_score:
            best = result

    if best is None or best.confidence_score < _MIN_CONFIDENCE:
        return _UNKNOWN.classify(context) or ClassificationResult(
            document_type=DocumentType.UNKNOWN,
            confidence_score=0.1,
            classifier_name="unknown",
        )

    return best
