# Repository Health Dashboard

**Purpose:** give anyone joining the project an immediate picture of repository health. Refresh this dashboard when closing a sprint or tagging a release.

**Last verified:** 2026-06-29 (local measurement against `main`)

## At a glance

| Metric             | Value                                     | Target / expectation                                                 | Status |
| ------------------ | ----------------------------------------- | -------------------------------------------------------------------- | ------ |
| Current version    | `v4.3.1` (tag) · Sprint 4.3.1 in progress | Stabilization complete before `v4.5.0` kickoff                       | 🟡     |
| API tests          | **120** passing                           | All integration tests green in CI                                    | ✅     |
| E2E tests          | **1** golden path                         | `test_full_case_lifecycle` required in CI                            | ✅     |
| CI                 | Lint, typecheck, pytest, build, Docker    | All workflows green on `main`                                        | ✅     |
| API coverage       | **90%** (`api/` package)                  | 85–90% on core services (sprint exit criteria)                       | ✅     |
| Critical bugs      | **0** open                                | None blocking Operational Core                                       | ✅     |
| Performance SLAs   | **4 / 5** met                             | Login follow-up (`<150 ms` target)                                   | 🟡     |
| Worker baselines   | **5 / 5** captured                        | OCR, classification, metadata, entity resolution recorded            | ✅     |
| Security review    | Complete                                  | Checklist complete; no unresolved findings                           | ✅     |
| Architecture drift | **None** detected                         | Matches [v4.3.0 snapshot](../architecture/v4.3.0-snapshot.md)        | ✅     |
| Branch protection  | Complete                                  | PR review, strict CI/E2E status checks, conversations, no force push | ✅     |

## Sprint 4.3.1 workstream status

| Workstream              | Status      | Reference                                                                                  |
| ----------------------- | ----------- | ------------------------------------------------------------------------------------------ |
| E2E workflow validation | ✅ Complete | [`tests/e2e/`](../../tests/e2e/README.md)                                                  |
| Performance baselines   | ✅ Complete | [`docs/quality/performance/v4.3.1-baseline.md`](../quality/performance/v4.3.1-baseline.md) |
| Security review         | ✅ Complete | [`docs/quality/security/v4.3.1-review.md`](../quality/security/v4.3.1-review.md)           |
| Coverage improvements   | ✅ Complete | [`docs/quality/testing/coverage-plan.md`](../quality/testing/coverage-plan.md)             |
| Branch protection       | ✅ Complete | `main` requires review plus strict CI and E2E checks                                       |

## Performance detail

Synchronous endpoint SLAs from the [v4.3.1 baseline](../quality/performance/v4.3.1-baseline.md):

| Metric          | Target    | Result                                       | Status       |
| --------------- | --------- | -------------------------------------------- | ------------ |
| Dashboard API   | `<500 ms` | 86.52 ms avg                                 | ✅           |
| Login           | `<150 ms` | 330.89 ms avg verified; bcrypt avg 285.14 ms | 🟡 Follow-up |
| Create case     | `<200 ms` | 21.67 ms avg                                 | ✅           |
| Upload document | `<500 ms` | 138.27 ms avg                                | ✅           |
| Timeline write  | `<100 ms` | 7.50 ms avg                                  | ✅           |

Worker pipeline stages are baselined (not SLA-gated yet). Candidate CI regression thresholds are documented in [`ci-thresholds.md`](../quality/performance/ci-thresholds.md).

## How to refresh this dashboard

Run from the repository root unless noted.

**API test count and pass rate**

```bash
cd apps/api
python -m pytest tests/ -q
```

**API coverage**

```bash
cd apps/api
python -m pytest tests/ --cov=api --cov-report=term-missing:skip-covered -q
```

**E2E golden path** (requires Docker stack — Postgres, Redis, MinIO, API, worker)

```bash
cd tests/e2e
python -m pytest test_full_case_lifecycle.py -v
```

**Performance baselines**

```bash
python docs/quality/performance/measure_v431_baseline.py
```

Update the tables above with the new counts, dates, and pass/fail status. Link any regressions to GitHub issues and the [incident log](../quality/reliability/incident-log.md).

## Related documents

- [Architecture scorecard](architecture-scorecard.md) — release-level architectural review
- [Capability matrix](capability-matrix.md) — product capability readiness
- [Quality hub](../quality/README.md) — performance, security, testing, reliability
- [Sprint 4.3.1 plan](../sprint-4.3.1/operational-core-stabilization.md) — stabilization exit criteria
