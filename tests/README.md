# Tests

Repository-level test suites that span multiple apps/services.

- [`e2e/`](e2e/README.md) — end-to-end workflow validation (the Sprint 4.3.1
  release gate). A single black-box test that drives the full case lifecycle
  from authentication through the document pipeline to the Mission Control
  dashboard, against a running stack.

Component-level tests live with their app (for example `apps/api/tests/`).
