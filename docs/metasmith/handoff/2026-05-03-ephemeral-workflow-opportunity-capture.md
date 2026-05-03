# Ephemeral Workflow Opportunity Capture Handoff

Status: Handoff

This handoff captures side-conversation reflection on session-scoped workflow
constructs that may be valuable enough to promote into durable Agent Equipment.
It is not canonical Framework doctrine. A future post-Seed task should ingest
this document, challenge it against the then-current repo docs, and engineer the
useful parts through the full workflow.

## Source Context

During the Framework Seed, useful workflow ideas have appeared in ephemeral
places: chat instructions, side conversations, review loops, operator
corrections, temporary handoff notes, validation habits, and emergent operating
rules. Some of those ideas became durable repo policy or plans only because the
operator explicitly noticed the opportunity and asked for a side quest.

Without that operator prompt, similar discoveries can be lost at session end.
Future agents would then need the same behavior re-instructed, rediscovered, or
reconstructed from memory. The repository should eventually contain equipment
that helps agents notice these extraction opportunities and recommend an
appropriate durable handling path.

## Generalized Problem

An agent may encounter a session-scoped construct that has durable value:

- a workflow rule that keeps recurring across tasks;
- a side-thread boundary or hand-back pattern;
- a review or security practice that catches real defects;
- an operator preference that changes agent behavior;
- an escalation pattern that resolves authority cleanly;
- a validation habit that should become deterministic;
- a documentation placement rule that prevents future confusion;
- a reusable prompt, checklist, template, or pressure scenario.

The opportunity is not always a mandate to mutate the repo immediately. The
agent needs to classify the construct, estimate durability and risk, and surface
a right-sized recommendation.

## Opportunity Signals

Candidate signals include:

- repeated operator corrections that reveal a stable preference or policy;
- workflow steps that prevent defects or reduce ambiguity;
- ad hoc instructions that a future agent would need before scouting;
- side conversation outcomes that affect integration, review, validation, or
  closeout;
- temporary notes that name a future engineering story;
- review findings that imply a reusable validator, checklist, or template;
- security or privacy boundaries that should not rely on memory;
- instructions that are useful across repos but currently live only in chat;
- cases where a minimal future prompt would fail unless this context were
  preserved.

Signals should be treated as prompts for reflection, not automatic promotion.
The agent should ask whether the construct is durable, non-obvious, broadly
useful, and better captured as equipment than as one-off session history.

## Candidate Equipment

### Opportunity Detector

A lightweight agent-facing workflow could guide agents to recognize and classify
ephemeral constructs during normal work. It should produce a recommendation,
not silently edit durable docs.

The detector should distinguish:

- no durable action needed;
- mention in the current closeout only;
- add a note to the active plan;
- create a source handoff for future processing;
- create or update a backlog item, issue, or queued plan;
- recommend a side quest now because the opportunity affects the active change
  set.

The detector should not start a new side quest, mutate durable docs, or open
tracker work solely because it noticed a signal. It should surface the
recommendation and the reason, then proceed according to established repo policy
or explicit operator authorization for that route.

### Routing Policy

The routing policy should choose a handling mode based on harness capabilities,
operator preference, urgency, risk, and disruption cost.

Possible modes:

- side chat, when the harness supports it and the operator prefers that path;
- subagent or agent thread, when independent analysis can proceed without
  interrupting the main worker;
- current thread, when the opportunity affects active work or no side surface is
  available;
- durable follow-up note in the active plan;
- new queued plan, local backlog note, or issue tracker item;
- explicit no-action record when the construct is intentionally session-local.

### Handoff Template

A template should make side-quest handoff material consistent enough for later
ingestion. It should capture:

- source context and provenance;
- the ephemeral construct being considered;
- why it may be durable;
- risks of premature promotion;
- candidate durable surfaces;
- harness and operator-preference constraints;
- validation ideas;
- follow-up routing and return contract.

