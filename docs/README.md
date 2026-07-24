# Documentation

Hub for product, engineering, and operations docs for Ultimate Credit Repair LLC (Verdin Credit Platform).

**Current release:** [v27.0.0](release-notes/v27.0.0.md)

## Start here

| Need                       | Document                                                                    |
| -------------------------- | --------------------------------------------------------------------------- |
| What shipped / what’s next | [Roadmap](roadmap/README.md)                                                |
| Capability readiness       | [Capability matrix](governance/capability-matrix.md)                        |
| Local development          | [Developer guide](developer-guide.md)                                       |
| HTTP API                   | [API reference](api/reference.md) · [Authentication](api/authentication.md) |
| Deploy / pilot             | [Deployment guide](deployment/guide.md)                                     |
| Why we built it this way   | [Architecture](architecture/README.md) · [ADRs](adr/README.md)              |
| Implementation decisions   | [Engineering changelog](engineering/changelog.md)                           |
| Release notes              | [release-notes/](release-notes/)                                            |

## Governance & delivery

| Document                                                                   | Purpose                           |
| -------------------------------------------------------------------------- | --------------------------------- |
| [Governance hub](governance/README.md)                                     | Lifecycle, release cadence, links |
| [Version 27.0 scope](governance/version-27.0-scope.md)                     | Latest signed-off phase           |
| [Version 27.0 checklist](development/version-27.0-completion-checklist.md) | Slice tracker                     |
| [Engineering changelog](engineering/changelog.md)                          | Implementation decisions          |

## Guides

| Guide                                          | Purpose                                              |
| ---------------------------------------------- | ---------------------------------------------------- |
| [Dispute workflow](guides/dispute-workflow.md) | Staff path: import → compare → letters → mail export |

## Quality & tests

| Document                            | Purpose                                 |
| ----------------------------------- | --------------------------------------- |
| [Quality hub](quality/README.md)    | Performance / security / coverage notes |
| [Repo tests](../tests/README.md)    | E2E + fixture corpus overview           |
| [E2E suite](../tests/e2e/README.md) | Black-box lifecycle tests               |

## Packages of note

| Package                                                       | README                                                                      |
| ------------------------------------------------------------- | --------------------------------------------------------------------------- |
| Credit report parsers (Experian / EQ / TU / ACR / IdentityIQ) | [`packages/report-parsers/README.md`](../packages/report-parsers/README.md) |
