# Equifax regression corpus — report_001

## Layout Family

Equifax 2026 consumer credit file (sanitized synthetic fixture).

## Purpose

Second-parser validation fixture for the Version 4.5 credit report intelligence contract.
This layout intentionally differs from the Experian fixture by using Equifax-style section
names and field labels:

- `CONSUMER INFORMATION`
- `TRADELINES`
- `CREDIT INQUIRIES`
- `PUBLIC RECORD INFORMATION`
- `COLLECTION ACCOUNTS`

## Sanitization

All PII is synthetic:

| Field    | Value                                 |
| -------- | ------------------------------------- |
| Consumer | Morgan T. Lee                         |
| DOB      | 09/18/1988                            |
| SSN      | 987-65-4321 (masked in parser output) |

## Expected Parser Behavior

- `can_parse` confidence >= 0.99 when all layout signals are present
- `parse` selects bureau `equifax`
- 2 tradelines, 1 inquiry, 1 public record, 1 collection
- `metadata.is_partial` = false
- `metadata.parser_name` = `equifax`

## Regenerating The PDF

```bash
python tests/fixtures/credit_reports/equifax/2026/build_report_001.py
```

## Updating Expected Output

When parser rules change intentionally, regenerate `report_001.expected.json` from the
regression harness snapshot utility in `apps/api/tests/report_parsers/corpus.py`.