### Preference Surface

The repo may need a small preference surface describing how this operator wants
opportunity recommendations handled. It should avoid hard-coding one harness.
Examples:

- prefer side chat for broad reflection when available;
- keep the main worker responsible for integration;
- do not promote side-thread discoveries into canonical docs without a designed
  follow-up;
- preserve source handoffs as provenance when future engineering is expected;
- choose issue tracker, active plan, backlog, or local note according to repo
  policy.

### Validation And Pressure Scenarios

Future equipment should be validated with pressure scenarios:

- a small repeated operator preference that belongs in a closeout note only;
- a recurring workflow correction that belongs in agent-facing policy;
- a side-thread discovery that should become a source handoff and deferred
  follow-up;
- a security-sensitive session habit that should trigger security closeout;
- a repo without side-chat support, requiring current-thread or issue fallback;
- a repo without issue tracker access, requiring local queued-plan fallback;
- a tempting but premature idea that should remain unpromoted.

Expected evidence:

- the agent notices the opportunity without an explicit operator prompt;
- the agent recommends rather than silently mutates;
- the recommendation is right-sized to risk and durability;
- the selected route matches harness capability and operator preference;
- the artifact is durable enough for a later agent to resume;
- canonical docs are not polluted with undeveloped doctrine.

## Design Constraints

The equipment should be portable across repositories and harnesses:

- do not assume side chats, subagents, GitHub Issues, Codex, Python, or a
  specific review tool;
- separate universal opportunity detection from adapter-specific routing;
- keep always-loaded instructions minimal;
- make mutation opt-in and scoped;
- preserve auditability when an ephemeral construct becomes source material;
- keep privacy and sensitive-data boundaries explicit.

The equipment should also scale down. Not every useful observation needs a PRD
or a new issue. The future design should make the smallest durable action the
default and reserve full engineering treatment for constructs with meaningful
future impact.

## Security And Privacy Notes

Opportunity capture can itself create risk. Session history may include
sensitive data, private operator preferences, tool outputs, local paths, or
third-party content. Future equipment should require agents to classify what is
safe to persist and avoid copying sensitive or third-party-instruction content
into durable docs without explicit authorization.

If the construct concerns credentials, personal data, security posture, or
authority boundaries, the recommendation should include the applicable security
closeout path before promotion.

## Relationship To Existing Follow-Ups

This handoff should be processed after, or in coordination with, the Portable
Agentic Engineering Workflow Equipment follow-up. That story defines the broader
agent-operated engineering workflow. This story adds a meta-workflow: noticing
when session-scoped workflow discoveries should be extracted into that durable
system.

If the Side-Thread Hand-Back Workflow has already landed, use its hand-back
contract as input. If Post-Seed Skill Migration has already landed, inspect
migrated skills for examples of session-scoped practices that were previously
global or implicit.

## Open Questions For The Future Grill Loop

1. What is the canonical name for this capability: Opportunity Capture,
   Workflow Extraction, Ephemeral Construct Promotion, or another term?
2. What threshold separates a closeout note from a full source handoff?
3. Which signals are reliable enough for automatic surfacing without creating
   constant noise?
4. How should agents learn harness capabilities and operator routing
   preferences?
5. What should happen when side chats are unavailable or non-resumable?
6. How should sensitive session content be summarized without overexposure?
7. What durable queue should be preferred when issue tooling is unavailable?
8. How should the system prove that it reduces repeated instruction burden?

## Proposed Post-Seed Task

Begin by ingesting this handoff and the then-current Framework Seed docs. Run a
`grill-with-docs` loop before drafting requirements. The loop should challenge
terminology, detection thresholds, routing surfaces, privacy constraints,
harness adapters, and right-sizing rules.

After the grill loop, produce a PRD, specification or implementation plan,
tests/validators, templates, docs, examples, security review, and Ralph-reviewed
closeout appropriate to the final scope.
