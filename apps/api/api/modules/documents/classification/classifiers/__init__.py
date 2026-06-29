"""Document type classifiers."""

from api.modules.documents.classification.classifiers.bankruptcy import BankruptcyClassifier
from api.modules.documents.classification.classifiers.bureau_response import (
    BureauResponseClassifier,
)
from api.modules.documents.classification.classifiers.collection_letter import (
    CollectionLetterClassifier,
)
from api.modules.documents.classification.classifiers.court_record import CourtRecordClassifier
from api.modules.documents.classification.classifiers.credit_report import CreditReportClassifier
from api.modules.documents.classification.classifiers.identity_document import (
    IdentityDocumentClassifier,
)
from api.modules.documents.classification.classifiers.medical_collection import (
    MedicalCollectionClassifier,
)
from api.modules.documents.classification.classifiers.proof_of_address import (
    ProofOfAddressClassifier,
)
from api.modules.documents.classification.classifiers.unknown import UnknownClassifier
from api.modules.documents.classification.classifiers.utility_bill import UtilityBillClassifier

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
