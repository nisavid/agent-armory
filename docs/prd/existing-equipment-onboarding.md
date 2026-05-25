# Existing Equipment Onboarding PRD

Status: Repo Draft PRD

Published PRD Issue: #111

## Problem Statement

Agent Equipment onboarding needs a generic way to handle equipment that already
exists in a repository, user profile, harness, plugin cache, or explicit source
root. Existing equipment is not monolithic, and installed state is not evidence
of current use, retention intent, replacement intent, or safe removal.

Without a shared onboarding model, each equipment line can overclaim
Replacement Coverage, leave conflicting auto-triggerable capabilities active,
drop consumer compatibility contracts, lose reviewed operator decisions in
chat, or send user-specific follow-ups into team trackers. Operators need
onboarding to discover relevant Existing Equipment Surfaces, ask only for the
decisions that cannot be inferred safely, preserve compatibility and evidence,
and expose activation limits before new equipment becomes active.

## Solution

Define Existing Equipment Onboarding as a generic Agent Armory product contract
that equipment lines can implement or specialize.

The product contract covers:

- named Equipment Discovery Scopes;
- Onboarding Intent before detailed dispositions;
- classification of Existing Equipment Surfaces and Equipment Facets;
- reviewed Equipment Dispositions;
- Consumer Compatibility Entries;
- Equipment Review Records with structured evidence;
- unassessed-area handling and scoped risk acceptance;
- activation, Replacement Coverage, Operational Continuity, Shadow Mode, and
  Advisory Mode reporting;
- follow-up candidates with audience scope;
- a generic User Follow-up Registry fallback for user-specific follow-ups;
- Follow-up Reminder Surfaces with harness-specific projection;
- issue-tracker projection when team-wide follow-ups belong in a repository or
  team tracker.

The generic Armory contract should be stable enough for Fork Ops, Repo Ops,
Issue Tracker Ops, Agent Equipment Config, Periodic Actions, and future
equipment lines to reuse without copying one equipment line's vocabulary or
artifact names.

## User Stories

1. As an Operator, I want onboarding to discover existing skills, plugins,
   tools, config, hooks, prompts, docs, profiles, scripts, workflows, and other
   behavior-shaping surfaces, so that prior behavior is not ignored.
2. As an Operator, I want onboarding to distinguish installed state from
   current intent, so that old equipment is not retained or removed merely
   because it exists.
3. As an Operator, I want onboarding to ask when retention, replacement,
   discard, risk, or compatibility choices depend on my intent, so that the
   agent does not infer stakeholder decisions from weak signals.
4. As an Operator, I want questions phrased in progressive, relatable terms, so
   that I do not need to understand the full taxonomy before making a decision.
5. As an Operator, I want broad group-level recommendations, so that large
   migrations are understandable.
6. As an Operator, I want item-level and facet-level decisions to control
   behavior, so that a mixed surface is not handled as one indivisible object.
7. As an Operator, I want repo-local and user-global equipment handled
   differently, so that onboarding respects repository authority and personal
   tool ownership.
8. As an Operator, I want user-global equipment edits, removals, disables, or
   redirects to require explicit authority, so that onboarding does not mutate
   my broader environment unexpectedly.
9. As an Operator, I want skippable broad discovery to create visible
   Unassessed Equipment Areas, so that skipped work does not masquerade as
   safety.
10. As an Operator, I want accepted unscanned-equipment exceptions to record
    scope, impact, disclosure, and review freshness, so that future agents know
    what risk was accepted.
11. As an Operator, I want required user-specific follow-ups to persist outside
    team trackers, so that personal activation tasks are not lost or exposed in
    the wrong audience.
12. As an Operator, I want optional follow-ups to be easy to defer without
    discarding them accidentally, so that onboarding stays efficient.
13. As a Smith, I want a generic Existing Equipment Onboarding contract, so
    that each equipment line does not invent a separate migration model.
14. As a Smith, I want source-material disposition separated from Equipment
    Disposition, so that source extraction does not decide what happens to
    active or installed equipment.
15. As a Smith, I want structured review records with schema versions and
    artifact discriminators, so that review artifacts can be validated and
    evolved safely.
16. As a Smith, I want evidence entries referenced by ID, so that dispositions,
    risk acceptances, and coverage reports do not depend on free-form prose.
