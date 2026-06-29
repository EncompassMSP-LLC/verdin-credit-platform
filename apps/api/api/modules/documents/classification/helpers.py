"""Shared helpers for keyword-based classifiers."""

from api.modules.documents.classification.base import (
    ClassificationContext,
    ClassificationResult,
)
from api.modules.documents.constants import ClassificationMethod, DocumentType


def keyword_match(
    context: ClassificationContext,
    *,
    classifier_name: str,
    document_type: DocumentType,
    keywords: tuple[str, ...],
    base_confidence: float = 0.55,
    per_match_boost: float = 0.1,
    max_confidence: float = 0.95,
) -> ClassificationResult | None:
    text = context.searchable_text()
    if not text:
        return None

    matches = sum(1 for keyword in keywords if keyword in text)
    if matches == 0:
        return None

    confidence = min(base_confidence + (matches - 1) * per_match_boost, max_confidence)
    return ClassificationResult(
        document_type=document_type,
        confidence_score=confidence,
        classification_method=ClassificationMethod.RULES,
        classifier_name=classifier_name,
    )
