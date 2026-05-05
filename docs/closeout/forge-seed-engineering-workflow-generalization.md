# Forge Seed Engineering Workflow Generalization Addendum

Status: Open Capture

This addendum extends the [Forge Seed Workflow Lessons](forge-seed-workflow-lessons.md).
It captures generalizable workflow patterns, antipatterns, and equipment ideas
that emerged while refining the human-facing documentation spine, closeout
evidence, validation contracts, review loops, and publication state for the
Forge Seed.

The later Portable Agentic Engineering Workflow Equipment and Reflection and
cognition equipment stories should ingest this addendum as source material.
Treat it as reflection evidence, not as final equipment design.

## Core Pattern

The session repeatedly converged on one portable workflow shape:

1. Start from the operator's current intent, not from an old plan snapshot.
2. Locate the durable repo surface that should own the new information.
3. Make the smallest change that preserves the larger system contract.
4. Rerun the owning validation gate after every substantive change.
5. Refresh evidence whose truth depends on the current tree.
6. Ask for review when the change affects cross-boundary claims or closeout
   evidence.
7. Remove transient process noise before publication while preserving durable
   status, risks, and next actions.

This shape is independent of the Forge domain. It can apply to package work,
application code, infrastructure, docs, security, incident response, release
work, or repo operations whenever agents perform assigned work under human
initiative authority.

## Generalizable Patterns

### Intent And Scope Control

- Treat new operator input as live intent that can refine or supersede the
  current plan, even late in closeout.
- Separate the stated task from the broader story. Handle the immediate request,
  then update downstream evidence only where the request actually changes it.
- Keep the latest correction concrete. The useful unit is often a wording rule,
  ordering rule, audience boundary, or publication boundary, not a broad
  preference statement.
- Preserve human initiative authority while allowing agents to execute
  autonomously within known policy, validation, and control boundaries.

### Audience And Surface Placement

- Route information by reader objective before choosing a file.
- Keep public or human-facing docs free of maintainer-only process history
  unless the reader needs that history to decide or act.
- Keep agent-facing docs terse, durable, and discoverable before task scouting.
- Put technical terms where precision helps. In casual human-facing docs,
  introduce domain language only after the reader has enough context to care.
- Prefer linked progressive disclosure over one overloaded document.

### Evidence Discipline

- Distinguish durable evidence from session evidence. Validation output,
  review results, source digests, and publication state can be durable; raw scan
  bundles, chat-only reasoning, and review-cycle narration usually are not.
- When evidence depends on the exact tree, treat every tracked edit as capable
  of making that evidence stale.
- Preserve enough status for a future agent to continue safely: what passed,
  what remains pending, which branch or issue is involved, and which surface is
  source of truth until publication catches up.
- Avoid storing entire review histories when the durable output is a clean
  review status and a current risk boundary.

### Validation And Review

- Make validators check behaviorally important contracts, not incidental prose
  shape.
- When a cleanup reveals that validation encodes noise, change the validation
  contract and tests together.
- Run the smallest relevant test first when changing a validation contract, then
  run the full deterministic gate before closeout.
- Use review-until-clean for changes that alter story-level coherence,
  projection surfaces, security claims, validation contracts, or public
  expectations.
- Treat review feedback as technical input to verify, not as text to accept
  performatively.

### Source And Projection Handling

- Keep source-derived claims traceable without preserving raw handoff material
  indefinitely.
- Separate repo-file projection from external publication. Drafts can be ready
  while issues, pull requests, releases, or handoffs remain unpublished.
- Do not describe pending publication as completed work. Keep placeholders that
  must be filled at publication time, such as commit SHA fields, visibly
  unresolved and validation-aware.
- After projection text changes, rerun projection consistency and any final
  closeout gate that depends on the projected surface.

### Security And Control

- Treat docs-only security non-applicability as a conclusion that may still need
  a narrow refresh when docs change trust, control, installation, or
  publication claims.
- Keep raw scan outputs out of durable docs unless deliberately promoted with a
  scope, staleness boundary, and review status.
- Represent approval, autonomy, side effects, secrets, and local host behavior
  as control concerns, not as narrative warnings scattered through prose.

### Git And Publication Hygiene