17. As a Smith, I want reviewed entries to use append-and-supersede lifecycle,
    so that history is preserved while current state remains derivable.
18. As a Smith, I want extension types to be namespaced and constrained, so
    that unknown semantics cannot support activation, coverage, conflict, or
    risk claims.
19. As a Wielder, I want Capability Reports or equivalent activation reports
    to derive current state from reviewed decisions, control-surface
    projections, evidence, compatibility constraints, blockers, and unassessed
    areas, so that reports are explainable.
20. As a Wielder, I want review records to avoid storing manual activation
    state, so that activation state reflects current projected controls and
    evidence.
21. As a Wielder, I want Replacement Coverage distinguished from Operational
    Continuity, so that retained-owner continuity is not mistaken for
    replacement.
22. As a Wielder, I want Shadow Mode distinguished from Advisory Mode, so that
    comparison mode and non-authoritative guidance have different safety
    meaning.
23. As a Wielder, I want retained authoritative owners represented explicitly,
    so that redirected behavior remains visible and testable.
24. As a Wielder, I want auto-triggerable conflicts to block activation unless
    resolved or risk-accepted in scope, so that harness-triggered behavior does
    not become inconsistent.
25. As a Wielder, I want explicit-only retained equipment to remain a conscious
    choice, so that low-risk overlap is still visible.
26. As an Agent, I want onboarding preflight to be non-mutating by default, so
    that discovery and recommendations cannot change behavior.
27. As an Agent, I want mutating review/apply workflows to be dry-run-default
    when changes are hard to reverse, varied, or situational, so that operators
    can review the exact plan.
28. As an Agent, I want replayable wet-runs to fail closed on drift, so that an
    approved dry-run plan is not silently replanned at apply time.
29. As an Agent, I want reviewed evidence gaps to fail closed when they affect
    activation, conflict, Replacement Coverage, Operational Continuity, or risk
    acceptance, so that missing proof does not become hidden permission.
30. As an Agent, I want low-impact advisory omissions to warn instead of block,
    so that onboarding rigor tracks consequence.
31. As an Agent, I want consumer compatibility handled separately from
    Equipment Disposition, so that preserving dependent output shapes does not
    imply behavior ownership.
32. As an Agent, I want required compatibility checks to block only their named
    workflow or capability scope, so that one compatibility issue does not
    freeze unrelated equipment.
33. As an Agent, I want mutating compatibility verification to be unsupported
    until specified, so that activation checks do not create surprise side
    effects.
34. As an Agent, I want follow-up candidates to carry audience scope, so that
    team-wide and user-specific work are routed to different durable homes.
35. As an Agent, I want Issue Tracker Ops used for team-wide projection when
    available, so that repository follow-ups become normal issue-tracked work.
36. As an Agent, I want tracker-unavailable follow-ups to produce projection
    records, so that temporary inability to write the tracker does not create a
    parallel tracker.
37. As an Agent, I want user-specific required follow-ups to use a generic
    User Follow-up Registry fallback when no preference is configured, so that
    required personal work is never chat-only.
38. As an Outfitter, I want reminder behavior to be harness-projected, so that
    follow-up visibility uses the strongest available surface in each harness.
39. As an Outfitter, I want reminder surfaces to minimize token overhead, so
    that unresolved follow-up visibility does not bloat ordinary sessions.
40. As a Forgewright, I want generic policy and schema decisions in Armory
    terms, so that Fork Ops can prove a concrete model without becoming the
    source of generic onboarding doctrine.

## Implementation Decisions

- Product boundary: Existing Equipment Onboarding is generic Armory equipment
  policy and schema behavior. Fork Ops may implement the first concrete version
  and feed lessons back, but the generic contract must not copy Fork Ops-only
  artifact names or fork-specific policy.
- Delivery sequence: capture the generic PRD now; let Fork Ops prove the first
  concrete migration/onboarding implementation; then use those lessons to
  implement generic Armory, Repo Ops, or shared Config/Issue Ops support.
- Onboarding preflight: the first generic workflow is a non-mutating preflight
  that discovers Existing Equipment Surfaces, proposes Equipment Facets,
  groups findings, identifies conflicts, proposes Consumer Compatibility
  Entries, identifies Unassessed Equipment Areas, and reports activation impact.
- Onboarding Intent: preflight establishes operator session intent before
  detailed dispositions. Installing or invoking new equipment is a useful
  signal, but it does not decide detailed dispositions.
