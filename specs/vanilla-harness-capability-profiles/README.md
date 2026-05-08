# Vanilla Harness Capability Profiles

Status: Equipment Blueprint
Promotion state: specified

This Equipment Design Bundle defines the Vanilla Harness Capability Profiles Epic:
the replacement shape for the Harness Capability Catalog's structured records.
It covers Vanilla Harness Capability Profiles and the Harness Capability
Profile Manager. It does not implement periodic scheduling or prescribe how
Smiths consume profile facts when crafting Agent Equipment.

## Bundle map

- [Capability card](capability-card.md)
- [Interface decision record](interface-decision-record.md)
- [Security and control classification](security-control-classification.md)
- [Pressure scenarios](pressure-scenarios.md)
- [Validation plan](validation-plan.md)
- [Closeout evidence plan](closeout-evidence-plan.md)
- [Forge Domain Model Review](forge-domain-model-review.md)
- [Schema pressure report](schema-pressure-report.md)
- Research notes:
  - [Codex](research-notes/codex.md)
  - [Claude Code](research-notes/claude_code.md)
  - [Cursor](research-notes/cursor.md)
  - [Hermes Agent](research-notes/hermes_agent.md)
  - [OpenCode](research-notes/opencode.md)
  - [OpenClaw](research-notes/openclaw.md)

## Issue projection

