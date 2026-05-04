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
- Keep the main worker responsible for integration, validation, review, commit,
  PR handling, and final closeout.
- Treat the side-thread handoff as source material for the future engineering
  story, not as an isolated side-thread commit.

## GitHub Issue Projection

When issue creation is blocked by a story pause, keep the follow-up in this
file, name the blocked projection surface in the handoff, and reconcile the
file with the issue tracker when the session resumes and issue tooling is
available.
