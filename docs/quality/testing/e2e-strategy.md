# E2E Strategy

**Purpose:** define how end-to-end tests protect the platform without making the release gate slow or unpredictable.

## Golden Path

`tests/e2e/test_full_case_lifecycle.py` is the required golden-path workflow:

```text
Organization → User → Authenticate → Case → Account → Document Upload
→ OCR → Classification → Metadata → Entity Resolution → Timeline
→ Task → Mission Control
```

Keep this test:

- Fast enough to run on every merge.
- Deterministic.
- Focused on one successful customer journey.
- Required as a release gate once branch protection is configured.

## LRP smoke (LRP-503)

`tests/e2e/test_lrp_smoke.py` is the Mortgage Partner Edition smoke path in the same E2E workflow:

```text
Auth → mortgage-partner status → partnership → client/case/account
→ credit analysis → referral → pipeline/dashboard → readiness report
→ automation rules dry-run audit
```

CI enables `ENABLE_MORTGAGE_PARTNER=true`. The smoke stays claim-safe and never exercises unsupervised filing or live bureau pulls.

## Edge-Case Scenarios

Do not expand the golden-path test with edge cases. Add separate scenarios so failures remain isolated:

- `test_entity_resolution_ambiguous.py` — ambiguous match
- `test_entity_resolution_unmatched.py` — no match
- `test_ocr_failure_recovery.py` — OCR retry
- `test_worker_restart.py` — worker resilience

## Diagnostics

E2E failures should preserve:

- API responses
- OCR output
- Dashboard response
- API logs
- Worker logs
- MinIO logs
- Future UI screenshots

The current suite records per-stage diagnostic payloads and uploads artifacts from `.github/workflows/e2e.yml` on failure.

## Branch Protection

Once the workflow remains stable across multiple merges:

- Require the E2E workflow for merges to `main`.
- Require code review before merge.
- Require all required checks to pass.
- Consider requiring branches to be up to date before merge if multiple contributors are active.
