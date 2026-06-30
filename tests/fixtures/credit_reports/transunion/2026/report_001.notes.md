# TransUnion regression corpus — report_001

## Layout Family

TransUnion 2026 consumer credit report (sanitized synthetic fixture).

## Purpose

Third-parser expansion fixture for the Version 4.5 credit report intelligence contract.
This layout intentionally differs from Experian and Equifax by using TransUnion-style
section names and field labels:

- `PERSONAL INFORMATION`
- `ACCOUNTS`
- `INQUIRIES`
- `PUBLIC RECORDS`
- `COLLECTIONS`
- `Subscriber:` (not Furnisher/Creditor)
- `Date Opened` / `Date Updated` (not Opened/Last Reported)

## Sanitization

All PII is synthetic:

| Field    | Value                                 |
| -------- | ------------------------------------- |
| Consumer | Avery J. Morgan                       |
| DOB      | 05/12/1987                            |
| SSN      | 456-78-9012 (masked in parser output) |

## Expected Parser Behavior

- `can_parse` confidence >= 0.99 when all layout signals are present
- `parse` selects bureau `transunion`
- 2 accounts, 1 inquiry, 1 public record, 1 collection
- `metadata.is_partial` = false
- `metadata.parser_name` = `transunion`

## Regenerating The PDF

```bash
python tests/fixtures/credit_reports/transunion/2026/build_report_001.py
```

## Updating Expected Output

When parser rules change intentionally, regenerate `report_001.expected.json` from the
regression harness snapshot utility in `apps/api/tests/report_parsers/corpus.py`.
