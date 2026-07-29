# Performance CI Thresholds

**Purpose:** define how performance regression checks should move from observation to enforcement.

Performance gates should not be blocking until they have been observed across multiple CI runs. Developer machines and CI runners vary; thresholds should be calibrated from CI data, not one local run.

## Rollout Plan

1. Add a non-blocking CI benchmark job that runs the benchmark harness and uploads raw JSON output as an artifact.
2. Collect results across several merges.
3. Establish CI variance for stable metrics.
4. Enable blocking thresholds only for low-variance metrics.
5. Revisit thresholds each release after changes in infrastructure, dependencies, or workload shape.

## Candidate Thresholds

Initial candidates based on the v4.3.1 local baseline:

| Metric          | Candidate Failure Threshold | Enforcement Status | Notes                                         |
| --------------- | --------------------------- | ------------------ | --------------------------------------------- |
| Dashboard API   | `>250 ms avg`               | Observe only       | Useful early signal for aggregation drift.    |
| Create Case     | `>100 ms avg`               | Observe only       | Catches large service/repository regressions. |
| Timeline Write  | `>25 ms avg`                | Observe only       | Timeline is central to Mission Control.       |
| Document Upload | `>300 ms avg` excluding OCR | Observe only       | Keep storage/upload regressions visible.      |

### LRP V1.0 budgets (LRP-504)

See [lrp-v1-perf-budgets.md](lrp-v1-perf-budgets.md). Harness: `measure_lrp_perf_budgets.py` (runs in E2E workflow, observe mode).

| Metric                    | Product p95 budget | CI observe ceiling | Enforcement Status |
| ------------------------- | ------------------ | ------------------ | ------------------ |
| Partner dashboard summary | ≤ 500 ms           | ≤ 3000 ms          | Observe only       |
| Readiness report JSON     | ≤ 750 ms           | ≤ 4000 ms          | Observe only       |
| Readiness export (text)   | ≤ 1500 ms          | ≤ 6000 ms          | Observe only       |

## Metrics To Avoid Blocking Initially

- Login latency: currently above the initial local target and needs profiling before threshold enforcement.
- OCR/classification/metadata/entity-resolution timings: useful as baselines, but asynchronous worker timing should be calibrated in CI before blocking.

## Required Before Enforcement

- [x] CI benchmark job exists and uploads raw JSON artifacts. (LRP harness via E2E workflow, observe mode)
- [ ] At least several CI runs are recorded.
- [ ] Thresholds are based on CI variance, not local machine timings.
- [ ] Flaky metrics are excluded or remain observe-only.
- [ ] Required checks are documented in branch protection settings.
