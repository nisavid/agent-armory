# Forge Seed Workflow Lessons

Status: Open Capture

This capture remains conceptually open through PR creation, review, merge,
cleanup, external reconciliation, and final hand-back. Tracked edits after the
final source-retired stamp stales that stamp. Any tracked update that should be
part of the stamped Forge Seed state must rerun source-retired pre-stamp,
commit a replacement final source-retired checkpoint, and pass detached
validation before publication.

## Captured Lessons

- The branch-push pause is a valid operator boundary only when projection drafts
  and final hand-back explicitly state which external actions remain pending.
- Source-retirement stamps must avoid self-reference. The Forge Seed uses a
  placeholder-normalized canonical tree digest.
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