- Discovery scopes: generic scope names include `repo-local`, `user-global`,
  `explicit-source-root`, and `known-plugin-cache`. Equipment lines may add
  namespaced scopes.
- Unassessed areas: skipped or inconclusive discovery creates an Unassessed
  Equipment Area with reason, affected capability or workflow scope, activation
  limits, retry or refine path, and any scoped risk acceptance.
- Dispositions: Equipment Dispositions attach to a surface or facet and cover
  migration, retain, redirect, disable, split, discard, defer, or equipment-line
  extensions with controlled semantics.
- Group handling: group-level dispositions guide presentation only unless the
  group is homogeneous or the operator deliberately chooses a group default.
  Surface-level and facet-level dispositions decide activation and coverage.
- Review artifact: the generic review artifact is an Equipment Review Record.
  It uses an artifact discriminator, its own schema version, reviewed entries,
  evidence IDs, lifecycle metadata, and validation rules. It is not active
  configuration by itself.
- Control projection: activation, disable, redirect, and mutation behavior must
  project into explicit control surfaces such as equipment config, hooks,
  harness settings, or documented manual controls before behavior changes.
- Evidence model: Equipment Evidence Entries carry stable IDs, source type,
  source path or URI, controlled fact type, optional summary, and freshness or
  invalidation data when needed. Source hashes and timestamps live in evidence
  or replay snapshots, not duplicated across dispositions.
- Evidence trust: `operator_statement` evidence can support operator intent
  and risk acceptance, but it cannot prove factual behavior by itself.
- Extension safety: unknown extension fact types and source types may be
  recorded but cannot support activation, Replacement Coverage, Operational
  Continuity, conflict, or risk claims until the consuming equipment understands
  their semantics.
- Current-state reports: activation and coverage reports derive current state
  from non-superseded reviewed decisions, projected control surfaces,
  retained-owner evidence, Consumer Compatibility Entries, follow-up blockers,
  evidence freshness, and Unassessed Equipment Areas.
- Replacement Coverage: Replacement Coverage requires target Agent Equipment
  to own active behavior for the declared scope. Redirected retained-owner
  behavior can preserve Operational Continuity, but it is not Replacement
  Coverage.
- Operational Continuity: Operational Continuity may come from target
  equipment or from a verified retained owner. Reports must name which source
  provides continuity.
- Shadow Mode: Shadow Mode requires a retained authoritative owner. It can
  build confidence and compare behavior, but continuity remains attributed to
  the retained owner and Replacement Coverage remains unestablished.
- Advisory Mode: Advisory Mode provides guidance, diagnostics, plans, or
  reports without authoritative behavior ownership. It does not satisfy
  Operational Continuity by itself.
- Consumer compatibility: Consumer Compatibility Entries are separate from
  Equipment Dispositions. They record the consumer, affected workflow or
  capability scope, compatibility impact, preserved contract or output shape,
  verification checks, evidence, and override eligibility.
- Compatibility verification: first implementation support should be
  non-mutating verification only. Mutating verification remains unsupported
  follow-up and blocks activation when required for the scope.
- Follow-up audience scope: follow-up candidates distinguish team-wide
  activation work from user-specific activation work. Team-wide work should be
  offered for Issue Tracker Ops projection when available.
- User registry: user-specific required follow-ups use a generic User Follow-up
  Registry. The default fallback is a registry under a well-known user-global
  agents home, such as a `follow-ups/registry.toml` subpath beneath the active
  user-global agents directory. Agent Equipment Config may later make this
  path configurable.
- Required user follow-ups: if no user registry or preference is available,
  onboarding must let the operator configure one or abort. Required
  user-specific follow-ups do not have a non-durable decline path.
- Reminder surfaces: Follow-up Reminder Surfaces are required conceptually, but
  the low or null token-overhead implementation path is harness-specific and
  must be proven before it becomes a guarantee.
- Issue Tracker Ops boundary: Issue Tracker Ops owns issue-tracked projection,
  fallback captures, and tracker reconciliation for team-wide follow-ups.
  Existing Equipment Onboarding prepares and routes follow-up candidates; it
  does not replace Issue Ops.
- Repo Ops boundary: Repo Ops should consume generic Existing Equipment
  Onboarding for repository-operation equipment. Existing Equipment Onboarding
  does not require Repo Ops to exist.
