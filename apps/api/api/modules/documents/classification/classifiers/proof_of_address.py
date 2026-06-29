"""Proof of address classifier."""

from api.modules.documents.classification.base import ClassificationContext, ClassificationResult
from api.modules.documents.classification.helpers import keyword_match
from api.modules.documents.constants import DocumentType


class ProofOfAddressClassifier:
    name = "proof_of_address"

    _KEYWORDS = (
        "proof of address",
        "proof of residency",
        "residence verification",
        "lease agreement",
        "mortgage statement",
        "bank statement",
        "service address",
    )

    def classify(self, context: ClassificationContext) -> ClassificationResult | None:
        return keyword_match(
            context,
            classifier_name=self.name,
            document_type=DocumentType.PROOF_OF_ADDRESS,
            keywords=self._KEYWORDS,
            base_confidence=0.55,
        )
