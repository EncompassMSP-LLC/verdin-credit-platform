"""Production Equifax consumer credit report parser."""

from verdin_report_parsers.base import ParsedDocument
from verdin_report_parsers.constants import Bureau
from verdin_report_parsers.models import ParseMetadata, ParsedCreditReport
from verdin_report_parsers.parsers.equifax.extract import (
    build_summary,
    extract_accounts,
    extract_collections,
    extract_consumer,
    extract_inquiries,
    extract_public_records,
    extract_report_date,
)
from verdin_report_parsers.parsers.equifax.layout import is_acr_layout, score_layout, split_sections

PARSER_VERSION = "1.0.0"


class EquifaxParser:
    """Parse Equifax 2026 consumer credit report layouts into ``ParsedCreditReport``."""

    name = "equifax"
    version = PARSER_VERSION

    def can_parse(self, document: ParsedDocument) -> float:
        layout = score_layout(document.source_text())
        return layout.confidence

    def parse(self, document: ParsedDocument) -> ParsedCreditReport:
        source_text = document.source_text()
        layout = score_layout(source_text)
        sections = split_sections(source_text)

        field_confidence: dict[str, float] = dict(layout.signals)
        warnings: list[str] = []

        consumer, consumer_confidence = extract_consumer(
            sections.get("consumer_information", ""),
            source_text,
        )
        field_confidence.update(consumer_confidence)

        accounts, account_confidence = extract_accounts(
            sections.get("tradelines", ""),
            full_text=source_text,
        )
        field_confidence.update(account_confidence)
        if not accounts:
            warnings.append("no_tradelines_extracted")

        inquiries, inquiry_confidence = extract_inquiries(sections.get("credit_inquiries", ""))
        field_confidence.update(inquiry_confidence)

        public_records, public_record_confidence = extract_public_records(
            sections.get("public_record_information", "")
        )
        field_confidence.update(public_record_confidence)

        collections, collection_confidence = extract_collections(
            sections.get("collection_accounts", "")
        )
        field_confidence.update(collection_confidence)

        report_date, report_date_confidence = extract_report_date(source_text)
        field_confidence.update(report_date_confidence)
        if report_date is None:
            warnings.append("report_date_missing")

        summary = build_summary(accounts, inquiries, public_records, collections, field_confidence)
        field_confidence["parser.layout_confidence"] = layout.confidence

        required_sections = (
            ("consumer_information", "tradelines")
            if is_acr_layout(source_text)
            else (
                "consumer_information",
                "tradelines",
                "credit_inquiries",
                "public_record_information",
                "collection_accounts",
            )
        )
        missing_sections = [name for name in required_sections if name not in sections]
        if missing_sections:
            warnings.append(f"missing_sections:{','.join(missing_sections)}")

        return ParsedCreditReport(
            report_id=document.document_id,
            bureau=Bureau.EQUIFAX,
            consumer=consumer,
            accounts=accounts,
            inquiries=inquiries,
            public_records=public_records,
            collections=collections,
            personal_information=(),
            summary=summary,
            metadata=ParseMetadata.now(
                parser_name=self.name,
                classification_type=document.document_type,
                classification_confidence=document.classification_confidence,
                field_confidence=field_confidence,
                warnings=tuple(warnings),
                is_partial=bool(missing_sections or not accounts),
            ),
        )
