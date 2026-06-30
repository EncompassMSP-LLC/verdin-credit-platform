# Experian regression corpus — report_001

## Layout family

Experian 2026 consumer credit report (sanitized synthetic fixture).

## Purpose

Reference layout for the first production Experian parser. Validates:

- layout detection (`can_parse`)
- section segmentation (Personal Information, Accounts, Inquiries, Public Records, Collections)
- structured extraction into `ParsedCreditReport`
- parser provenance and deterministic confidence scoring

## Sanitization

All PII is synthetic:

| Field    | Value                                 |
| -------- | ------------------------------------- |
| Consumer | Alex M. Rivera                        |
| DOB      | 04/22/1990                            |
| SSN      | 123-45-6789 (masked in parser output) |

## Expected parser behavior

- `can_parse` confidence ≥ 0.99 (all layout signals present)
- `parse` selects bureau `experian`
- 2 tradelines, 2 inquiries, 1 public record, 1 collection
- `metadata.is_partial` = false
- `metadata.parser_name` = `experian`

## Regenerating the PDF

```bash
python tests/fixtures/credit_reports/experian/2026/build_report_001.py
```

## Updating expected output

When parser rules change intentionally, regenerate `report_001.expected.json` from the
regression harness snapshot utility in `apps/api/tests/report_parsers/corpus.py`.
