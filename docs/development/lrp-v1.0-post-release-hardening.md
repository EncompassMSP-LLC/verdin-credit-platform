# LRP V1.0 Post-Release Hardening Checklist

Controlled cycle after tag `lrp-platform-v1.0.0` — **not** a feature sprint.

| Order | Item                                    | Owner          | Status                | Evidence                                                                                           |
| ----- | --------------------------------------- | -------------- | --------------------- | -------------------------------------------------------------------------------------------------- |
| 1     | Security-officer sign-off               | Security / Eng | ☐ Ready for signature | [`lrp-v1.0-security-officer-signoff.md`](../quality/security/lrp-v1.0-security-officer-signoff.md) |
| 2     | Disaster-recovery runbook               | Ops / Eng      | ✅ Drafted            | [`lrp-v1.0-disaster-recovery-runbook.md`](../deployment/lrp-v1.0-disaster-recovery-runbook.md)     |
| 3     | Production smoke vs tagged release      | Eng / QA       | ☐                     | Runbook §5 against prod/staging                                                                    |
| 4     | Backup restore test (staging)           | Ops            | ☐                     | Runbook §8 log row                                                                                 |
| 5     | Monitoring / alert verification         | Ops            | ☐                     | Runbook §9                                                                                         |
| 6     | Release retrospective                   | Product / Eng  | ☐                     | Notes linked here                                                                                  |
| 7     | Prioritize LRP-208A / LRP-209A for V1.1 | Product        | ✅ Shipped in V1.1    | [`lrp-platform-v1.1.0`](../release-notes/lrp-platform-v1.1.0.md) · tag `lrp-platform-v1.1.0`       |

## Deferred product (V1.1 — shipped)

| ID       | Slice                                                   | Status  |
| -------- | ------------------------------------------------------- | ------- |
| LRP-208A | Evidence Vault document↔issue association               | ✅ #414 |
| LRP-208B | Case action timeline                                    | ✅ #415 |
| LRP-209A | Unwanted-call complaint workflow and follow-up tracking | ✅ #416 |

Optional timeline enrichments remain backlog-only (PB-011 / PB-012).
