# Agentic Engineering Workflow Seed Closeout Addendum

Status: Handoff Addendum

This addendum captures workflow lessons that emerged after the original Agentic
Engineering Workflow Equipment handoff was written and before the Framework Seed
is complete. It is source material for the future Portable Agentic Engineering
Workflow Equipment story, not canonical Framework doctrine.

This file is the capture for those lessons. The later post-Seed story should
ingest, challenge, and engineer the captured material; it should not be the first
place these lessons are recorded.

Keep this addendum current through full Framework Seed completion. For this
capture, full completion means the Seed branch has been pushed, the PR lifecycle
has run, the Seed has been merged, external issue and PR surfaces have been
reconciled with repo-file projections, merge cleanup has completed or been
explicitly deferred, and the final hand-back records that state. The capture
window includes final local validation, closeout reviews, issue projection,
branch push, PR creation, PR review orchestration, merge, and merge cleanup. If
those steps expose new insights, guardrails, policies, techniques, failure
modes, or harness-specific constraints, append them before treating the Seed as
fully closed.

If the operator explicitly holds or cancels the Seed instead of merging it,
continue capture through the hold or cancellation hand-back. Record the
unmerged state directly; do not describe it as full Seed completion.

If a session pauses after branch push and before PR creation, do not treat the
capture as complete. The hand-back should say that this addendum remains open
through the PR, merge, and cleanup lifecycle.

## Completion-Window Capture

The future Portable Agentic Engineering Workflow Equipment story should ingest
not only this addendum's current contents, but also any additions made during
the remaining Seed closeout and PR lifecycle.

Capture likely belongs here when it concerns:

- how PR and issue orchestration should interact with repo-file projections;
- when review-bot feedback should reopen documentation, security, validation,
  projection, Cross-Boundary Coherence, or Story Quality gates;
- how branch push, PR creation, merge, or cleanup changes agent handoff and
  final-response obligations;
- which harness control surfaces made the intended workflow easier, weaker, or
  unavailable;
- which closeout steps proved too vague, too brittle, or too expensive for the
  risk they addressed.

Do not wait for the post-Seed story to remember these observations. Record them
as they occur, then let the post-Seed story challenge and engineer them.

## Subagent Review Availability

When the harness can provide subagent reviewers, local in-session review is only
scratch work. It is not an adequate substitute for required subagent review.

If the agent is at the thread limit, close completed subagents before accepting
reduced review quality. Review capacity management is part of the workflow, not
an exceptional cleanup task.

## Closeout Gate Ordering

Story-level closeout needs a defined gate order. Subordinate security and
documentation closeouts happen before story-level Cross-Boundary Coherence and
Story Quality reviews.

Projection needs two stages:

- prepare issue, PR, release, and handoff drafts before Cross-Boundary Coherence
  review, or record a pending-projection rationale;
- publish or update external surfaces only after final validation confirms the
  reviewed evidence.

If a published issue, PR, release, or handoff differs materially from the
reviewed draft, correct the published surface and run a narrow Cross-Boundary
Coherence review for that projection surface.

## Recursive Closeout Refresh

Closeout gates are interdependent. A fix must rerun the gate that owns the
changed surface:

- security changes rerun or update security closeout;
- documentation changes rerun or update documentation closeout;
- validation changes rerun deterministic tests and validators;
- PRD, spec, or plan changes rerun acceptance and projection checks;
- issue, PR, release, or handoff projection changes rerun projection
  consistency checks.

Bookkeeping-only updates, such as recording the latest clean review cycle, do
not reopen the full loop unless they change substantive claims.

## Security Evidence Freshness

Security closeout evidence must describe the current final diff, not a prior
scan snapshot. The scan scope needs to include committed changes, staged changes,
unstaged changes, and untracked intended files.

Security phase evidence should reflect actual phase applicability. If finding
discovery produces no technically plausible candidates, validation and
attack-path analysis may be explicitly recorded as not separately run. If those
phases run, the closeout should record completion instead of forcing a skipped
phase sentence.

Re-validation counts in durable closeout evidence must match the current test
and validator run.

## Documentation Evidence Freshness

Documentation closeout evidence must include the full affected-doc scope, not
only the root README, root AGENTS file, and glossary. It should cover affected
canonical docs, plans, PRDs, ADRs, specs, templates, examples, security docs,
closeout docs, issue-tracker docs, and archived handoff material when stale
language searches reach it.

The latest clean review cycle in documentation closeout must be current after
security closeout and after any subsequent closeout-process edits.

Deferred post-Seed follow-ups belong in plan or handoff surfaces until the
corresponding story is actively designed. Do not promote them into always-loaded
policy, README success claims, PRD success criteria, or canonical Framework docs
early.

## Process Validation

Workflow equipment should validate process semantics, not only exact prose.
Exact required phrases can preserve critical terms, but structural checks are
needed for things like closeout gate order, projection correction paths, rerun
rules, and evidence freshness.

The Framework Seed validator grew from phrase checks toward structural checks
for Story Closeout gate order. Future portable workflow equipment should keep
that direction and avoid brittle wording-only gates where process shape matters.

## Plan-State Hygiene

Plans, closeout summaries, and review evidence must agree about what is complete.
If a closeout summary claims completion while the plan leaves its refresh step
unchecked, agents can start the next gate from stale evidence.

Checklists should be updated only when the referenced evidence is current, and
review fixes should update the plan's rerun instructions when they expose a new
gate dependency.
