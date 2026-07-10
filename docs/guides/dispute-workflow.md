# Dispute workflow guide

Step-by-step guide for staff using **Ultimate Credit Repair LLC** to import credit reports, find cross-bureau problems, prepare dispute letters, and mail them.

For local pilot setup, see [local-docker-pilot.md](../deployment/local-docker-pilot.md).

---

## Overview

| Phase               | Where in the app                        | Outcome                                   |
| ------------------- | --------------------------------------- | ----------------------------------------- |
| 1. Set up case      | **Cases**                               | Client case ready for reports             |
| 2. Import reports   | **Import credit report**                | Parsed Experian, Equifax, TransUnion data |
| 3. Compare bureaus  | **Case → Cross-bureau discrepancies**   | Actionable tradeline issues               |
| 4. Prepare disputes | **Prepare all disputes** or per-row     | Accounts + letter drafts created          |
| 5. Review & mail    | **Case → View accounts → Saved drafts** | Mail-ready PDF + labels                   |
| 6. Track response   | **Account → Dispute workflow**          | Status through CRA response               |

---

## Phase 1 — Create or open a case

1. Log in at **http://localhost:8080** (pilot: `owner@verdin.demo` / `changeme123`).
2. Go to **Cases** and open an existing case or create one.
3. Confirm **client name** is correct on the case (used on every letter).
4. Optionally add **client email** (helps evidence checklist completeness).

**Tip:** Case stage `dispute_preparation` is set automatically as you work through disputes.

---

## Phase 2 — Import bureau credit reports

You need **at least two different bureaus** on the same case for cross-bureau comparison.

1. On the case page, click **Import credit report** (or use **Imports** in the sidebar).
2. Select the **case**.
3. Upload the PDF for one bureau (Experian, Equifax, or TransUnion).
4. Repeat for the other bureau(s).
5. Wait for the worker to parse documents (refresh the document or case page).

**Verify parsing**

- Open each document → **Parsed credit report** should show tradelines (not “Partial parse”).
- On the case page, **Tradeline report history** shows per-bureau snapshots when multiple reports exist.

---

## Phase 3 — Review cross-bureau discrepancies

1. On the **case detail** page, scroll to **Cross-bureau discrepancies**.
2. Review the summary badges:
   - **actionable** — tradelines worth disputing
   - **missing** — account on one bureau but not others
   - **balance** / **status** — bureaus disagree on amounts or status
3. Read each row’s **Recommended action** and **By bureau** columns.

**What “missing from bureau” means**

The same debt may appear under different creditor names on different bureaus. The matcher may flag a tradeline as “missing” on a bureau when names don’t align. Always review before bulk-preparing.

---

## Phase 4 — Prepare dispute accounts and letter drafts

### Option A — Bulk (all actionable items)

1. Click **Prepare all disputes (N)**.
2. Wait for the green success message.
3. Click **View case accounts →** to open the account list.

### Option B — One tradeline at a time

1. In the discrepancies table, click **Create account & letter** on a row.
2. Click **Open account** after success.

**What this creates**

- One **credit account** (tradeline) per discrepancy
- One **dispute letter draft** per account (`status: draft`)
- Account **dispute status** set to `ready_for_dispute`

---

## Phase 5 — Review, export, and mail

For **each account**:

1. **Cases → View accounts** → click the **creditor name**.
2. Scroll to **Dispute draft preview** and **Saved drafts**.
3. Click **View details** on the draft to read the full text.
4. Fix any **Missing evidence** warnings on the account/case before mailing.

### Export types

| Button                        | Use for                                                                    |
| ----------------------------- | -------------------------------------------------------------------------- |
| **Download mail packet**      | **Primary** — 3-page PDF: labels + FCRA letter + mailing checklist         |
| **Download all mail packets** | ZIP of every creditor's mail packet on the case (case discrepancies panel) |
| **Review PDF**                | Internal staff copy with evidence checklist and compliance notes           |

Each **mail packet** PDF contains:

1. **Page 1 — Labels:** MAIL TO (bureau address), RETURN (your office), CONSUMER
2. **Page 2 — Letter:** FCRA § 611 letter with consumer address, bureau address, disputed items, signature block, return address
3. **Page 3 — Checklist:** ID, proof of address, report page, certified mail reminder, readiness warnings

