"""Report parser exceptions.

The fallback parser is designed never to raise. Bureau-specific parsers may raise
these exceptions when strict parsing is required in future versions.
"""


class ReportParseError(Exception):
    """Base error for report parsing failures."""


class UnsupportedReportFormatError(ReportParseError):
    """Raised when no parser can handle a document and fallback is disabled."""


class BureauParserError(ReportParseError):
    """Raised when a bureau parser encounters an unrecoverable format error."""
