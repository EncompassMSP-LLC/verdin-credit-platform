"""Document classification engine — rule-based classifiers with registry."""

from verdin_document_classification.base import (
    ClassificationContext,
    ClassificationResult,
    DocumentClassifier,
)
from verdin_document_classification.registry import classify_document, list_classifiers

__all__ = [
    "ClassificationContext",
    "ClassificationResult",
    "DocumentClassifier",
    "classify_document",
    "list_classifiers",
]
