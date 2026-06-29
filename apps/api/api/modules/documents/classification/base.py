"""Document classification contracts — re-export from shared package."""

from verdin_document_classification.base import (
    ClassificationContext,
    ClassificationResult,
    DocumentClassifier,
)

__all__ = ["ClassificationContext", "ClassificationResult", "DocumentClassifier"]
