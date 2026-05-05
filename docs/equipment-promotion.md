# Equipment Promotion

Status: Forge Seed

The Equipment Promotion Path prevents examples, specs, plans, implementations, validations, and published equipment from being treated as the same thing.

Promotion state changes also preserve alignment with the
[Armory Vision](vision.md). A candidate moves forward only when the evidence
supports the intended agent and human experience, not merely the existence of
files or instructions.

## example

An `example` is an annotated teaching artifact that demonstrates Forge decisions.

Entry criteria:

- the artifact has a clear instructional purpose;
- it is labeled as non-production;
- it names the capability shape it demonstrates.

Exit criteria:

- a Smith chooses to turn the example into a real Equipment Candidate; or
- the example is retired, replaced, or kept only as teaching material.

## specified

`specified` equipment has accepted desired behavior but no implementation-ready plan.

Entry criteria:

- a spec states purpose, users, target harness assumptions, required surfaces, security boundaries, validation needs, and open questions;
- the spec does not claim implementation or validation.

Exit criteria:

- an implementation plan is accepted; or
- the spec is deferred or closed with rationale.

## planned

`planned` equipment has an implementation path ready for execution.

Entry criteria:

- scope, file ownership, validation strategy, security considerations, and dependencies are clear;
- unresolved stakeholder decisions are escalated or explicitly out of scope.

Exit criteria:

- implementation begins and the state moves to `implemented`; or
- the plan is revised, deferred, or closed.

## implemented

`implemented` equipment has built surfaces but has not completed equipment-specific validation.

Entry criteria:

- the planned docs, config, scripts, hooks, skills, Agent Profiles, plugins, tools, or templates exist;
- local checks relevant to the implementation have run or have an explicit unavailable-control note.

Exit criteria:

- validation evidence supports promotion to `validated`; or
- defects move the equipment back to `planned` or `specified`.

## validated

`validated` equipment has evidence that it behaves correctly in its intended harness and task pressure.

Entry criteria:

- deterministic checks pass where applicable;
- pressure scenarios or harness smoke tests cover the intended use;
- validation evidence shows the Agent can discover, equip, use, or hand off the
  equipment under realistic task pressure;
- cognition and Reflection equipment evidence shows changed agent behavior
  under task pressure, not merely plausible introspective prose;
- security and control checks have no unresolved reportable risk;
- evidence category, source basis, and residual uncertainty are recorded.

Exit criteria:

- publication materials, install path, and usage guidance are ready; or
- validation expires or harness drift requires revalidation.

## published

`published` equipment is intended to be equipped by users, Agents, or harnesses.

Entry criteria:

- the equipment is validated;
- installation or equipping instructions are clear;
- usage guidance explains where the equipment fits in the intended Loadout,
  Assembly, or Armory experience;
- support, maintenance, refresh, rollback, and deprecation expectations are documented;
- publication does not expose secrets, private host assumptions, or unapproved mutation authority.

Exit criteria:

- a new version supersedes it;
- harness drift requires revalidation;
- the equipment is deprecated, unpublished, or withdrawn.

## entry/exit criteria

Every state change records the evidence that justifies entry into the new state and the criteria required to leave it.

Smiths keep state labels current in examples, specs, plans, implementation docs, and publication surfaces. Forgewrights inspect promotion-state language when Forge decisions change, validation rules change, or harness capability claims are refreshed.