- Epic: [#4 Replace harness catalog with Vanilla Harness Capability Profiles](https://github.com/nisavid/agent-armory/issues/4)
- [#42 Refactor live Forge validation boundaries](https://github.com/nisavid/agent-armory/issues/42)
- [#43 Implement Harness Capability Profile Manager core migration](https://github.com/nisavid/agent-armory/issues/43)
- [#44 Research harness surfaces and schema pressure](https://github.com/nisavid/agent-armory/issues/44)
- [#45 Refresh six Vanilla Harness Capability Profiles](https://github.com/nisavid/agent-armory/issues/45)
- [#46 Define the Capability Profiling Protocol](https://github.com/nisavid/agent-armory/issues/46)
- [#47 Review the Agentic Engineering Operating Model](https://github.com/nisavid/agent-armory/issues/47)
- [#48 Implement manual Harness Capability Profile refresh](https://github.com/nisavid/agent-armory/issues/48)
- [#49 Close out Harness Capability Profiles issue projection](https://github.com/nisavid/agent-armory/issues/49)

The projected issues are native sub-issues of #4 in story order. Tracker
dependencies make #43 blocked by #42, #44 blocked by #43, #45 blocked by #43
and #44, #46 blocked by #42, #48 blocked by #45 and #46, and #49 blocked by the
completed implementation stories. #23 and #36 are blocked by #4 for the
pre-Config manual profile surface. Periodic refresh remains deferred until
[#23 Agent Equipment Config](https://github.com/nisavid/agent-armory/issues/23)
and [#3 Periodic Actions](https://github.com/nisavid/agent-armory/issues/3).

## Purpose

Vanilla Harness Capability Profiles describe the Vanilla Harness Capability
Surface exposed by each supported Agent Harness. They record what the harness
can load, activate, configure, inherit, execute, gate, import, validate, and
refresh immediately after installation and onboarding with default settings and
default equipment, with evidence and schema-extension details attached to each
claim.

The Harness Capability Profile Manager is the system that maintains Harness
Capability Profiles through deterministic manager-core tooling, agent-guided
workflows, and optional evidence adapters. Harness Capability Refresh is future
recurring Agent Equipment that can invoke the manager on a cadence.

The Harness Capability Profile Manager Core is the deterministic tool layer. It
handles schema validation, structured IO, claim IDs, evidence-link checks,
summary generation, diffs, deterministic migration, dry-run and apply
mechanics, audit formatting, fixture checks, and machine-readable study plan or
report validation. Agent-guided workflows handle judgment-heavy work such as
Capability Claim Triage, selecting Capability Analysis Angles, interpreting
source deltas, comparing alternate Capability State Graphs, evaluating schema
pressure, and deciding whether similar harness behavior transfers.

The Manager Core is implemented as a standard-library Python CLI. Inference-
bearing manager behavior is specified as agent-guided workflows around the
core, not embedded in the deterministic CLI.

Every Manager Core command exposes stable JSON output, even when it also prints
human summaries. Agent-guided workflows, tests, and future automation consume
JSON rather than scraping prose.

The Manager Core uses one script with subcommands, provisionally
`tools/harness_capability_profiles.py`, so schema loading, profile discovery,
error handling, JSON output, and dry-run or apply semantics remain consistent.

Detailed Vanilla Harness Capability Profile validation belongs to
`tools/harness_capability_profiles.py validate`. The live repository validation
command established by the validation boundary refactor should invoke or
require the Manager Core's validation result without duplicating detailed
profile schema rules.

This epic defines the agent-guided workflows required for manual refresh of
Vanilla Harness Capability Profiles: research notes, Capability Claim Triage,
schema pressure review, study-plan and study-report review, and manual refresh
review. Later work may promote some of these workflows into reusable Agent
Equipment, but they are part of the Harness Capability Profile Manager system
needed to complete this epic.

The first implementation slice includes lightweight workflow templates or
checklists for those agent-guided steps under this Equipment Design Bundle.
They are local execution aids for the epic, not global repo policy or
Published Agent Equipment.

Workflow templates live under
`specs/vanilla-harness-capability-profiles/workflows/`. Planned starter
templates are `research-note.md`, `claim-triage.md`,
`schema-pressure-review.md`, `manual-refresh-review.md`,
`study-plan-review.md`, and `study-report-review.md`.

## Settled boundaries

- `docs/harness-capabilities.md` remains the human-facing catalog front door.
- Each supported harness has one per-harness structured Vanilla Harness
  Capability Profile under `docs/harness-capabilities/vanilla/<harness-id>.toml`.
- Shared schema and migrations live under `docs/harness-capabilities/schema/`.
- The current aggregate `docs/harness-capabilities.toml` is migrated into
  per-harness vanilla profiles and then removed once the manager can validate
  the new files and generate needed summaries. Authored truth should not remain
  split across old and new profile formats.
- The first implementation uses deterministic migration to seed the six
  per-harness vanilla profiles from the aggregate TOML. Migrated claims retain
  their evidence basis and are marked for schema pressure or equivalent review
  until research enriches them under the new rubric.
- Profiles are descriptive records of Harness Capability Surfaces, not Forge
  projection guidance or Smith instructions.
- Vanilla Harness Capability Profiles describe the Vanilla Harness Capability
  Surface, not the Effective Harness Capability Surface of a specific
  configured harness instance plus installed or equipped Agent Equipment.
- Profiles use first-party source evidence as the baseline. Local CLI or
  runtime observations supplement source-backed claims as a separately labeled
  evidence channel.
- Local observations are first-class but scoped evidence. They may support a
  source-backed claim, contradict a source, record local variation, or remain a
  noncanonical note. Exact observation fields are provisional during schema
  research.
- Nontrivial profile claims must distinguish universal harness claims from
  environment-scoped claims. Applicability may vary by harness version,
  distribution channel, plan or tier, platform, user profile, workspace,
  directory subtree, session, plugin install, or local machine. Exact scope
  values are provisional during schema research.
- The manager handles profile data, evidence, diffs, scouting, analysis,
  migration, and schema-candidate discovery through a deterministic core plus
  agent-guided workflows and optional evidence adapters.
- Periodic orchestration belongs to Harness Capability Refresh, not the profile
  manager. Periodic refresh integration is deferred until Periodic Actions
  exists, and Periodic Actions depends on Agent Equipment Config.
- The first manager-core implementation target is read-only: validate profiles,
  summarize them, compare profile revisions, and report schema pressure without
  network scouting or automatic file mutation.
- Vanilla Harness Capability Profile work blocks returning to Agent Equipment
  Config until the manager supports manual refresh: evidence scouting, change
  analysis, schema-candidate discovery, migration planning, controlled profile
  updates, and audit output.
- Effective Harness Capability Surface inventory or evaluation tooling is
  deferred. The base profile schema should still be shaped so future tooling
  can compose Vanilla Harness Capability Profiles with installed equipment,
  local config, and local observations.

## Epic stories

- Forge validation boundary refactor.
- Migration and profile validation core.
- Research notes and schema pressure.
- Profile schema enrichment and six profile refresh.
- Capability Profiling Protocol slice.
- Manual refresh manager.
- Closeout and issue projection alignment.

Project child issues after this design grill has settled enough acceptance
criteria for future Agents to execute the stories without repeating the same
scope questions.

The story order is a dependency chain with limited parallel research. Some
source research may happen while the migration core is implemented, but
schema/profile changes wait until the migration substrate exists.

After the initial batch of child-story acceptance criteria is drafted and
before issue projection, run a comprehensive Ralph Review of the batch. The
review considers the Armory and Forge vision, core requirements, current
status, this bundle's specs and ADRs, the design decisions from the grill, and
downstream issues that will depend on the batch outcomes.

Before issue projection, run a Forge Domain Model Review. The review should
inventory core concepts and domains, verify the split between Forge Canon,
Forge Core, Forge Equipment Core, and Armory Equipment Core, identify Seed-era
names still carrying live responsibilities, and decide any required renames,
reparenting, validator splits, or follow-up tasks.

The broader Agentic Engineering Operating Model Review is a separate
high-priority follow-up. This epic carries one checkpoint for it: before the
Manual Refresh Manager is considered feature-complete, either the Agentic
Engineering Operating Model Review has completed or this epic records a local
certification that its manual-refresh workflow has sufficient authority,
escalation, evidence-durability, mutation, and closeout rules to proceed.

## Prerequisite implementation story

The first implementation story refactors the live validation boundary before
the Harness Capability Profile Manager integrates with repository validation.
It is TDD-scoped around classifying and renaming the validation surface:

- define Armory Integrity Validation as the top-level live repository
  validation umbrella;
- define Forge Integrity Validation as the Forge-scoped suite within Armory
  Integrity Validation;
- define the relationship between those validation scopes and
  equipment-specific behavioral validation;
- inventory every current `tools/validate_armory_integrity.py` check and supporting
  test;
- classify each check as Armory Integrity, Forge Integrity,
  equipment-candidate shape validation, equipment-specific behavioral
  validation, historical Seed migration validation, or other;
- remove checks whose only purpose is proving the completed Forge Seed
  migration;
- re-home still-live provenance, source-disposition, route, documentation,
  template, spec, and bundle-shape checks under the correct live validation
  boundary;
- split bundle-shape checks from equipment-specific behavioral validation;
- rename or split the tool and tests so active validation no longer uses Seed
  Validation as its canonical umbrella;
- define the CLI or module target that downstream Manager Core validation will
  call;
- preserve temporary compatibility only inside the implementation branch when
  needed;
- add tests for classification, renamed command output, JSON shape, removed
  compatibility path markers, and live-doc command references;
- gate story completion on a deterministic check that no transient
  compatibility path remains in live surfaces;
- update active docs, specs, runbooks, tests, tool help, JSON output, and
  closeout commands to use the new validation boundary names;
- leave historical Seed documents historically accurate unless they are being
  used as current process guidance.

## Manager Core implementation story

The next implementation story is TDD-scoped around deterministic migration
and validation before research enrichment:

- implement `tools/harness_capability_profiles.py` as a standard-library
  Python Manager Core CLI;
- implement `migrate` with dry-run default and explicit `--apply`;
- split the aggregate `docs/harness-capabilities.toml` into exactly six
  per-harness Vanilla Harness Capability Profile files under
  `docs/harness-capabilities/vanilla/<harness-id>.toml`;
- preserve the aggregate catalog's harness ids, display names, checked-at
  timestamp, checked versions, version basis, evidence category, source URLs,
  source kinds, claim scopes, components, scheduling summaries, scheduling
  detail, limitations, uncertainty, refresh notes, and local observations;
- convert migrated source rows into stable evidence records with deterministic
  evidence ids;
- convert migrated catalog facts into stable claim records with deterministic
  per-profile claim ids;
- mark migrated claims with migration status and evidence basis so later
  refresh work can triage them;
- cover the standard surface-family rubric in every profile without inventing
  support claims: families not proven by migrated data must carry explicit
  unsupported, unknown, or not-applicable claims with limitations or
  uncertainty;
- implement `validate --json` for required profile metadata, vanilla scope,
  schema version, standard surface-family coverage, claim ids, claim status,
  evidence references, applicability scope, capability origin, limitations or
  uncertainty, source shape, and migration status;
- implement a summary check or summary writer so `docs/harness-capabilities.md`
  remains the human-facing catalog front door and is aligned with validated
  per-harness profiles;
- integrate Manager Core validation into the renamed or split repository
  validation surface without duplicating detailed profile rules;
- remove `docs/harness-capabilities.toml` as authored truth once migration and
  validation pass.

## Issue #44 research outputs

Issue #44 records one durable research note per supported harness and one
schema pressure report. These artifacts describe current research evidence and
profile-schema pressure only. They do not mutate canonical profile claims and
do not encode downstream Forge consumption logic.

The Manager Core validates the research-note/report structure required by the
story: required sections, checked-at/version-basis/source coverage, standard
surface-family coverage, evidence-classification language, schema-pressure
finding rows, allowed finding dispositions, and source references. The
deterministic checks prove structure and traceability, not the correctness of
agent-inferred conclusions.

The Manager Core implementation story is accepted when:

- rerunning migration from the same aggregate input produces stable profile
  files and no claim-id or evidence-id churn;
- validation fails for missing required metadata, duplicate claim ids, missing
  standard surface-family coverage, invalid claim status, missing evidence
  records, broken evidence references, missing applicability scope, missing
  origin, missing migration status on imported claims, and summary drift;
- JSON output uses stable keys, relative paths, machine-readable result codes,
  and nonzero exit status for validation failures;
- the aggregate TOML is absent as authored truth from the completed tree and
  active docs point to per-harness profiles rather than the retired aggregate;
- the live repository validation command calls Manager Core validation as the
  source of detailed profile checks;
- tests cover migration, idempotence, validation failures, JSON output,
  summary alignment, repository-validation integration, and aggregate-retirement
  behavior.

The first-slice profile schema is intentionally small and claim-centered. It
requires profile metadata, profile scope, standard surface-family coverage,
inline stable claim IDs, claim status, evidence references, applicability
scope, capability origin, limitations or uncertainty, and migration status for
aggregate-imported claims. It is sufficient to retire the aggregate TOML but is
not the final Harness Capability Profile schema.

## Research notes and schema pressure story

The research notes and schema pressure story uses the migrated profiles as the
baseline and studies the six harnesses for schema pressure before profile
enrichment. It produces durable research summaries and schema recommendations;
it does not treat those summaries as canonical profile claims until the profile
enrichment story applies them.

The story is accepted when:

- every supported harness has a durable research note that names the checked
  harness version or version basis, checked-at timestamp, first-party source
  set, fallback source use if any, locally observed evidence if any, and major
  uncertainty;
- research notes cover the standard surface-family rubric and call out
  evidence for instructions/context, skills, MCP/tools, hooks/events,
  plugins/bundles, Agent Profiles/subagents, memory/context retrieval,
  config/settings, permissions/approvals/sandboxing, scheduling/automation,
  commands/shortcuts, providers/connectors, runtime modes, cross-harness
  import/compatibility, and lifecycle reload/update;
- research notes distinguish source-backed facts, local observations,
  implementation inferences, hypotheses, unsupported claims, unknowns, and
  not-applicable surfaces;
- schema pressure findings identify fields, value sets, nested structures, or
  extension points needed for uniform capabilities, harness-specific extensions
  of uniform capabilities, and harness-specific bespoke capabilities;
- every schema pressure finding records affected harnesses, motivating
  evidence, example claim shape, proposed validation rule, migration impact,
  and disposition as accepted, deferred, rejected, or needs more evidence;
- cross-harness import and compatibility behavior receives first-class schema
  pressure review rather than being flattened into native support;
- memory-like capability surfaces receive first-class schema pressure review
  without assuming a stable shared memory API;
- research output records when multiple Capability Analysis Angles or
  Capability State Graphs could model the same claim and why one angle is
  preferred or deferred;
- scratch artifacts such as raw page bodies, fixture logs, and transient local
  observations are summarized by scope and disposition instead of committed as
  project truth;
- deterministic validation checks required research-note and schema-pressure
  sections without attempting to validate the correctness of agent inference;
- a Ralph Review of the schema pressure report runs before accepted schema
  changes become inputs to the profile enrichment story.

## Profile schema enrichment and six-profile refresh story

The profile enrichment story turns accepted schema pressure findings and
current evidence into canonical Vanilla Harness Capability Profiles for all
six supported harnesses.

The story is accepted when:

- accepted schema pressure findings are implemented as schema fields, value
  sets, validation rules, extension points, or explicit deferments;
- profile schema migrations preserve stable claim ids and evidence ids when
  claim meaning is unchanged, create new ids for new claims, and record
  replacement or supersession when a migrated claim is split or retired;
- all six Vanilla Harness Capability Profiles are refreshed against current
  first-party version and capability evidence, with fallback evidence labeled
  when used;
- each profile covers every standard surface family with supported,
  unsupported, unknown, or not-applicable claims and records limitations or
  uncertainty for every material unknown;
- each material supported claim has traceable evidence, applicability scope,
  capability origin, install or activation notes where relevant, configuration
  surface where relevant, and reload or update behavior where relevant;
- cross-harness import and compatibility claims record imported convention,
  surviving components, activation mechanism, disable behavior, precedence,
  fidelity limits, and evidence;
- memory-like claims record load timing, retrieval behavior, mutability,
  freshness, privacy exposure, write authority, and evidence or unknowns;
- harness-specific extensions appear under a clearly scoped extension shape
  and do not replace uniform fields when uniform fields apply;
- Capability Claim Triage has run for every retained, changed, new, unsupported,
  and unknown material claim, with rationale that accounts for current source
  deltas and prior evidence reuse;
- profiles remain strictly descriptive and do not prescribe how Smiths should
  craft equipment from the profile;
- `docs/harness-capabilities.md` summarizes the refreshed profiles and no
  longer depends on the retired aggregate TOML;
- deterministic validation passes for schema, migrations, profile files,
  summary alignment, evidence references, claim-id stability, and extension
  shape;
- remaining material unknowns are linked to follow-up issues or explicitly
  accepted as non-blocking with rationale.

## Capability Profiling Protocol story

The Capability Profiling Protocol story defines the generic meta-protocol for
planning and reporting studies of Capability Surfaces. The slice supports
Vanilla and Effective study targets with shared nomenclature, while the
official profile work continues to require only Vanilla Harness Capability
Profiles.

The story is accepted when:

- the protocol can describe Vanilla Harness, Effective Harness, Equipment,
  clean-room jig, and hypothetical Capability Surface targets without using
  separate terminology for common concepts;
- a study target declaration records target type, target state or Capability
  State Graph, scope, claims under study, required evidence, allowed effects,
  available controls, operator preferences, and selected rigor;
- rigor axes are explicit and provisional, including isolation, reproducibility,
  harness-state control, equipment-state control, config control, version
  pinning, provider/randomness control where available, subject/operator
  separation, network access, mutation allowance, and observation quality;
- effects are classified separately from rigor, including passive scanning,
  active non-mutating use, local mutation, profile mutation, external network
  access, external disclosure, process execution, and harness runtime-state
  changes;
- Capability State Graphs support sequences and DAGs of harness, equipment,
  component, and relevant external states, with observation points and expected
  evidence at each relevant state;
- study plans can record multiple Capability Analysis Angles for the same
  claim and compare cost, control, observation strength, contamination risk,
  and expected confidence;
- study reports distinguish observed results, claim confidence, test
  sufficiency, limitations, failed controls, artifact disposition, and profile
  impact;
- Standard Clean-Room Profiling Jig and Per-Harness Clean-Room Jig adequacy
  reports have a minimal machine-readable shape for claimed, verified,
  unsupported, and unknown controls;
- Manager Core validation checks study-plan, study-report, and jig-adequacy
  structure without executing studies or certifying inference-heavy
  conclusions;
- the protocol includes at least one representative study plan for a vanilla
  harness claim, one for an effective harness or equipment-composed claim, and
  one for a jig adequacy report;
- active local probing, mutating studies, and external disclosure remain
  blocked unless the relevant security/control classification and operator
  approval path are present.

## Manual refresh workflow

Manual refresh uses staged commands with dry-run defaults:

1. `scout` fetches or inspects evidence sources and records a refresh report or
   cache.
2. `analyze` compares evidence against current profiles and reports harness
   surface, profile, and schema changes.
3. `plan` produces a profile update and migration plan.
4. `diff` shows the planned profile, schema, and evidence-promotion changes
   against the current repository state.
5. `apply` updates profile files only after explicit execution.
6. `audit` summarizes sources, changed claims, unresolved uncertainty, schema
   pressure, and files changed.

Canonical profile mutation must be explicit and reviewable. The manager should
not silently mutate profile files while scouting or analyzing.

Scout output is instance-scoped scratch/cache by default. Durable project
evidence is exported explicitly through audit or evidence-export behavior and
is limited to curated source URLs, claim scopes, checked-at timestamps,
selected evidence notes, profile diffs, and reviewable summaries.

The manual refresh manager story is accepted when:

- `scout`, `analyze`, `plan`, `apply`, and `audit` expose stable JSON output
  and concise human summaries;
- `scout` can record first-party source evidence, fallback source evidence,
  local observations, selected study reports, curated evidence notes,
  explicitly marked hypotheses, and explicit unknowns without mutating
  canonical profiles;
- network scouting, local probing, command execution, live-study effects,
  profile mutation, and external disclosure are classified before use and
  blocked unless the configured or operator-approved control path allows them;
- `analyze` compares current evidence against current profiles, prior evidence
  basis, schema pressure findings, version deltas, and similar claims in other
  harnesses;
- `analyze` performs Capability Claim Triage so unchanged well-grounded claims
  can be accepted cheaply, changed or stale claims are selected for deeper
  review, and uncertain claims stay visible;
- `plan` emits a reviewable update plan with proposed profile edits, schema
  migrations if any, evidence promotions, claim triage rationale, security or
  control requirements, expected validation commands, and follow-up issue
  candidates;
- `diff` compares the update plan to current profile, schema, and durable
  evidence files so reviewers can inspect intended mutations before apply;
- `apply` requires an explicit plan reference, verifies the current profile
  state still matches the plan preconditions, refuses stale plans, and writes
  only the planned canonical profile or schema changes;
- `audit` records sources checked, profile files changed, claims added,
  changed, retired, unsupported, or left unknown, schema pressure, selected
  rigor deviations, scratch evidence disposition, validation results, and
  follow-up disposition;
- scratch artifacts remain out of committed project truth unless explicitly
  promoted as curated durable evidence;
- manual refresh does not depend on Periodic Actions or Agent Equipment Config;
- before this story is considered feature-complete, the Agentic Engineering
  Operating Model Review has completed or this epic records a local
  certification that manual refresh has sufficient authority, escalation,
  evidence-durability, mutation, and closeout rules;
- tests cover dry-run defaults, no silent mutation during scout or analyze,
  effect gating, stale-plan refusal, explicit apply, diff output, audit output,
  JSON shape, evidence promotion, issue-follow-up candidates, and validation
  after apply.

Manual refresh is complete enough to unblock returning to Agent Equipment
Config when all six Vanilla Harness Capability Profiles exist in the new
schema, each profile covers the standard surface-family rubric, material
surfaces have source-backed evidence or explicit unsupported or unknown claims,
Capability Claim Triage has run against current first-party version and source
evidence, pressure-set research notes exist, manager validate/summarize/diff
and audit pass, and remaining unknowns are issue-tracked or accepted as
non-blocking. Completion does not require exhaustive proof of every possible
surface.

Network scouting, local probing, controlled fixture use, live-study effects,
and controlled profile mutation require security/control classification before
implementation. The classification covers network reads and source trust, local
filesystem reads and writes, process execution, credential or auth exposure,
profile mutation gates, scratch artifact durability, local harness
contamination risk, and externally visible side effects.

Cross-harness import and compatibility behavior is a first-class profile
surface. Profiles record which external harness convention or component can be
imported, which parts survive translation, how import is activated or disabled,
what precedence rules apply, and what fidelity limits remain.

Memory-like capabilities are a first-class surface family even though they do
not yet share a stable cross-harness standard. Research should cover
monolithic preloaded memory files, structured memory stores, RAG or vector
retrieval, context provider plugins, session summaries, persistent goals or
tasks, user preferences or custom instructions, and reflection findings routed
to durable systems. Exact schema fields remain provisional.

## Closeout and issue projection alignment story

The closeout and issue projection alignment story turns the design-grill output
into executable tracker work and verifies that downstream stories can depend on
the resulting surfaces without inheriting unresolved terminology, validation,
or profile-state ambiguity.

The story is accepted when:

- the Forge Domain Model Review has run and its required terminology,
  validation-boundary, Seed-era naming, and reparenting decisions are applied
  or explicitly issue-tracked;
- the initial child-story acceptance criteria have received a Ralph Review that
  considers the Armory and Forge vision, current repo status, this Equipment
  Design Bundle, ADRs, downstream dependent issues, and closeout obligations;
- each projected child issue has a title, problem statement, non-goals,
  dependencies, acceptance criteria, expected artifacts, verification commands,
  security/control expectations, documentation closeout expectations, and
  remaining open questions;
- issue dependencies preserve the story order and identify limited parallel
  research lanes that do not mutate canonical profiles before their blockers
  complete;
- the issue projection records that periodic refresh integration is deferred
  until Periodic Actions exists, and that manual refresh remains blocking
  before returning to Agent Equipment Config;
- active docs and specs agree on Equipment Design Bundle, Capability Surface,
  Capability Profile, Vanilla and Effective Harness Capability Profile,
  Harness Capability Profile Manager, Armory Integrity Validation, Forge
  Integrity Validation, Capability Profiling Protocol, Capability State Graph,
  Capability Analysis Angle, and Capability Claim Triage;
- historical Seed records remain historically accurate while live guidance
  uses live-domain terms;
- downstream references from `docs/harness-capabilities.md`,
  `specs/harness-capability-refresh.md`, Agent Equipment Config materials, and
  issue tracker docs are updated or have recorded deferments;
- residual unknowns, deferred high-priority follow-ups, and accepted
  non-blocking limitations are issue-tracked or recorded with a clear owner and
  return condition;
- Cross-Boundary Coherence and Story Quality Ralph Reviews pass before the
  epic is treated as complete.

## Research and schema-pressure cycle

Before the profile schema is fixed, the bundle uses a research and
schema-pressure cycle:

1. Scout representative surfaces across the six supported harnesses.
2. Capture first-party evidence and local observations when available.
3. Draft provisional normalized fields from observed harness behavior.
4. Pressure the draft against awkward cases such as inheritance, partial bundle
   imports, lazy loading, plugin-shipped components, in-harness activation
   flows, cloud-only features, and preview features.
5. Revise the schema into the first implementation target.

The first concrete artifacts are source-backed surface evidence notes under
`specs/vanilla-harness-capability-profiles/research/<harness-id>.md`, one for
each supported harness. A schema pressure report synthesizes those notes into
accepted, deferred, rejected, or evidence-seeking schema findings.

Research notes use a light shared shape so evidence can be compared across
harnesses without freezing the profile schema:

- version and evidence basis
- surface findings
- installation and activation
- configuration and inheritance
- authority, permissions, and side effects
- cross-harness import and compatibility behavior
- validation probes
- schema pressure
- open questions

The first research cycle covers all six supported harnesses across the standard
surface-family rubric, with deeper source pressure on representative surfaces:

- Codex: skills, plugins, hooks, MCP, automations, AGENTS/profile layering.
- Claude Code: skills, hooks, MCP, plugins, subagents, settings, scheduled
  tasks.
- OpenClaw: compatible bundle imports, native plugins, cron/heartbeat,
  hooks/webhooks, multi-agent config.
- Hermes Agent: Skills Hub or external skill directories, profiles, toolsets,
  memory/context providers, cron/curator.
- Cursor: rules/AGENTS, skills, hooks, MCP, Cloud Agent Automations, plugins.
- OpenCode: plugins/hooks, custom tools, agents, instructions, permissions,
  command templates.

The Codex research cycle identifies candidate local probes for a live Codex
harness after source evidence establishes the base-harness baseline. Candidate
live observations must be scoped against source-backed claims, but active
probing waits until the Capability Profiling Protocol, security/control
classification, allowed effects, isolation requirements, and contamination
risks are defined. The specific Codex instance under test remains undecided
until that protocol work has enough detail to choose safely.

Live study uses a generic Capability Profiling Protocol rather than a fixed
harness-testing protocol. The meta-protocol generates a study protocol for the
selected Capability Surface target, such as a Vanilla Harness Capability
Surface, Effective Harness Capability Surface, or Equipment Capability Surface.
It considers target type, desired rigor, available controls, permitted effects,
operator preferences, evidence needs, and jig constraints so vanilla and
effective live-study targets can share common design and implementation where
their requirements overlap.

The protocol architecture is designed from the generic Capability Surface
standpoint. This epic implements only the slice needed for Vanilla Harness
Capability Profiles, using spec-driven TDD, but the design should remain shaped
for later Effective Harness Capability Profiles, Equipment Capability Profiles,
memory-system evaluation, integration tests, audits, and opportunity or risk
assessment.

The Capability Profiling Protocol distinguishes advised rigor from selected
rigor. Advised rigor follows from experiment-control factors such as target
surface, claim criticality, expected effects, contamination risk,
reproducibility needs, available harness controls, provider seed support,
isolation support, and evidence durability. Selected rigor is the actual study
choice after operator preference, cost and time limits, access constraints, and
harness jig limitations are applied.

Official Vanilla Harness Capability Profiles use the Standard Clean-Room
Profiling Jig as the preferred baseline. The jig aims to maximize control over
harness state, equipment, configuration, isolation, reproducibility, permitted
effects, and evidence quality. Per-harness profiles must record jig limitations
and any selected-rigor deviation from the advised clean-room baseline.

The perfect clean-room jig is an ideal baseline. A per-harness clean-room jig
records how closely that harness can approach the ideal and where it falls
short, such as seed control, config-root control, equipment isolation, plugin
isolation, subagent isolation, filesystem sandboxing, model/provider control,
network control, or noninteractive execution.

The Standard Clean-Room Profiling Jig and each Per-Harness Clean-Room Jig are
also Capability Surfaces. The Capability Profiling Protocol can therefore
profile jig adequacy, limits, isolation, observability, reproducibility, reset
behavior, and permitted effects with the same vocabulary used for harness and
equipment surfaces.

The first implementation must at least express a jig profile or jig adequacy
report: claimed controls, verified controls, unsupported controls, unknowns,
and how those limits affect selected rigor. Full self-hosted jig profiling may
come later, but jig limitations must not remain prose-only.

The Capability Profiling Protocol treats permitted effects as a design axis
separate from rigor. A study may be passive, active and non-mutating, locally
mutating, harness-configuration mutating, equipment-installing, network-using,
privileged, externally visible, or otherwise effectful. This taxonomy is
provisional and should be revised as research characterizes the capability
space.

Every study identifies the Capability Surface state or Capability State Graph
it targets. A single target state may be vanilla post-installation and
onboarding state, current or prior effective state, potential state after
proposed equipment installation, hypothetical state, or fixture state. A
Capability State Graph covers a sequence or directed acyclic graph of states
and transitions when a capability manifests across harness state,
state-bearing components, equipment, or external states, with testable aspects
at each relevant state or transition.

Every claim under study identifies the observation points on the Capability
State Graph where evidence is expected. Starter observation points include
before installation or onboarding, after default onboarding, after activation,
during agent invocation, after hook/tool/MCP calls, after config mutation,
after restart or reload, during teardown or recovery, and in external systems
affected by the capability. The observation-point taxonomy is provisional and
should expand as profiling reveals new evidence surfaces.

The protocol must allow multiple well-grounded Capability State Graphs and
test designs for the same capability or claim. A Capability Analysis Angle is
a way of modeling, probing, or judging a claim, including the chosen Capability
State Graph, observation points, controls, expected evidence, and practical
tradeoffs. Agents should be prepared to compare alternative Capability Analysis
Angles before accepting a study design or judging a test outcome.

Study reports distinguish claim confidence from test sufficiency. A report
states the claim tested, Capability Analysis Angle used, observed evidence,
whether the outcome supports or refutes the claim, whether the test is
sufficient for the intended use, and what alternate angles or stronger controls
remain worth considering.

The Capability Profiling Protocol produces separate study plans and study
reports. A study plan records the intended target, Capability State Graph,
Capability Analysis Angle, advised and selected rigor, permitted effects,
controls, observation points, and sufficiency criteria before execution. A
study report records actual execution, deviations from the plan, observed
evidence, claim confidence, test sufficiency, and follow-up analysis angles.
Study artifacts are generated or instance-scoped by default. Curated durable
summaries, selected study reports, evidence notes, audit summaries, and profile
claims are promoted to committed project surfaces only when they affect
profiles, decisions, or reviewable evidence. Raw transcripts, logs, and
temporary fixture output remain scratch unless explicitly promoted as portable
evidence.

The manager validates evidence linkage from material profile claims to allowed
evidence classes such as first-party sources, local observations, selected
study reports, curated evidence notes, or explicitly marked hypotheses and
unknowns. Capability Claim Triage decides how much re-analysis a claim needs.
Simple claims that were previously traced and remain applicable should not
require heavy inference; new-version analysis should focus on deltas from the
previously analyzed version; and similar capabilities across harnesses may
inform analysis angles, deductions, simplifying assumptions, and memoized
checks. The manager should reduce cognitive load and produce practical
outcomes on practical time scales rather than attempting exhaustive exploration
of the capability state and claim space.

Capability Claim Triage is hybrid. The manager deterministically identifies
obvious inputs such as changed versions, changed source URLs or sections,
missing evidence, critical-claim markers, stale evidence, profile schema
changes, and applicability-scope changes. Judgment-heavy work, such as
selecting alternate Capability Analysis Angles or deciding whether similar
harness behavior transfers, is agent-guided and recorded as analysis rationale.

Profile claims live inline inside profile entries at first, with stable claim
IDs. Stable IDs let triage, diffs, evidence links, migrations, and study
reports target specific claims without creating a separate claim ledger before
the schema pressure cycle proves one is needed. If later analysis needs a
machine-readable cross-profile claim index, the manager can extract it from
inline claim IDs.

Claim ID namespaces are per profile. Cross-profile references use
profile-qualified claim references. Cross-harness generalized claim IDs may be
introduced later only if research proves they are useful.

Profiles include positive, unsupported, and unknown claims when the distinction
matters. Explicit negative or unknown claims are required for standard surface
families, capabilities implied by docs but not verified, capabilities needed by
current or planned equipment, and unsupported behavior that affects safety,
portability, or design. Profiles do not need exhaustive negative claims for
every theoretical capability.

Profiles cover a normalized standard surface-family rubric while still allowing
open-ended harness-specific surfaces. Each standard family is addressed as
supported, unsupported, unknown, or not applicable. The starter rubric includes
instructions and context, skills, MCP/tools, hooks and events,
plugins/bundles, Agent Profiles and subagents, memory and context retrieval,
config and settings, permissions, approvals and sandboxing, scheduling and
automation, commands and shortcuts, providers and connectors, runtime modes and
noninteractive execution, cross-harness import and compatibility, and lifecycle
reload or update behavior. The rubric remains revisable as research discovers
better families or boundaries.

Profile entries distinguish capability origin. A capability may come from the
native harness, default config, default equipment, bundled plugin, external
provider, cross-harness import, local observation only, or an unknown source.
The origin taxonomy is provisional but should remain first-class because origin
affects vanilla profile semantics and future Effective Harness Capability
Surface composition.

Default equipment counts as part of a Vanilla Harness Capability Surface only
when it is installed or enabled by the harness's normal post-installation and
onboarding path. Profiles still label origin so native harness behavior,
default-equipped behavior, removable plugins, disabled-by-default features, and
onboarding-choice variants remain distinguishable.

Each supported harness normally has one Vanilla Harness Capability Profile with
explicit variants for material onboarding branches such as plan tiers, optional
default plugins, cloud versus local modes, or guided setup choices. Separate
profiles are reserved for onboarding paths that produce substantially different
vanilla surfaces that cannot be compared cleanly inside one profile.

## Provisional schema hypotheses

These axes are research prompts, not settled schema. Both the axes and their
field shapes remain subject to review and revision during the research and
schema-pressure cycle.

- support and evidence state
- maturity and availability
- capability origin
- capability state graph
- installation and activation mechanism
- load timing and trigger semantics
- memory shape, retrieval, mutability, freshness, privacy, and write authority
- profiling rigor, permitted effects, and selected-rigor deviations
- configuration and inheritance
- authority and permission boundary
- execution and side-effect model
- cross-harness import and compatibility behavior
- validation probe
- refresh volatility
- harness-specific extension shape

## Deferred high-priority follow-up topics

These topics are important to the Vanilla Harness Capability Profiles Epic but
are not part of the current design-grill branch unless the operator reopens
them:

- For a given harness instance, the effective capability surface includes the
  base harness capabilities combined with capabilities provided by equipped
  Agent Equipment. Tooling for this Effective Harness Capability Surface is
  deferred, but the Harness Capability Profile schema should support future
  composition.
- The Armory should later help evaluate memory-system options for Codex and
  OpenClaw harness instances by using the deeper harness-surface model that
  emerges from this epic.
- The Armory role taxonomy should later be reviewed for end-user stories that
  are not cleanly Smith, Outfitter, or Wielder stories, including
  pre-outfitter evaluation and selection scenarios.

## Supported harnesses

- Codex
- OpenClaw
- Hermes Agent
- Claude Code
- Cursor
- OpenCode
