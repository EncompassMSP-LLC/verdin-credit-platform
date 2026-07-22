"""Parser registry — selects the best bureau parser or falls back."""

from verdin_report_parsers.base import CreditReportParser, ParsedDocument
from verdin_report_parsers.constants import _MIN_PARSER_CONFIDENCE
from verdin_report_parsers.models import ParsedCreditReport
from verdin_report_parsers.parsers.equifax.parser import EquifaxParser
from verdin_report_parsers.parsers.experian.parser import ExperianParser
from verdin_report_parsers.parsers.fallback.parser import FallbackParser
from verdin_report_parsers.parsers.identityiq.parser import IdentityIQParser
from verdin_report_parsers.parsers.smartcredit.parser import SmartCreditParser
from verdin_report_parsers.parsers.transunion.parser import TransUnionParser

_BUREAU_PARSERS: tuple[CreditReportParser, ...] = (
    IdentityIQParser(),
    SmartCreditParser(),
    ExperianParser(),
    EquifaxParser(),
    TransUnionParser(),
)
_FALLBACK = FallbackParser()


def list_parsers() -> tuple[CreditReportParser, ...]:
    return _BUREAU_PARSERS + (_FALLBACK,)


def list_bureau_parsers() -> tuple[CreditReportParser, ...]:
    return _BUREAU_PARSERS


def select_parser(document: ParsedDocument) -> CreditReportParser:
    """Return the highest-confidence bureau parser, or the fallback."""
    best_parser: CreditReportParser | None = None
    best_confidence = 0.0

    for parser in _BUREAU_PARSERS:
        confidence = parser.can_parse(document)
        if confidence > best_confidence:
            best_confidence = confidence
            best_parser = parser

    if best_parser is not None and best_confidence >= _MIN_PARSER_CONFIDENCE:
        return best_parser

    return _FALLBACK


def parse_credit_report(document: ParsedDocument) -> ParsedCreditReport:
    """Parse a classified document into a versioned ``ParsedCreditReport``."""
    parser = select_parser(document)
    return parser.parse(document)
