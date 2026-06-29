"""Classification contracts and shared types."""

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from api.modules.documents.constants import ClassificationMethod, DocumentType


@dataclass(frozen=True, slots=True)
class ClassificationContext:
    """Inputs available to every classifier."""

    ocr_text: str | None
    file_name: str
    title: str
    mime_type: str | None

    def searchable_text(self) -> str:
        parts = [self.title, self.file_name]
        if self.ocr_text:
            parts.append(self.ocr_text)
        return " ".join(parts).lower()


@dataclass(frozen=True, slots=True)
class ClassificationResult:
    document_type: DocumentType
    confidence_score: float
    classification_method: ClassificationMethod = ClassificationMethod.RULES
    classifier_name: str = ""


@runtime_checkable
class DocumentClassifier(Protocol):
    """Evaluate a document and return a typed result with confidence, or None."""

    name: str

    def classify(self, context: ClassificationContext) -> ClassificationResult | None: ...
