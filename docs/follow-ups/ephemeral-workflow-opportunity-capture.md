# Ephemeral Workflow Opportunity Capture

Status: Follow-Up Capture

## Purpose

Design a lightweight durable capture path for workflow opportunities discovered
inside active sessions, especially when the current change set should not absorb
the work immediately.

## Captured Requirements

- Capture the smallest durable item that preserves the opportunity without
  turning it into active scope.
- Route the item to a local follow-up, issue, queued plan, or backlog according
  to repo policy and available control surfaces.
- Record source context, operator intent, affected workflow, urgency,
  dependencies, and expected future owner.
- Avoid assuming a particular harness, GitHub issue tracker, side-chat feature,
  subagent system, or programming language.
- Provide a recovery path when issue tooling is unavailable.

## GitHub Issue Projection

Projected follow-up issue:

- [#9](https://github.com/nisavid/agent-armory/issues/9): Engineer Ephemeral
  Workflow Opportunity Capture.

This capture remains local source material until
[#10](https://github.com/nisavid/agent-armory/issues/10) decides whether to
retain, consolidate, or retire the Seed-era bookkeeping now that active
tracking lives in GitHub Issues.