- Agent Equipment Config boundary: Agent Equipment Config should eventually
  carry shared paths, authority, schema fragments, and control projection
  policy. The generic onboarding contract must still describe plain artifacts
  when shared Config is absent.
- Run modes: non-mutating review may emit proposed structured artifacts.
  Mutating review/apply is dry-run-default for hard-to-reverse or situational
  workflows and should offer replayable wet-run after review.
- Replay snapshots: replayable wet-runs embed enough evidence snapshot to
  detect drift, including reviewed dispositions, evidence IDs, source hashes or
  timestamps, blocker-clearance facts, and required compatibility-check
  evidence.

## Testing Decisions

- Test externally visible behavior, artifact schemas, validation decisions, and
  report derivation rather than internal helper structure.
- Cover preflight with fixtures for empty discovery, repo-local discovery,
  user-global discovery, explicit-source-root discovery, known-plugin-cache
  discovery, skipped scopes, and inconclusive scopes.
- Cover classification with irrelevant equipment, consumer-only equipment,
  mixed ownership surfaces, fully owning equipment, and equipment with multiple
  facets.
- Cover Onboarding Intent cases where install/invocation intent is sufficient
  for default migration direction and cases where detailed disposition still
  needs an operator decision.
- Cover Equipment Review Record validation for artifact discriminator, schema
  version, required IDs, evidence references, controlled source types,
  controlled fact types, lifecycle metadata, supersede relationships, and
  extension namespace rules.
- Cover evidence trust rules, including operator statements that support intent
  but cannot prove factual equipment behavior.
- Cover current-state report derivation from reviewed decisions, projected
  controls, retained-owner evidence, compatibility entries, blockers,
  unassessed areas, and superseded entries.
- Cover Replacement Coverage and Operational Continuity as separate states.
- Cover Shadow Mode and Advisory Mode so neither accidentally establishes
  Replacement Coverage.
- Cover auto-triggerable conflicts, explicit-only retained equipment, scoped
  risk acceptance, and activation blocking.
- Cover Consumer Compatibility Entries with required, optional, and advisory
  impact; unknown workflow scopes; future scopes; missing impact; required
  verification pass, failure, unavailable check, and scoped risk override.
- Cover follow-up routing for team-wide tracker projection, tracker-unavailable
  projection records, user-specific registry writes, optional deferment,
  explicit discard, and required follow-up abort when no durable user registry
  is available.
- Cover reminder projection through harness fixtures once a harness-specific
  surface is selected.
- Cover run modes with dry-run plans, reviewed apply, replay drift failure,
  safe drift continuation when explicitly supported, and mutation refusal.
- Cover integration with Issue Tracker Ops, Agent Equipment Config, and Repo
  Ops through contract tests or fixtures rather than requiring those equipment
  lines to be implemented first.

## Out of Scope

- Implementing generic Existing Equipment Onboarding runtime behavior in this
  PRD change.
- Blocking Fork Ops from building its concrete migration/onboarding workflow
  before the generic Armory implementation exists.
- Making Fork Ops artifact names the generic Armory artifact names.
- Migrating all existing user-global skills, plugins, tools, configs, hooks,
  docs, prompts, or profile state.
- Replacing Issue Tracker Ops for team-wide follow-up projection.
- Replacing Agent Equipment Config for shared configuration, authority, path,
  and policy layering.
- Replacing Repo Ops for repository-operation framework behavior.
- Supporting mutating compatibility verification in the first implementation.
- Guaranteeing low or null token-overhead reminders before each target harness
  has a proven reminder projection.
- Treating review records as active control surfaces without explicit
  projection into config, hooks, harness settings, or other controls.

## Further Notes

- Source material for this PRD includes Agent Armory issue #111 and the Fork
  Ops equipment migration/onboarding synthesis linked from `nisavid/fork-ops#32`.
- This PRD uses Agent Armory vocabulary from `CONTEXT.md`; Fork Ops-specific
  names remain source examples, not generic doctrine.
- The next useful generic work is an Equipment Design Bundle for Existing
  Equipment Onboarding after Fork Ops has proven the concrete workflow enough
  to validate the shared schema and report model.
- The Published PRD Issue remains #111. Material changes to this repo draft
  should be projected to #111 after review.
