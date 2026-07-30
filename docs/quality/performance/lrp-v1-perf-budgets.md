# LRP V1.0 Performance Budgets (LRP-504)

**Purpose:** define product latency budgets for Mortgage Partner Edition surfaces called out in the V1.0 exit criteria — partner dashboard and readiness export — and how we observe them in CI.

## Product budgets (p95)

Measured after one warm-up request; prefer median + p95 over single-shot timings.

| Surface                     | Endpoint                                                    | Local / staging p95 budget | CI observe ceiling* | Notes                                      |
| --------------------------- | ----------------------------------------------------------- | -------------------------- | ------------------- | ------------------------------------------ |
| Partner dashboard summary   | `GET /mortgage-partner/partnerships/{id}/dashboard-summary` | **≤ 500 ms**               | ≤ 3000 ms           | Stage counts + attention signals           |
| Readiness report (JSON)     | `GET .../referrals/{id}/readiness-report`                   | **≤ 750 ms**               | ≤ 4000 ms           | Band-first advisory report                 |
| Readiness export (text)     | `GET .../readiness-report/export?format=text`               | **≤ 1500 ms**              | ≤ 6000 ms           | Synchronous text export; PDF may be slower |
| Platform dashboard (shared) | `GET /dashboard`                                            | ≤ 500 ms                   | ≤ 3000 ms           | Cross-check vs v4.3.1 dashboard baseline   |

\*CI runners are noisier than local/staging. Observe ceilings are **non-blocking** soft gates used by the measure harness when `PERF_LRP_ENFORCE=observe` (default). Hard enforcement (`PERF_LRP_ENFORCE=1`) is reserved for calibrated environments.

## Explicit non-goals

- Live bureau soft-pull latency (deferred / never)
- Unsupervised filing throughput
- Cross-tenant marketplace load tests
- Blocking merges on flaky CI runner variance (observe-only until calibrated)

## How to measure

From the repository root, with API + Postgres up and `ENABLE_MORTGAGE_PARTNER=true`:

```bash
python docs/quality/performance/measure_lrp_perf_budgets.py
```

Environment:

| Variable            | Default                                             | Purpose                                        |
| ------------------- | --------------------------------------------------- | ---------------------------------------------- |
| `E2E_BASE_URL`      | `http://localhost:8000`                             | Running API                                    |
| `DATABASE_URL_SYNC` | local `verdin_credit_test` DSN                      | Seed org/user/partner                          |
| `PERF_ITERATIONS`   | `10`                                                | Timed iterations after warm-up                 |
| `PERF_LRP_ENFORCE`  | `observe`                                           | `observe` soft-fail; `1` exit non-zero on miss |
| `PERF_LRP_OUT`      | `docs/quality/performance/_artifacts/lrp-perf.json` | JSON results path                              |

## CI

`.github/workflows/e2e.yml` runs the harness after the E2E suite (observe mode) and uploads `lrp-perf.json` as an artifact. Failures in observe mode do not block the workflow.

## Rollout to enforcement

Follow [ci-thresholds.md](ci-thresholds.md): collect several CI artifacts, adjust ceilings for variance, then flip selected metrics to blocking only after calibration.
