"""Document classification engine — rule-based classifiers with registry."""

from api.modules.documents.classification.base import (
    ClassificationContext,
    ClassificationResult,
    DocumentClassifier,
)
from api.modules.documents.classification.registry import classify_document

__all__ = [
    "ClassificationContext",
    "ClassificationResult",
    "DocumentClassifier",
    "classify_document",
]
