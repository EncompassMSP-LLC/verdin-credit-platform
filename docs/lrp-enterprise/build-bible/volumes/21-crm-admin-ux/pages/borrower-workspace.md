# Page spec — Borrower workspace

| Field       | Value                            |
| ----------- | -------------------------------- |
| Page name   | Borrower workspace               |
| Route       | `/crm/borrowers/:id`             |
| Volume      | 21                               |
| Status      | `ready-for-build`                |
| Actors      | Case manager, reviewer, ops lead |
| Permissions | Case read/write by role          |

## 1. Purpose

Single pane of glass to run a borrower’s readiness file: profile, reports, findings, score, tasks, docs, disputes, partner status, messages.

## 2. Entry / exit

- Entered from: list, pipeline, referrals
- Navigates to: document viewer, dispute review, partner pages

## 3. Layout

**Header:** name, stage, assignee, band, partner badges  
**Tabs (draft):** Overview · Reports/Analysis · Score · Tasks · Documents · Disputes · Partner · Timeline · Messages

## 4. Fields (overview)

| ID             | Label            | Type      | Required | Source    | Validation  | PII |
| -------------- | ---------------- | --------- | -------- | --------- | ----------- | --- |
| stage          | Stage            | enum      | y        | case      | transitions | N   |
| assignee_id    | Assignee         | uuid      | n        | case      | —           | N   |
| readiness_band | Band             | enum/null | n        | readiness | —           | N   |
| next_check_in  | Next check-in    | date      | n        | case      | —           | N   |
| flags          | Compliance flags | list      | n        | case      | —           | N   |

Analysis / dispute sub-panels follow Vol 22 + SOP-06.

## 5. Actions

| ID              | Control              | Result         | API     | Audit     | Errors |
| --------------- | -------------------- | -------------- | ------- | --------- | ------ |
| save_stage      | Update stage         | PATCH case     | **yes** | 409       |
| run_analysis    | Queue analysis       | POST analysis  | **yes** | 409 busy  |
| publish_score   | Publish score        | POST readiness | **yes** | gate fail |
| draft_dispute   | Start dispute draft  | POST letter    | **yes** | —         |
| approve_dispute | Approve send         | POST approve   | **yes** | 403       |
| record_send     | Record filed/sent    | POST send      | **yes** | —         |
| invite_portal   | Send portal invite   | POST invite    | yes     | —         |
| partner_update  | Post partner note    | POST note      | yes     | —         |
| request_export  | Prep package         | POST export    | **yes** | —         |
| view_as         | View borrower portal | support mode   | **yes** | —         |

**Forbidden actions on this page:** one-click unsupervised bureau API file; “auto-approve all disputes.”

## 6. States

Loading / 404 / partial analysis / conflict on stale edit

## 7. Compliance copy

Persistent advisory chip; dispute panel states “Staff-mediated — human approval required before send.”

## 8. Analytics events

`crm_borrower_view` · `crm_analysis_queue` · `crm_score_publish` · `crm_dispute_approve`

## 9. Open questions

- [x] Mobile IA → **tabs collapse to accordion under `md`**
- [ ] Exact dispute state machine vs platform letters module (map in first E5 slice)
