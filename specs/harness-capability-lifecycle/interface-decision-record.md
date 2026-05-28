# Interface Decision Record: Harness Capability Lifecycle Methodology

Status: Equipment Blueprint
Promotion state: specified

## Requirement

Issue #62 needs one coherent methodology that covers new capability discovery,
cross-harness definition, reanalysis and schema refinement, deprecation and
removal, and projection into Manager Core and Forge workflows. The design must
use issue #61 as a future evidence path without claiming implemented jig
behavior.

## Vision alignment

The decision follows least cognitive privilege from `docs/vision.md`: use docs
and issues for current design truth, deterministic Manager Core tooling for
structured validation and mutation, agent-guided workflows for source
interpretation and cross-harness judgment, future jigs for controlled
execution, and security closeout for effectful or disclosure-prone work.

## Decision

Use an Equipment Design Bundle as the current surface. Project executable
behavior into follow-up issues for Manager Core, schema, workflows, validation,
Config, Periodic Actions, Issue Tracker Ops, Reflection Findings, and future
Harness Test Suite integration.

Do not create a CLI, API, schema migration, validator, or ADR in this design
PR. No hard-to-reverse implementation tradeoff is being made here.

## Chosen surface

- Skill: current session uses grill, design, review, security, and TDD policy
  skills; future lifecycle-use skills may be implemented later.
- MCP/tool: future Manager Core commands or Issue Tracker Ops operations after
  schema and workflow work land.
- Hook: future policy or evidence gates around profile mutation or effectful
  studies.
- Agent Profile: future cross-harness reviewer, adjudicator, or security
  reviewer roles.
- Plugin: deferred until lifecycle equipment is validated and portable.
- Script: future standard-library Manager Core slices and validators.
- Config: future Agent Equipment Config settings for source policy, cadence,
  effect policy, evidence retention, and projection.
- Local docs: current design bundle, profile-bundle discoverability, and
  follow-up issue projection.
- GitHub Issues: implementation tracking and closeout state.

## Rationale

The main uncertainty is methodology and issue/workflow decomposition, not
syntax. Implementing a Manager Core slice before the lifecycle phases are
settled would freeze artifact names, schema fields, and mutation semantics too
early. A design bundle keeps the current rules inspectable and lets future
implementation slices apply TDD around narrow contracts.

An ADR is not warranted because this package does not pick a durable runtime,
schema format, storage model, driver, or security enforcement mechanism. It
records a reversible design surface and issue projection.

## Evidence category

- Source-supported: current repository docs and specs.
- Official documentation-supported: Codex docs checked on 2026-05-28 for
  config precedence, hooks, matcher behavior, hook input stability, and sandbox
  or approval controls.
- Implementation inference: future Manager Core should own deterministic
  candidate and disposition validation because current profile validation
  already lives there.
- Hypothesis: future profile lifecycle automation should use Periodic Actions
  only after Agent Equipment Config and Periodic Actions are implemented.

## Harness-specific projection

- Codex: pressure case for hooks, project trust, command handlers, matcher
  support, transcript instability, sandbox, and approval semantics.
- Claude Code: pressure case for cloud routines, desktop scheduled tasks,
  session scheduled tasks, hooks, skills, MCP, and plugin limits.
- Cursor: pressure case for changelog-backed Cloud Agent automations,
  marketplace and team-plan scope, MCP, hooks, and rules.
- Hermes Agent: pressure case for gateway, cron, no-agent mode, plugin hooks,
  Kanban workers, and release-backed lifecycle facts.
- OpenCode: pressure case for external scheduling, plugin hooks, plan-mode
  security fixes, and unresolved reload semantics.
- OpenClaw: pressure case for cron, heartbeat, hooks, compatible bundles,
  plugin lifecycle, and runtime config snapshots.

## Alternatives rejected

- Implement lifecycle Manager Core in #62: rejected because the plan explicitly
  limits this PR to design and projection, and future code requires TDD.
- Add new profile statuses now: rejected because lifecycle dispositions can be
  workflow decisions until schema pressure proves fields are needed.
- Add downstream Smith guidance to Vanilla Harness Capability Profiles:
  rejected because profiles are descriptive records, not equipment projection
  recipes.
- Treat #61 as implemented validation: rejected because #61 delivered a design
  package and follow-up issues, not a runner, driver, schema, or Harness Test
  Suite.
- Create one broad implementation issue: rejected because it would mix Manager
  Core, schema, workflows, validation, Config, Periodic Actions, Issue Tracker
  Ops, and jig integration.

## Risks

- Design-only rules can drift unless follow-up issues carry concrete
  acceptance criteria.
- Lifecycle dispositions may be mistaken for profile schema statuses.
- Reviewers may over-trust official docs without preserving version, trust,
  plan, and local-state scope.
- Future automation may publish raw evidence if durability and disclosure
  controls are not implemented.

## Maintenance notes

Review this decision when a lifecycle candidate schema is implemented, when
profile schema fields are proposed for lifecycle dispositions, when Harness
Test Suite output becomes available, when Config and Periodic Actions own
refresh execution, or when a new harness onboarding case exposes missing
lifecycle phases.