- Commit only after validation and review evidence match the current tree.
- Keep the working tree clean after commit and push when the user asks for
  publication.
- Respect branch-push pauses and side quests as real operating state; record the
  next external action rather than silently continuing.
- Use fix-forward history for published or reviewable branches unless the
  operator explicitly asks for destructive history editing.

### Human-Agent Collaboration

- The human should be able to provide a small prompt because repo equipment
  carries the standing workflow.
- The agent should surface only meaningful boundaries: missing policy, missing
  control surface, non-dismissible intent uncertainty, or required human access.
- Intermediate updates should explain what is being checked or changed without
  turning process into permanent documentation.
- Side-thread edits are useful, but the main worker remains responsible for
  integration, validation, review, commit, and publication.

## Generalizable Antipatterns

- Letting maintainer or implementer perspective leak into docs meant for
  prospective users.
- Treating capitalized project vocabulary as reader value before the reader
  understands the problem it solves.
- Preserving review-cycle narratives after the durable result is just a clean
  review status.
- Updating closeout evidence without refreshing dependent source-retirement
  stamps.
- Letting validators require incidental headings or phrases that no longer
  serve the document.
- Treating untracked files as outside the change unless the final work product
  explicitly accounts for them.
- Asking the human to remember workflow rules that should be encoded in repo
  policy, skills, templates, configs, or validators.
- Deferring first capture of workflow insights until a future story starts.
  Capture during the work; engineer later.
- Equating a source handoff, teaching example, blueprint, implemented
  candidate, and published equipment.
- Using a broad review as a substitute for targeted deterministic validation,
  or using passing tests as a substitute for cross-boundary coherence review.

## Equipment Needed For Prompt Reduction

To reduce a future prompt to something like "Use this repo's Agent Ops workflow
to do the requested work," a repo needs equipment that projects the following
capabilities without relying on the operator's memory.

### Always-Loaded Orientation

- A short repo role statement.
- The autonomy model and escalation boundaries.
- Pointers to triggered workflow equipment, not full workflow dumps.
- Current publication or closeout state when the repo is mid-story.

### Workflow Router

- A route from task type and risk to the right workflow: small edit, docs
  refresh, implementation, security-sensitive change, release, incident,
  external projection, side-thread support, or closeout.
- Rules for when to escalate, when to proceed autonomously, and when to spawn or
  reuse side work.
- A right-sizing model so a typo fix does not receive the same ceremony as a
  cross-boundary architecture change.

### Intent Model Refresh

- A lightweight gate that rereads recent operator input, accepted plan/spec/ADR
  changes, review dispositions, and observed corrections before downstream
  closeout.
- An Intent Alignment Check for story quality review.
- A rule to ask the operator only when evidence creates real uncertainty that
  cannot be resolved from repo state.

### Change-Set Closeout

- Security closeout equipment.
- Documentation closeout equipment.
- Validation gate registry.
- Projection consistency check.
- Cross-Boundary Coherence review.
- Story Quality review.
- Publication readiness check.

### Evidence And Source Handling

- A source-disposition ledger pattern for source-heavy work.
- A tree-dependent stamp pattern that avoids self-reference.
- Rules for classifying raw artifacts, durable summaries, external projection
  drafts, and transient scratch evidence.
- A validator or checklist that catches stale digests, pending placeholders, and
  host-local paths in durable projection surfaces.

### Documentation Equipment

- Audience mapper for human-facing, agent-facing, hybrid, reference,
  explanation, tutorial, how-to, closeout, and projection docs.
- Human-facing doc hone that removes maintainer-only clutter.
- Agent-facing doc hone that keeps durable instructions narrow and scoutable.
- Style and terminology checks that can distinguish casual public prose from
  technical docs.

### Review Equipment

- Review-until-clean loop with labeled cycles.
- Reviewer prompts for docs, validation contracts, security, coherence, story
  quality, and publication readiness.
- Reception rules that require verifying reviewer feedback before implementing
  it.
- A compact durable review-status format that avoids carrying review history
  into closeout or projection docs.

### Side-Thread Hand-Back

