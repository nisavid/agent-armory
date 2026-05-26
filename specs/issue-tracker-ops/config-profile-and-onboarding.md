# Config Profile And Onboarding: Issue Tracker Ops

Status: Equipment Blueprint
Promotion state: planned

This spec describes desired behavior only. It does not implement Agent Equipment.

Issue: [#13](https://github.com/nisavid/agent-armory/issues/13)
Product requirements:
[Issue Tracker Ops PRD](../../docs/prd/issue-tracker-ops.md).

## Purpose

Issue Tracker Ops needs a progressive config profile that lets agents and
operators use tracker policy safely before, during, and after Agent Equipment
Config is available. The profile defines Issue Ops policy and onboarding
behavior without moving generic layer composition, governance, migration apply,
or effective-config explanation out of Agent Equipment Config.

The config profile gives Issue Ops enough local knowledge to:

- run session-scoped issue workflows without hidden preference;
- serialize and ingest a plain handoff;
- expose missing policy, assumptions, incomplete sections, confidence, and
  safety status in machine-visible output;
- fail closed for unsafe tracker mutation;
- contribute an Issue Ops schema fragment and consumer semantics when shared
  Config is equipped.

## Progressive Enhancement Boundary

Issue Tracker Ops treats Agent Equipment Config as the durable layered
configuration primitive. Shared Config owns layer precedence, Policy Authority,
generic conflict diagnostics, source migration apply, authoring mechanics, and
effective Config explanation.

Issue Ops owns the behavior-specific profile: taxonomy, priority scales,
workflow status semantics, readiness signals, WIP policy, stakeholder
overrides, issue-set selection, dependency semantics, mutation safety, external
disclosure, adapter capability assumptions, onboarding prompts, compatibility
classification, and effective next-work explanation.

When shared Config is absent, Issue Ops may operate only from explicit session
inputs, discovered tracker facts, and a plain handoff. Advisory and dry-run
operations remain available when their inputs are sufficient. Mutation-capable
behavior fails closed unless policy explicitly allows the side effect and the
adapter confirms support.

When shared Config is present, the Issue Ops field namespace becomes the
`issue_tracker_ops` schema fragment and the plain handoff becomes a session
override layer. Issue Ops derives its consumer action decision from effective
Config and records the consumer decision before external calls, durable
publication, or tracker mutation.

## Plain Handoff And Session Behavior

The plain handoff is a TOML session-scoped record for continuity when shared
Config is absent or intentionally not loaded. It is not durable project policy.
It must be ingestible later as a session override in Agent Equipment Config.

The plain handoff may include:

- tracker identity and selected adapter;
- runtime mode, external disclosure policy, and mutation safety gates;
- taxonomy mappings for category, state, depth, work kind, engagement mode,
  brief status, dependency disposition, and other tracker predicates;
- priority scales, board-column or workflow status semantics, WIP policy, and
  selected-for-work indicators;
- readiness signals, stakeholder overrides, issue-set selection predicates,
  and dependency semantics;
- adapter capability assumptions, including native, emulated, unsupported, and
  fallback behavior;
- plain-text references to relevant policy surfaces when a structured field
  cannot faithfully represent the current rule.

Session behavior must never treat a missing field as silent approval. Missing
mutation policy produces advisory output or a blocking consumer action
decision. Missing selection policy produces effective next-work output that
names the unavailable factor and explains how candidate ordering was derived.

## Onboarding Flow

Onboarding starts when Issue Ops lacks enough policy to perform the requested
behavior safely or explainably. The flow should be interruptible and resumable,
and it should expose progress in a way that keeps operators focused on the next
decision rather than the whole policy model.

Onboarding states:

- `first_run`: no usable Issue Ops policy was found for the requested scope.
- `incomplete`: some required policy exists, but one or more sections block the
  requested behavior.
- `interrupted`: prior onboarding stopped before a safe terminal state.
- `resume`: onboarding continues from a saved partial state.
- `restart`: the operator discards partial onboarding state and starts again.
- `re_onboard`: existing policy is present, but drift, conflict, stale schema,
  or changed scope requires a new decision.
- `advisory_ready`: read-only or dry-run behavior can proceed with visible
  assumptions.
- `mutation_ready`: write-capable behavior is authorized by usable policy and
  adapter support.

The onboarding output should group decisions by immediate purpose: tracker
selection, taxonomy, mutation and disclosure safety, issue selection,
dependency semantics, foreign policy disposition, and compatibility. Each
decision point should name a recommended next action when evidence supports
one, with alternatives limited to meaningful choices for the current surface.
Advanced policy remains hidden until the current behavior needs it.

## Foreign Policy Surface Discovery And Migration Fates

Onboarding discovers repo-local and user-global Foreign Policy Surface inputs
that already carry issue-tracker behavior. Discovery includes skills, docs,
config files, hooks, scripts, templates, tracker instructions, and integrations.
User-global discovery may inspect and classify surfaces, but user-global
mutation requires explicit approval.

Each discovered Foreign Policy Surface receives a reviewed migration fate:

- keep and establish compatibility;
- remove and ingest policy;
- remove and discard policy;
- ignore;
- defer for review;
- split.

`keep and establish compatibility` preserves a surface for active consumers
while anchoring its policy in the Armory preferred encoding. `remove and ingest
policy` converts useful policy into Issue Ops Config and retires the foreign
surface when its consumers no longer require it. `remove and discard policy`
removes a surface whose policy should not continue. `ignore` leaves a surface
outside the migration scope. `defer for review` records a blocking or
judgment-heavy disposition. `split` separates facets that need different
fates.

Migration is plan-first. Apply output must show exact source targets,
authority, diff or create payload, compatibility decision, audit evidence, and
rollback stance before a write occurs.

## Compatibility Classification

Compatibility classification decides how a kept Foreign Policy Compatibility
Surface remains faithful after Issue Ops policy is anchored in Config. The fate
is operator-facing; the mechanism is selected after the surface is classified.

Compatibility mechanisms:

- indirection, where the foreign surface points to the preferred policy source;
- generation, where Issue Ops or Config produces the foreign surface from the
  preferred policy source;
- adapter behavior, where Issue Ops preserves compatibility at operation time;
- mixed strategy, where separate facets use separate mechanisms.

Classification must record what the foreign surface can represent, what it
cannot represent, which consumers still depend on it, which assumptions make
compatibility safe, and which policy remains prose-only with an explicit
reason.

## Machine-Visible Output

Issue Ops output must make uncertainty explicit. Machine-visible output
includes Config Safety Status, safety status, assumptions, incomplete sections,
confidence, policy authority evidence, discovered Foreign Policy Surface
records, migration fates, compatibility classification, conflict reporting,
adapter capability assumptions, and unavailable config-equipment status.

Effective next-work output must explain candidate ordering and blocking
constraints. It should name the considered issue set, selection policy,
readiness evidence, dependency disposition, stakeholder overrides, WIP
constraints, and unsupported or missing policy factors. It must distinguish
ranking from feasibility: dependencies determine whether work can proceed
unless policy explicitly says they also affect priority.

Conflict reporting should separate:

- same-precedence or Policy Authority conflicts from Agent Equipment Config;
- Issue Ops semantic conflicts, such as execute mode with blocked external
  disclosure;
- adapter capability conflicts, such as a requested native dependency relation
  on a tracker that only supports fallback records;
- unresolved judgment, such as assignee or priority decisions without policy.

## CLI And MCP Parity

CLI and MCP parity means the same typed contracts exist for deterministic
Issue Ops operation families. The CLI may be the initial executable surface,
but MCP tools must expose equivalent input and output schemas when the tool
surface is published.

Parity covers:

- config validation and effective Issue Ops policy explanation;
- onboarding plan output for first-run, incomplete, interrupted, resume,
  restart, re-onboarding, and revise flows;
- migration preview and migration apply plans;
- compatibility classification and conflict reports;
- dry-run tracker operation plans;
- adapter capability reports;
- issue selection and effective next-work explanation;
- mutation audit output.

Judgment-heavy workflows, such as triage, issue repair, PRD publication, issue
slicing, and agent brief drafting, may live in skills or Agent Profiles. Their
writes still flow through deterministic operation plans and gates.

## Security And Safety

Issue Ops protects public tracker state, notifications, stakeholder workflow,
and private context. Unsafe writes fail closed. External disclosure remains
blocked unless policy allows it. User-global source mutation requires explicit
approval even when discovery can read the surface.

Mutation-capable behavior requires:

- requested behavior set to mutation;
- usable effective policy or an approved plain handoff with equivalent
  semantics;
- external disclosure allowed for externally visible content;
- adapter capability support for the requested operation;
- duplicate or idempotency checks when creation or closure can collide;
- audit output that names operation, target, policy mode, request shape,
  result or failure, fallback, and compensation guidance.

Dry-run output can itself disclose content through logs or chat. Issue Ops
should classify disclosure risk before projecting raw issue bodies, comments,
or local paths into durable evidence.

## Validation And Closeout

Validation covers:

- plain handoff ingestion with shared Config absent;
- promotion of a plain handoff into Agent Equipment Config;
- missing, partial, stale, conflicted, unsafe, and untrusted policy states;
- onboarding state output for first-run, interruption, resume, restart, and
  re-onboarding;
- migration fates for repo-local and user-global Foreign Policy Surface inputs;
- compatibility classification for indirection, generation, adapter behavior,
  and mixed strategies;
- conflict reports and unavailable config-equipment status;
- CLI and MCP parity for operation metadata, schemas, output shapes, side
  effects, and representative calls;
- issue selection explanation and effective next-work output;
- tracker projection updates for issue #13 and downstream blockers.

Closeout for #13 requires this owner spec, bundle references, validator
coverage, security and documentation closeout evidence, Ralph Review cycles
until clean, issue tracker drift correction, and a merged PR that closes #13.

## Non-goals

This design does not implement runtime onboarding, GitHub Projects custom
fields, full GitLab live mutation, live non-GitHub tracker mutation,
policy-doc migration, Config authoring mechanics, Existing Equipment
Onboarding follow-up projection, final Issue Ops packaging, or publication.

Those remain owned by their focused issues: #103 for policy-doc
migration, #93 and #99 for Config authoring mechanics, #121 for onboarding
follow-up projection, and #18 for validation, documentation, packaging, and
publication.
