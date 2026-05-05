# Forge Seed Workflow Lessons

Status: Open Capture

This capture remains conceptually open through PR creation, review, merge,
cleanup, external reconciliation, and final hand-back. Source retirement records
the stable fact that raw source inputs are retired and the disposition ledger is
complete; it does not require a commit-specific digest or timestamp.

## Captured Lessons

- The branch-push pause is a valid operator boundary only when projection drafts
  and final hand-back explicitly state which external actions remain pending.
- Source-retirement stamps must avoid self-reference. The Forge Seed records
  `source_retired: true` as the durable closeout fact instead of committing a
  digest that changes whenever the tree changes.
- Raw security or scan reports are instance-scoped unless deliberately promoted
  into a neutral durable project path with scope, review status, and staleness
  boundaries.
- Persistent specs and tests should define current desired construction, not
  enumerate discarded names or non-goals unless contrast is itself intended
  behavior.

## Linked Addenda

- [Engineering workflow generalization](forge-seed-engineering-workflow-generalization.md):
  generalizes the Forge Seed session workflow into portable equipment design
  inputs for the post-Seed engineering workflow story.
