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
| 7     | Prioritize LRP-208A / LRP-209A for V1.1 | Product        | ✅ Ranked             | [`lrp-platform-v1.1-completion-checklist.md`](lrp-platform-v1.1-completion-checklist.md)           |

## Deferred product (V1.1 candidates)

| ID       | Slice                                                          |
| -------- | -------------------------------------------------------------- |
| LRP-208A | Evidence Vault, document-to-issue association, action timeline |
| LRP-209A | Unwanted-call complaint workflow and follow-up tracking        |
