"""Document type classifiers."""

from verdin_document_classification.classifiers.bankruptcy import BankruptcyClassifier
from verdin_document_classification.classifiers.bureau_response import (
    BureauResponseClassifier,
)
from verdin_document_classification.classifiers.collection_letter import (
    CollectionLetterClassifier,
)
from verdin_document_classification.classifiers.court_record import CourtRecordClassifier
from verdin_document_classification.classifiers.credit_report import CreditReportClassifier
from verdin_document_classification.classifiers.identity_document import (
    IdentityDocumentClassifier,
)
from verdin_document_classification.classifiers.medical_collection import (
    MedicalCollectionClassifier,
)
from verdin_document_classification.classifiers.proof_of_address import (
    ProofOfAddressClassifier,
)
from verdin_document_classification.classifiers.unknown import UnknownClassifier
from verdin_document_classification.classifiers.utility_bill import UtilityBillClassifier

__all__ = [
    "BankruptcyClassifier",
    "BureauResponseClassifier",
    "CollectionLetterClassifier",
    "CourtRecordClassifier",
    "CreditReportClassifier",
    "IdentityDocumentClassifier",
    "MedicalCollectionClassifier",
    "ProofOfAddressClassifier",
    "UnknownClassifier",
    "UtilityBillClassifier",
]
