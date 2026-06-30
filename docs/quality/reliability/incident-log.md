# Incident Log

**Purpose:** track reliability incidents, stabilization findings, and follow-up actions.

This is not an operations incident-management system. It is a lightweight engineering log for issues discovered during development, CI, stabilization, or release readiness reviews.

| Date       | Severity | Area   | Summary                                                  | Status | Follow-Up                                       |
| ---------- | -------- | ------ | -------------------------------------------------------- | ------ | ----------------------------------------------- |
| 2026-06-29 | Medium   | Worker | OCR job could run before document transaction committed. | Fixed  | See [`race-conditions.md`](race-conditions.md). |

## Entry Guidelines

- Record the symptom and root cause when known.
- Link to issues, PRs, commits, or follow-up docs when available.
- Use severity to communicate release risk, not blame.
- Prefer short entries with links over long postmortems unless the issue affected production.
