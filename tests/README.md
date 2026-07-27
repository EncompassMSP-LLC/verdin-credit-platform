# Tests

Repository-level test suites that span multiple apps/services.

- [`e2e/`](e2e/README.md) — black-box HTTP workflows against a running stack (case lifecycle, dispute letter lifecycle, import→dispute). Used as a CI gate on `main`.
- [`fixtures/credit_reports/`](fixtures/credit_reports/) — golden credit-report corpus (Experian / Equifax / TransUnion / IdentityIQ). PDF + `*.expected.json` pairs exercised by `apps/api/tests/report_parsers/test_*_regression.py`.

Component-level tests live with their app (for example `apps/api/tests/`).

```bash
# API unit/integration (test DB)
cd apps/api
# PowerShell:
# $env:DATABASE_URL="postgresql+asyncpg://verdin:verdin@localhost:5432/verdin_credit_test"
python -m pytest

# Parser regression only
python -m pytest tests/report_parsers/test_identityiq_regression.py tests/report_parsers/test_experian_regression.py -q

# E2E (stack must be up — see e2e/README.md)
pytest tests/e2e -v
```
