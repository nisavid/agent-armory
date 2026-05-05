# Side-Thread Hand-Back Workflow

Status: Follow-Up Capture

## Purpose

Specify the Agent Ops workflow for side conversations that inspect, advise, or
make narrow operator-requested edits while a main worker owns an active change
set.

## Captured Requirements

- Define the default side-thread boundary as non-mutating unless the operator
  explicitly requests a narrow edit.
- Define when a side thread may make a narrow tracked edit and how it avoids
  conflicting with the main worker's ownership.
- Require a hand-back note that records provenance, operator intent, files
  touched, review and validation implications, and commit guidance.
- Preserve any reflection finding produced by the side thread, including whether
  it is integration evidence for the main worker or source material for future
  cognition equipment.
- Keep the main worker responsible for integration, validation, review, commit,
  PR handling, and final closeout.
- Treat the side-thread handoff as source material for the future engineering
  story, not as an isolated side-thread commit.

## GitHub Issue Projection

Projected follow-up issue:

- [#7](https://github.com/nisavid/agent-armory/issues/7): Specify Side-Thread
  Hand-Back workflow.
- [#25](https://github.com/nisavid/agent-armory/issues/25): Engineer
  Reflection and cognition equipment. Side-thread reflection findings are source
  material for that later story when they expose reusable agent-behavior
  adjustments.

This capture remains local source material until
[#10](https://github.com/nisavid/agent-armory/issues/10) decides whether to
retain, consolidate, or retire the Seed-era bookkeeping now that active
tracking lives in GitHub Issues.
