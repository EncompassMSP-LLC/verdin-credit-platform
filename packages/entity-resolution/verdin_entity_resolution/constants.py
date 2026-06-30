"""Entity resolution constants."""

from enum import StrEnum


class MatchedEntityType(StrEnum):
    CASE = "case"
    ACCOUNT = "account"
    ORGANIZATION = "organization"
    PERSON = "person"


class ResolutionStatus(StrEnum):
    MATCHED = "matched"
    AMBIGUOUS = "ambiguous"
    UNMATCHED = "unmatched"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


class ResolutionMethod(StrEnum):
    RULES = "rules"
    MANUAL = "manual"
    AI = "ai"
