# IdentityIQ regression corpus — report_001

## Layout family

IdentityIQ 2026 member monitoring / tri-merge credit report (sanitized synthetic fixture).

## Purpose

Reference layout for the IdentityIQ parser. Validates:

- layout detection (`can_parse`) and registry preference over single-bureau parsers
- section segmentation (Personal Information, Accounts, Inquiries, Public Records, Collections)
- tri-bureau account column expansion into per-bureau tradelines
- structured extraction into `ParsedCreditReport`

## Sanitization

All PII is synthetic:

| Field    | Value                                 |
| -------- | ------------------------------------- |
| Consumer | Alex M. Rivera                        |
| DOB      | 04/22/1990                            |
| SSN      | 123-45-6789 (masked in parser output) |

## Expected parser behavior

- `can_parse` confidence ≥ 0.9 (IdentityIQ branding + section signals)
- `parse` selects report-level bureau `unknown`
- 5 tradelines (First Horizon × 3 bureaus + Metro Retail × TU/EX), 2 inquiries, 1 public record, 1 collection
- `metadata.is_partial` = false
- `metadata.parser_name` = `identityiq`

## Regenerating the PDF

```bash
python tests/fixtures/credit_reports/identityiq/2026/build_report_001.py
```

## Updating expected output

When parser rules change intentionally, regenerate `report_001.expected.json` by parsing the
PDF with `IdentityIQParser` and writing via `report_to_comparable_dict` in
`apps/api/tests/report_parsers/corpus.py`.
