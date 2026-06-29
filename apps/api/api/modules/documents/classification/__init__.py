"""Document classification engine — re-exports shared package."""

from verdin_document_classification import (
    ClassificationContext,
    ClassificationResult,
    DocumentClassifier,
    classify_document,
    list_classifiers,
)
from verdin_document_classification.constants import ClassificationMethod, DocumentType

__all__ = [
    "ClassificationContext",
    "ClassificationResult",
    "ClassificationMethod",
    "DocumentClassifier",
    "DocumentType",
    "classify_document",
    "list_classifiers",
]
