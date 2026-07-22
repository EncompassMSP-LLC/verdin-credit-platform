# `@verdin/report-parsers` (`verdin_report_parsers`)

Heuristic OCR credit-report parsers used by the API and worker after classification.

**Not** live bureau APIs. Client-uploaded / monitoring PDFs only.

## Registered parsers

| Name         | Layout                          | Notes                                                                   |
| ------------ | ------------------------------- | ----------------------------------------------------------------------- |
| `identityiq` | IdentityIQ monitoring tri-merge | Expands bureau columns → per-bureau tradelines; report `bureau=unknown` |
| `experian`   | Experian consumer               | Single-bureau                                                           |
| `equifax`    | Equifax consumer                | Single-bureau                                                           |
| `transunion` | TransUnion consumer (+ ACR)     | ACR portal variants via layout helpers                                  |
| `fallback`   | Unknown                         | Partial parse when no bureau layout matches                             |

Registry: `verdin_report_parsers/registry.py` — highest `can_parse` confidence ≥ threshold wins.

On IdentityIQ documents, Experian/Equifax/TransUnion confidence is forced to `0` so the registry cannot mis-route.

## Golden fixtures

Corpus lives under `tests/fixtures/credit_reports/<layout>/2026/`:

```
report_001.pdf            # regenerated via build_report_001.py
report_001.expected.json  # version-controlled parse snapshot
report_001.notes.md       # layout notes
build_report_001.py       # synthetic PDF builder
```

Regression harness: `apps/api/tests/report_parsers/corpus.py` + `test_*_regression.py`.

```bash
# from apps/api with PYTHONPATH / editable install as usual
python -m pytest tests/report_parsers/test_identityiq_regression.py -q
python -m pytest tests/report_parsers/test_experian_regression.py -q
```

Regenerate an IdentityIQ PDF:

```bash
python tests/fixtures/credit_reports/identityiq/2026/build_report_001.py
```

## Docker note

Parsers are installed into API/worker images from `packages/report-parsers`. After changing parser code, rebuild:

```bash
docker compose build api worker
docker compose up -d api worker
```

## Related docs

- [API reference — credit report parse / reparse](../../docs/api/reference.md)
- [Engineering changelog](../../docs/engineering/changelog.md)
- [Version 28.0 scope — Monitoring Report Parser Depth](../../docs/governance/version-28.0-scope.md) (after Version 28.0 kickoff merges)
