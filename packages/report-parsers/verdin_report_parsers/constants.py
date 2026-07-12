"""Shared constants for report parsing."""

from enum import StrEnum

PARSED_CREDIT_REPORT_SCHEMA_VERSION = "1.1"

_MIN_PARSER_CONFIDENCE = 0.5


class Bureau(StrEnum):
    EXPERIAN = "experian"
    EQUIFAX = "equifax"
    TRANSUNION = "transunion"
    INNOVIS = "innovis"
    UNKNOWN = "unknown"
