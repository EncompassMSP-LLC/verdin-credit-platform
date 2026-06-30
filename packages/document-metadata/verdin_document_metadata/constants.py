"""Document metadata extraction constants."""

from enum import StrEnum


class ExtractionMethod(StrEnum):
    RULES = "rules"
    AI = "ai"


class MetadataStatus(StrEnum):
    PENDING = "pending"
    EXTRACTED = "extracted"
    FAILED = "failed"
