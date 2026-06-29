"""Document classification engine — rule-based classifiers with registry."""

from verdin_document_classification.base import (
    ClassificationContext,
    ClassificationResult,
    DocumentClassifier,
)
from verdin_document_classification.constants import ClassificationMethod, DocumentType
from verdin_document_classification.registry import classify_document, list_classifiers

__all__ = [
    "ClassificationContext",
    "ClassificationMethod",
    "ClassificationResult",
    "DocumentClassifier",
    "DocumentType",
    "classify_document",
    "list_classifiers",
]
