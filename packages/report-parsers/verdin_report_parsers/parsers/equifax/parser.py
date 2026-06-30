"""Equifax report parser (stub — registered when layout rules are implemented)."""

from verdin_report_parsers.base import ParsedDocument
from verdin_report_parsers.constants import Bureau
from verdin_report_parsers.helpers import detect_bureau
from verdin_report_parsers.models import ParsedCreditReport


class EquifaxParser:
    name = "equifax"

    def can_parse(self, document: ParsedDocument) -> float:
        if detect_bureau(document.searchable_text()) != Bureau.EQUIFAX:
            return 0.0
        return 0.0

    def parse(self, document: ParsedDocument) -> ParsedCreditReport:
        raise NotImplementedError("Equifax layout parsing is not implemented yet")
