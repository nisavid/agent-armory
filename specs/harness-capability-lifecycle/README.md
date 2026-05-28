# Harness Capability Lifecycle Methodology

Status: Equipment Blueprint
Promotion state: specified

This Equipment Design Bundle records the accepted design package for issue
[#62](https://github.com/nisavid/agent-armory/issues/62). It specifies how the
Armory discovers, compares, reanalyzes, refines, deprecates, removes, and
projects Harness Capability work after the first Vanilla Harness Capability
Profiles exist.

The package closes the design scope of issues
[#63](https://github.com/nisavid/agent-armory/issues/63),
[#64](https://github.com/nisavid/agent-armory/issues/64),
[#65](https://github.com/nisavid/agent-armory/issues/65),
[#66](https://github.com/nisavid/agent-armory/issues/66), and
[#67](https://github.com/nisavid/agent-armory/issues/67). It does not implement
new CLI commands, profile schema fields, validators, automation, Manager Core
behavior, or Jig Runner integration.

Issue [#61](https://github.com/nisavid/agent-armory/issues/61) is accepted
design input. Agent Test Jigs and Harness Test Suites are future evidence paths
for this lifecycle, not implemented capabilities in this package.

## Bundle map

- [Capability card](capability-card.md)
- [Interface decision record](interface-decision-record.md)
- [Security and control classification](security-control-classification.md)
- [Pressure scenarios](pressure-scenarios.md)
- [Validation plan](validation-plan.md)
- [Implementation projection](implementation-projection.md)
- [Closeout evidence plan](closeout-evidence-plan.md)
- [Capability Profiling Protocol](../capability-profiling-protocol/)
- [Agent Test Jigs design package](../agent-test-jigs/)
- [Manual refresh review workflow](../vanilla-harness-capability-profiles/workflows/manual-refresh-review.md)

## Issue projection

- Epic: [#62 Harness Capability lifecycle methodology](https://github.com/nisavid/agent-armory/issues/62)
- [#63 Design new capability discovery and onboarding methodology](https://github.com/nisavid/agent-armory/issues/63)
- [#64 Design cross-harness capability definition methodology](https://github.com/nisavid/agent-armory/issues/64)
- [#65 Design capability reanalysis and schema refinement methodology](https://github.com/nisavid/agent-armory/issues/65)
- [#66 Design capability deprecation and removal methodology](https://github.com/nisavid/agent-armory/issues/66)
- [#67 Project Harness Capability lifecycle methodology into Manager Core and Forge workflows](https://github.com/nisavid/agent-armory/issues/67)

Related design inputs and downstream surfaces:

- [#4 Replace harness catalog with Vanilla Harness Capability Profiles](https://github.com/nisavid/agent-armory/issues/4)
  and child issues #42 through #49 provide the current profile, Manager Core,
  protocol, refresh, and closeout baseline.
- [#61 Design Agent Test Jigs and Harness Testing System](https://github.com/nisavid/agent-armory/issues/61)
  provides the future controlled validation path.
- [#23 Agent Equipment Config](https://github.com/nisavid/agent-armory/issues/23)
  and [#3 Periodic Actions](https://github.com/nisavid/agent-armory/issues/3)
  own future configurable and recurring lifecycle execution.
- [#25 Reflection and Head Gear](https://github.com/nisavid/agent-armory/issues/25)
  is a future source for reflection findings, not a substitute for this
  lifecycle.
- [#36 Project Config enforcement into Smith workflows](https://github.com/nisavid/agent-armory/issues/36)
  is a consumer of reliable harness/config capability facts.
- [#59 Reanalyze Codex hook and command routing after Jig design lands](https://github.com/nisavid/agent-armory/issues/59)
  is an early pressure case for reanalysis and future jig-backed evidence.

Native GitHub dependencies and labels remain authoritative for blocked state.
This bundle records the design shape and the implementation issue projection.

## Purpose

Harness capabilities change through releases, docs, local behavior, user
configuration, managed policy, plugins, hooks, tooling, and future equipment.
The lifecycle methodology gives Smiths, Forgewrights, Outfitters, reviewers,
and later automation a shared way to route those changes without flattening
weak evidence into profile truth.

The methodology keeps four concerns separate:

- Candidate lifecycle: discover and classify a possible capability change.
- Evidence lifecycle: decide what evidence exists and what proof is still
  missing.
- Profile lifecycle: update Vanilla Harness Capability Profiles only through
  Manager Core gates and accepted profile workflows.
- Projection lifecycle: create follow-up issues for implementation,
  automation, schema, validation, or workflow work at the smallest coherent
  granularity.

## Lifecycle loop

### 1. Discover a candidate

A lifecycle candidate is a possible change in a Harness Capability Surface. It
may come from:

- first-party release notes, documentation, changelogs, source code, or schema
  references;
- existing Vanilla Harness Capability Profile refresh work;
- Capability Profiling Protocol Study Plans or Study Reports;
- schema pressure reports;
- Reflection Findings;
- downstream Smith or Outfitter work that needs a capability fact;
- security closeout or threat-model findings;
- local observations from approved profile refresh;
- future Harness Test Suite or Agent Test Jig results.

Discovery does not mutate canonical profile truth. The candidate records the
target harness, capability family, source pointer, evidence class, suspected
impact, affected consumers, and current uncertainty.

### 2. Classify evidence

Evidence classes are ordered by how directly they support durable profile
claims:

1. First-party source evidence: official docs, release notes, schema files,
   source repositories, or changelogs controlled by the harness owner.
2. Curated fallback evidence: third-party metadata used only when first-party
   evidence is unavailable or insufficient and labeled as fallback.
3. Local observation: reproducible local CLI, UI, runtime, or config evidence
   with scope, version, environment, and scratch disposition recorded.
4. Study Report: Capability Profiling Protocol output with selected rigor,
   observation points, and sufficiency criteria.
5. Jig evidence: future Agent Test Jig or Harness Test Suite result with
   driver, fixture, status, and limitation metadata.
6. Implementation inference: a reasoned conclusion from source shape or code
   behavior that still needs review before becoming profile truth.
7. Hypothesis, unknown, unsupported, or not-applicable: explicit uncertainty,
   negative evidence, or out-of-scope classification.

Do not collapse these classes into one confidence label. The class determines
what action is allowed next.

### 3. Correlate across harnesses

Cross-harness definition starts with the narrowest behavior that evidence can
support. Compare candidates across these dimensions:

- operation: what the user or agent can do;
- activation: how the surface is loaded, triggered, or selected;
- authority: which config, permission, sandbox, approval, or managed-policy
  layer can allow, constrain, or override it;
- state: what lifecycle, reload, persistence, update, or teardown behavior
  applies;
- side effects: filesystem, process, network, external disclosure, credential,
  automation, or irreversible mutation effects;
- scope: version, platform, plan, tier, workspace, project trust, user
  profile, installed equipment, plugin state, and local machine applicability;
- failure mode: unsupported behavior, partial support, fallback path,
  degraded state, explicit error, or silent no-op;
- consumer meaning: whether a Smith, Outfitter, profile manager, validator, or
  security gate can safely use the claim.

The allowed correlation outcomes are:

- common capability: the same meaningful behavior is source-backed across the
  compared harnesses;
- harness-specific variant: the behavior is related but materially different
  in activation, authority, side effects, scope, or failure mode;
- compatibility bridge: one harness can import, emulate, or translate another
  surface without proving native support for every imported component;
- superficial equivalence: names look similar but evidence does not support a
  shared capability;
- unresolved: the candidate needs more source, study, or future jig evidence.

If authority, side-effect, or activation semantics are unknown, do not promote
the candidate to a common capability.

### 4. Select the analysis path

Choose the lightest path that can answer the current decision:

- Semantic hygiene: use when the issue or docs need naming, label, or scope
  clarification only.
- Source refresh: use when first-party docs or releases can settle the claim.
- Capability Claim Triage: use when a profile claim needs retain, revise,
  split, remove, or follow-up disposition.
- Capability Profiling Protocol study: use when evidence requires a study
  plan, controlled observations, or explicit selected rigor.
- Schema pressure review: use when the current profile schema cannot represent
  the candidate without losing material meaning.
- Security closeout: use when the candidate affects permissions, sandboxing,
  process execution, network access, secrets, hooks, MCP/tools, managed
  policy, automation, or external disclosure.
- Future jig validation: use when local behavior needs controlled execution
  and issue #61 follow-up implementation provides adequate runner, driver, and
  suite support.

Unimplemented analysis paths remain explicit limitations. Do not write
profile claims as if unavailable jig validation already exists.

### 5. Decide the lifecycle disposition

Lifecycle dispositions are workflow decisions, not new profile schema statuses.
Until schema work says otherwise, Vanilla Harness Capability Profile claims
continue to use the v1alpha1 claim statuses: `supported`, `unsupported`,
`unknown`, and `not-applicable`.

Use these workflow dispositions when routing candidates:

- retain: current profile claim and evidence remain adequate;
- revise: update an existing claim through Manager Core gates;
- split: separate a too-broad cross-harness or profile claim into narrower
  claims;
- add: introduce a new claim, enrichment field, research note, or profile
  entry after schema and evidence gates pass;
- deprecate: source says the capability is discouraged, superseded, or
  scheduled for removal, but it still exists in the relevant checked state;
- remove: source and validation show the capability no longer exists or was
  never in scope;
- mark unsupported: source or local evidence supports a negative claim;
- mark unknown: evidence is insufficient, stale, contradictory, or unavailable;
- defer: create a follow-up issue because the decision depends on future
  schema, Manager Core, Config, Periodic Actions, jig, or workflow work;
- reject: do not route further because the candidate is out of scope,
  duplicate, or unsupported by the Armory's current purpose.

Every disposition records the evidence class, affected harnesses, affected
profile claims or workflow surfaces, security impact, and projection decision.

### 6. Gate schema and profile change

Schema evolution requires all of the following:

- a candidate that cannot be represented without material loss in the current
  schema;
- reviewed schema pressure that states why existing fields are insufficient;
- compatibility and migration expectations for existing profiles;
- validation-plan updates for schema, fixture, and Manager Core behavior;
- security/control review if the schema records effects, permissions, secrets,
  automation, external disclosure, or local observations;
- implementation projection into a scoped issue before executable work begins.

Profiles remain descriptive. Do not add Smith instructions, downstream
projection guidance, or consumption recipes to profile records. The accepted
schema pressure boundary from
[`SP-010`](../vanilla-harness-capability-profiles/schema-pressure-report.md)
continues to apply.

Profile mutation follows the manual refresh workflow until later Manager Core
implementation changes it. Claim IDs remain stable unless the change is a
reviewed split, merge, or removal with traceable replacement notes.

### 7. Project implementation work

Projection issues should be small enough that a future agent can validate them
without reopening the entire lifecycle design. Use separate issues for:

- Manager Core candidate artifacts and JSON output;
- schema additions or migrations;
- manual refresh workflow updates;
- Capability Profiling Protocol or Study Report changes;
- Harness Test Suite and Agent Test Jig integration;
- Config and Periodic Actions integration;
- Issue Tracker Ops and Reflection Finding routing;
- docs, examples, and reviewer-report consumption surfaces.

Do not create one implementation issue that owns Manager Core, schema,
workflow, validation, automation, and jig integration together.

## UX and cognitive-load rules

The primary consumption surfaces are issue bodies, profile diffs, study
reports, manual refresh artifacts, PR bodies, and reviewer reports. They should
show the current decision before raw evidence.

Use these rules for Smith, Outfitter, review, and report surfaces:

- Name the lifecycle phase and decision at the top.
- Show the affected harnesses, capability family, evidence class, and next
  action before detailed notes.
- Keep common, variant, compatibility, superficial-equivalence, and unresolved
  outcomes visibly distinct.
- Hide raw logs, local paths, transcripts, screenshots, and model outputs
  behind artifact references and durability classification.
- Use `CONTEXT.md` vocabulary for Agent Harness, Harness Capability Surface,
  Vanilla Harness Capability Profile, Study Report, Jig Adequacy Report, Smith,
  Outfitter, and Review Until Clean.
- Put implementation handoff in GitHub issues or committed specs, not in
  transient chat summaries.

## Documentation-pressure example: Codex hooks

Official Codex docs checked on 2026-05-28 are a useful pressure case:

- project-local `.codex/` config, hooks, and rules load only when the project
  is trusted, while user and system config can still load;
- `features.hooks` enables lifecycle hooks, and hooks may be loaded from
  `hooks.json` or inline `[hooks]` tables near active config layers;
- only command hook handlers run today; prompt and agent handlers are parsed
  but skipped;
- matcher support varies by event, and `UserPromptSubmit` and `Stop` ignore
  configured matchers;
- `transcript_path` is available for hook convenience, but the transcript
  format is not a stable hook interface;
- sandbox mode and approval policy are separate security-control layers.

These facts illustrate why the lifecycle cannot treat "hook support" as a
single portable cross-harness claim. A profile claim must preserve trust,
matcher, handler, input-stability, permission, sandbox, and approval
semantics, or it must remain unknown, split, or harness-specific.

Sources:

- [Codex config basics: configuration precedence](https://developers.openai.com/codex/config-basic#configuration-precedence)
- [Codex configuration reference](https://developers.openai.com/codex/config-reference#configtoml)
- [Codex advanced configuration: hooks](https://developers.openai.com/codex/config-advanced#hooks)
- [Codex hooks: config shape](https://developers.openai.com/codex/hooks#config-shape)
- [Codex hooks: matcher patterns](https://developers.openai.com/codex/hooks#matcher-patterns)
- [Codex hooks: common input fields](https://developers.openai.com/codex/hooks#common-input-fields)
- [Codex sandbox and approvals](https://developers.openai.com/codex/agent-approvals-security#sandbox-and-approvals)

## Closeout boundary

This design bundle is complete when it:

- defines discovery and onboarding;
- defines cross-harness capability correlation;
- defines reanalysis and schema-refinement gates;
- defines deprecation and removal routing;
- projects implementation work into scoped follow-up issues;
- passes repository validation;
- records security, documentation, Ralph Review, issue projection, evidence
  durability, and merge-readiness closeout.
