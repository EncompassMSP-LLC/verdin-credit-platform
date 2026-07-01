# Agent Sprint Loop (Version 4.5)

Hands-off workflow: **implement slice → open PR → CI → auto-merge → next slice**.

## One-time GitHub setup (repo admin)

1. Open **Settings → General → Pull Requests**
2. Enable **Allow auto-merge**
3. Under **Branch protection** for `main`:
   - Require status checks (CI workflow)
   - Do **not** require manual approval if you want fully unattended merges
   - Allow GitHub Actions to bypass if needed for automation merges

After merge of `.github/workflows/enable-auto-merge.yml`, every non-draft PR from `feature/*` → `main` is queued for squash auto-merge when CI passes.

Agents should also run `gh pr merge --auto --squash` immediately after `gh pr create` (see `.cursor/rules/version-45-sprint-loop.mdc`).

## Cursor Automation setup

Import the draft in [`cursor-automation-sprint-loop.yaml`](./cursor-automation-sprint-loop.yaml):

1. Open **Cursor → Automations → Create**
2. Trigger: **GitHub → Pull request merged** on `EncompassMSP-LLC/verdin-credit-platform`
3. Enable tools: **Shell** (or repo checkout), **GitHub CLI** if available
4. Paste the prompt from the YAML file (or import prefill if your Cursor build supports it)
5. Use **Cloud Agent** if you want runs when your machine is off
6. Save and enable

### What the automation does

When any PR merges to `main`, the agent:

1. Syncs `main`
2. Picks the next Version 4.5 slice
3. Implements with tests + api-client + docs
4. Verifies, commits, pushes, opens PR
5. Enables auto-merge
6. Stops only on blockers (CI, ambiguous requirements, permissions)

### Manual fallback

If Automation is disabled, send:

> Execute next steps

The project rule `.cursor/rules/version-45-sprint-loop.mdc` applies the same loop.

## Local `/loop` alternative

For local-only polling while Cursor is open:

```text
/loop 10m Check if main advanced on EncompassMSP-LLC/verdin-credit-platform; if a new merge landed, execute the Version 4.5 sprint loop (sync main, next slice, PR, auto-merge).
```

Cloud Automation on **PR merged** is preferred over polling.

See also [`version-4.5-completion-checklist.md`](./version-4.5-completion-checklist.md) for the full 4.5 exit path and Phase 2 queue.

## Troubleshooting

| Issue                    | Fix                                          |
| ------------------------ | -------------------------------------------- |
| Auto-merge not offered   | Enable **Allow auto-merge** in repo settings |
| PR stuck waiting         | CI failing — fix checks                      |
| Automation never runs    | Confirm trigger repo/branch; use Cloud Agent |
| `gh` not found (Windows) | `C:\Program Files\GitHub CLI\gh.exe`         |
