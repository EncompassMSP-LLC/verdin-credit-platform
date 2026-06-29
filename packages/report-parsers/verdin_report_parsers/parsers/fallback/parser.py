"""Fallback parser for unknown or unsupported bureau report layouts."""

from verdin_report_parsers.base import ParsedDocument
from verdin_report_parsers.constants import Bureau
from verdin_report_parsers.helpers import (
    detect_bureau,
    extract_account_number_masked,
    extract_address,
    extract_balance,
    extract_collection_agency,
    extract_consumer_name,
    extract_creditor,
    extract_dob,
    extract_inquiry_creditor,
    extract_open_date,
    extract_payment_status,
    extract_ssn_masked,
)
from verdin_report_parsers.models import (
    Collection,
    ConsumerInfo,
    Inquiry,
    ParseMetadata,
    ParsedCreditReport,
    PersonalInformation,
    ReportSummary,
    TradelineAccount,
)

_FALLBACK_CONFIDENCE = 0.15


class FallbackParser:
    """Always eligible; returns a partial report with confidence indicators."""

    name = "fallback"

    def can_parse(self, document: ParsedDocument) -> float:
        del document
        return _FALLBACK_CONFIDENCE

    def parse(self, document: ParsedDocument) -> ParsedCreditReport:
        source_text = document.source_text()
        searchable_text = document.searchable_text()
        field_confidence: dict[str, float] = {}
        warnings: list[str] = []

        bureau = detect_bureau(searchable_text)
        if bureau == Bureau.UNKNOWN:
            warnings.append("bureau_not_detected")

        consumer_name, consumer_name_conf = extract_consumer_name(source_text)
        if consumer_name:
            field_confidence["consumer.name"] = consumer_name_conf

        dob, dob_conf = extract_dob(source_text)
        if dob:
            field_confidence["consumer.date_of_birth"] = dob_conf

        ssn_masked, ssn_conf = extract_ssn_masked(source_text)
        if ssn_masked:
            field_confidence["consumer.ssn_masked"] = ssn_conf

        consumer_confidences = [c for c in (consumer_name_conf, dob_conf, ssn_conf) if c > 0]
        consumer = ConsumerInfo(
            name=consumer_name,
            date_of_birth=dob,
            ssn_masked=ssn_masked,
            confidence=max(consumer_confidences) if consumer_confidences else 0.0,
        )

        creditor_name, creditor_conf = extract_creditor(source_text)
        account_masked, account_conf = extract_account_number_masked(source_text)
        balance, balance_conf = extract_balance(source_text)
        payment_status, status_conf = extract_payment_status(source_text)
        open_date, open_conf = extract_open_date(source_text)

        accounts: tuple[TradelineAccount, ...] = ()
        if creditor_name or account_masked or balance is not None:
            account_field_confidences = [
                c for c in (creditor_conf, account_conf, balance_conf, status_conf, open_conf) if c > 0
            ]
            if creditor_name:
                field_confidence["accounts[0].creditor_name"] = creditor_conf
            if account_masked:
                field_confidence["accounts[0].account_number_masked"] = account_conf
            if balance is not None:
                field_confidence["accounts[0].balance"] = balance_conf
            if payment_status:
                field_confidence["accounts[0].payment_status"] = status_conf
            if open_date:
                field_confidence["accounts[0].open_date"] = open_conf

            accounts = (
                TradelineAccount(
                    creditor_name=creditor_name,
                    account_number_masked=account_masked,
                    balance=balance,
                    payment_status=payment_status,
                    open_date=open_date,
                    bureau=bureau.value if bureau != Bureau.UNKNOWN else None,
                    confidence=max(account_field_confidences) if account_field_confidences else 0.0,
                ),
            )
        else:
            warnings.append("no_tradelines_extracted")

        inquiry_creditor, inquiry_conf = extract_inquiry_creditor(source_text)
        inquiries: tuple[Inquiry, ...] = ()
        if inquiry_creditor:
            field_confidence["inquiries[0].creditor_name"] = inquiry_conf
            inquiries = (Inquiry(creditor_name=inquiry_creditor, confidence=inquiry_conf),)

        agency_name, collection_conf = extract_collection_agency(source_text)
        collections: tuple[Collection, ...] = ()
        if agency_name:
            field_confidence["collections[0].agency_name"] = collection_conf
            collections = (Collection(agency_name=agency_name, confidence=collection_conf),)

        address, address_conf = extract_address(source_text)
        personal_information: tuple[PersonalInformation, ...] = ()
        if address:
            field_confidence["personal_information.address"] = address_conf
            personal_information = (
                PersonalInformation(field_name="address", value=address, confidence=address_conf),
            )

        total_balance = balance
        summary = ReportSummary(
            total_accounts=len(accounts),
            total_inquiries=len(inquiries),
            total_public_records=0,
            total_collections=len(collections),
            total_balance=total_balance,
            confidence=max(field_confidence.values()) if field_confidence else 0.0,
        )

        if not field_confidence:
            warnings.append("minimal_extraction")

        return ParsedCreditReport(
            report_id=document.document_id,
            bureau=bureau,
            consumer=consumer if consumer.name or consumer.date_of_birth or consumer.ssn_masked else None,
            accounts=accounts,
            inquiries=inquiries,
            public_records=(),
            collections=collections,
            personal_information=personal_information,
            summary=summary,
            metadata=ParseMetadata.now(
                parser_name=self.name,
                classification_type=document.document_type,
                classification_confidence=document.classification_confidence,
                field_confidence=field_confidence,
                warnings=tuple(warnings),
                is_partial=True,
            ),
        )