- A default non-mutating side-thread mode.
- A narrow-edit exception with explicit ownership and validation implications.
- A hand-back template that records provenance, intent, files touched, findings,
  and integration requirements.
- A rule that the main worker owns final integration and publication.

### Workflow Opportunity Capture

- A way to notice recurring session practices that deserve durable equipment.
- A capture surface that records the pattern, pressure cases, possible
  equipment, and what not to promote yet.
- A follow-up route that turns capture into engineered equipment later.

### Reflection Finding Capture

- A durable issue-tracked form for manually produced reflection findings.
- A route from observed friction or insight to the narrowest owning equipment
  story, including generic Reflection and cognition equipment when no narrower
  owner exists.
- A privacy and disclosure classification before session context is projected
  into public or shared tracking surfaces.

## Portable Equipment Architecture

The workflow should be built as portable Agent Equipment, not as repo-specific
policy prose.

### Core Package

- A domain-neutral workflow specification.
- A small always-loaded policy block.
- Triggered skills or runbooks for each workflow phase.
- Templates for closeout, reviews, projection drafts, hand-backs, and source
  disposition.
- A validation contract that repos can extend.
- Pressure-scenario tests.

### Repo Adapter

- A repo-local config file that declares autonomy level, issue tracker, review
  expectations, validation commands, publication rules, and security closeout
  requirements.
- A docs map that names the repo's human-facing, agent-facing, source,
  closeout, and projection surfaces.
- Optional domain vocabulary that can be loaded without changing the generic
  workflow core.

### Harness Adapter

- A harness capability record for approvals, sandboxing, subagents, MCP/tools,
  hooks, browser use, git operations, and notification surfaces.
- Projection rules for how the same workflow appears in Codex, Claude Code,
  Cursor, Hermes Agent, OpenCode, OpenClaw, or another harness.
- Degradation behavior when a harness lacks a control surface. Missing controls
  should trigger advisory mode, escalation, or a different validation route.

### Human UX

- A short onboarding doc for people adding the equipment to a repo.
- A minimal invocation prompt.
- A configuration wizard or checklist for ownership, autonomy, validation,
  review, publication, and artifact-retention choices.
- Examples showing tiny, medium, and high-risk tasks so humans can see how the
  ceremony right-sizes.

### Agent UX

- Zero-scout pointers from the always-loaded policy.
- Progressive disclosure from orientation to task-specific workflow.
- Explicit return contracts for escalations.
- Deterministic validation commands and expected outputs.
- Compact closeout and hand-back formats.

## Pressure Scenarios

The post-Seed equipment story should prove the workflow under these scenarios:

- A one-line documentation fix with no security or projection impact.
- A public README rewrite that changes user expectations.
- A source-heavy migration with licensing and provenance concerns.
- A code change that touches executable side effects, secrets, or permissions.
- A release or PR where external publication must pause after branch push.
- A side-thread review that finds useful edits while a main worker owns the
  change set.
- A validation contract that encodes incidental prose and needs to be corrected.
- A repo without the operator's user-global skills installed.
- A harness without subagents, browser control, or approval gates.
- A domain with unfamiliar terminology where the generic workflow must not
  overfit to Forge language.

## Minimal Future Prompt Target

The equipment should make the following prompt sufficient for ordinary work:

```text
Use this repo's Agent Ops workflow to handle <task>. Right-size the ceremony,
update durable surfaces, validate, review if required, and stop only at a real
human decision or unavailable control surface.
```

For high-risk or publication work, the prompt should only need to add the
specific objective and any unusual operator preference. The repo equipment
should supply the rest: discovery routes, autonomy boundaries, validation
commands, review gates, evidence handling, and closeout shape.

## Open Design Questions

- Which parts belong in Agent Ops core and which belong in an engineering
  workflow extension?
- What is the smallest always-loaded policy that still reliably routes agents
  to the right triggered equipment?
- How should a repo declare that a validation command is advisory, required,
  expensive, destructive, or publication-blocking?
- How should review-until-clean cycles be recorded so agents can continue work
  without publishing review-history noise?
- What portable schema can describe side-thread ownership, hand-back, and
  integration obligations across harnesses?
- How should the workflow equipment detect when right-sizing has become either
  under-disciplined or performatively ceremonial?