### Before you mail

1. Set your **return address** in deployment config (`.env.production`):

   ```env
   DISPUTE_RETURN_NAME=Ultimate Credit Repair LLC
   DISPUTE_RETURN_ADDRESS_LINE1=Your street address
   DISPUTE_RETURN_ADDRESS_LINE2=City, ST ZIP
   ```

2. Rebuild/restart the API after changing env vars.
3. Print **Mail-ready letter** and have the **consumer sign**.
4. Print **Mailing labels** (or address the envelope manually).
5. Attach:
   - Copy of government-issued ID
   - Proof of current mailing address
   - Credit report page showing the disputed tradeline
6. Mail via **certified mail, return receipt** (recommended; tracked outside the app today).

**CRA mailing addresses** (included automatically on mail-ready exports):

| Bureau     | Address                                                   |
| ---------- | --------------------------------------------------------- |
| Experian   | P.O. Box 4500, Allen, TX 75013                            |
| Equifax    | P.O. Box 740256, Atlanta, GA 30374-0256                   |
| TransUnion | Consumer Dispute Center, P.O. Box 2000, Chester, PA 19016 |

**Furnisher disputes:** use **Mail-ready letter** with recipient type `furnisher`; verify the creditor’s dispute address before mailing.

---

## Phase 6 — Approve, mark sent, and track response

After staff review:

1. **Create review task** (optional) — assigns review in **Tasks**.
2. Move letter to **review** status (via review workflow / task completion).
3. **Approve letter** — required before marking sent.
4. **Mark as sent** — updates account dispute status and creates follow-up tracking.

On the account **Dispute workflow** card:

| Action                             | When                                                    |
| ---------------------------------- | ------------------------------------------------------- |
| **Mark awaiting response**         | After mailing; starts the response window               |
| **Verified / Corrected / Deleted** | When CRA response is recorded                           |
| Overdue escalation                 | Automatic task if investigation passes statutory window |

Check **Dashboard** and **Tasks** for letters in review and overdue investigations.

---

## Quick reference — where things live

| I want to…                       | Go to…                                               |
| -------------------------------- | ---------------------------------------------------- |
| Import PDF reports               | Case → **Import credit report**                      |
| Compare bureaus                  | Case → **Cross-bureau discrepancies**                |
| Bulk-create letters              | **Prepare all disputes**                             |
| See all tradelines on a case     | Case → **View accounts**                             |
| Read / export letters            | Account → **Saved drafts**                           |
| Mail-ready PDF + labels          | Account → **Mail-ready letter** / **Mailing labels** |
| Track dispute status             | Account → **Dispute workflow**                       |
| Same-bureau history (re-imports) | Document or case → **Tradeline report history**      |

---

## Letter lifecycle (status)

```
draft → review → approved → sent
         ↓
        void (cancel in-flight letter)
```

- **draft** — just created; safe to edit account fields and re-export.
- **review** — staff reviewing evidence and letter text.
- **approved** — cleared to mail.
- **sent** — recorded as mailed; follow up for CRA response.

---

## Troubleshooting

| Problem                               | What to do                                                                     |
| ------------------------------------- | ------------------------------------------------------------------------------ |
| No cross-bureau panel                 | Upload at least **two bureau reports** on the case                             |
| **Prepare all disputes** does nothing | Hard-refresh; check for red error banner (API may have failed)                 |
| Empty consumer address on labels      | Address is pulled from report metadata when available; otherwise fill manually |
| Return address placeholder            | Set `DISPUTE_RETURN_ADDRESS_*` in `.env.production`                            |
| Furnisher address says “verify”       | Look up creditor dispute address; mail-ready export cannot guess it            |
| Partial parse on import               | Re-parse document; see parser/deployment docs                                  |

---

## What the app does _not_ do yet

- Physical mailing or postage
- Certified mail tracking numbers
- Bulk ZIP download of all mail-ready letters for a case
- Automatic furnisher address lookup
- Autonomous bureau filing (compliance-gated; deferred)

---

## Related docs

- [API reference — accounts & dispute letters](../api/reference.md)
- [Local Docker pilot](../deployment/local-docker-pilot.md)
- [Account intelligence](../sprint-2/account-intelligence.md)
