# Stage 5 — Cursor Development

**Goal:** Implement only from approved Bible volumes.

## Rules

1. No feature PR without a Bible citation (`Vol NN §…`).
2. Prefer small vertical slices that match one page or one API group.
3. Existing `apps/lrp-web` / API code is **reference** until a volume marks it `keep` / `refactor` / `replace`.
4. Compliance guardrails never relaxed for velocity.
5. Update the Bible when reality forces a change — code does not silently diverge.

## Backlog home

[Vol 25 — Implementation backlog](../build-bible/volumes/25-implementation-backlog/) — epic order + Cursor prompt starter drafted.

## Gate before coding

Promote cited Vol 19–24 sections to `ready-for-build` (founder/compliance). Until then, Bible drafting and review only.
