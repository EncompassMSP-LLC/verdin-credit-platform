# Credit report golden fixtures

Synthetic OCR/PDF corpus for parser regression.

```
tests/fixtures/credit_reports/
  experian/2026/
  equifax/2026/
  transunion/2026/
  identityiq/2026/
```

Each layout directory typically contains:

| File                       | Purpose                                       |
| -------------------------- | --------------------------------------------- |
| `build_report_001.py`      | Regenerates the PDF from sanitized text lines |
| `report_001.pdf`           | Golden PDF                                    |
| `report_001.expected.json` | Expected `ParsedCreditReport` snapshot        |
| `report_001.notes.md`      | Layout notes                                  |

Harness: `apps/api/tests/report_parsers/corpus.py` + `test_*_regression.py`.

```bash
cd apps/api
python -m pytest tests/report_parsers/test_experian_regression.py tests/report_parsers/test_identityiq_regression.py -q
```

See [`packages/report-parsers/README.md`](../../packages/report-parsers/README.md).
