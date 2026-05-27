# Interface Decision Record: Agent Test Jigs and Harness Testing System

Status: Equipment Blueprint
Promotion state: specified

## Requirement

Issue #61 needs a design package for controlled local testing of harnesses,
equipment, Loadouts, interactions, and Harness Capability claims. The package
must define contracts before implementation so later executable work does not
pick a driver, schema, assertion model, or evidence path prematurely.

## Vision alignment

The decision follows least cognitive privilege from `docs/vision.md`: keep
judgment-heavy design and adjudication in Agents, deterministic execution and
validation in scripts or tools, durable truth in neutral project docs, local
variation in config, and effect enforcement in drivers, sandboxes, approvals,
or hooks.

## Decision

Use an Equipment Design Bundle as the current surface. Project implementation
into scripts, tools, config, hooks, Agent Profiles, and plugins only after the
driver gate and schema contracts are accepted.

## Chosen surface

- Skill: later runner-use and adjudication guidance, not part of this issue.
- MCP/tool: later typed runner and result-inspection operations.
- Hook: later effect and disclosure gates.
- Agent Profile: later latest-GPT high-thinking adjudicator profile.
- Plugin: later portable bundle once components are validated.
- Script: later Jig Runner, validators, driver adapters, and deterministic
  assertions.
- Config: later driver policy, assertion thresholds, model endpoints, and
  calibration profiles.
- Local docs: current design bundle, glossary, ADR, and follow-up issue
  projection.

## Rationale

The design bundle is the lowest reliable surface for this issue because the
main uncertainty is architecture and terminology. Implementing a runner or
driver before the gate would freeze assumptions about local isolation,
inference services, result schemas, and harness lifecycle behavior. Docs and an
ADR make those assumptions inspectable while preserving room for TDD in later
implementation slices.

## Evidence category

- Source-supported: current Armory docs, Capability Profiling Protocol, Harness
  Capability Profile Manager boundaries, and repository threat model.
- Implementation inference: TOML is the preferred behavioral spec direction
  because existing Armory and sibling-repo scenario surfaces use compact
  human-authored TOML.
- Hypothesis: a hybrid local driver may be the best first implementation
  candidate, pending ADR gate application.

## Harness-specific projection

- Codex: first invocation and result-consumption path; driver behavior must
  respect Codex sandbox and approval evidence rather than assume full control.
- OpenClaw: research reference for lifecycle, hooks, cron, heartbeat, and
  plugin-backed control ideas.
- Hermes Agent: research reference for gateway, cron, plugin hooks, and worker
  orchestration ideas.
- Claude Code, Cursor, and OpenCode: later Harness Test Suite consumers after
  source-backed profile refresh and lifecycle methodology work.

## Alternatives rejected

- Implement a runner in #61: rejected because the first driver and schema need
  the design gate first.
- Make the Capability Profiling Protocol the executable runner schema:
  rejected because Study Plans and Study Reports describe studies and evidence,
  while Jig Test Plans are executable input.
- Put the design in `AGENTS.md`: rejected because #61 is equipment-specific
  design, not durable cross-repository agent policy.
- Treat Learned Oracles as final judges: rejected because the Armory needs
  auditable structured disagreement and weakest-reliable-oracle behavior.

## Risks

- Design-only output can drift if follow-up implementation issues are too
  broad or do not carry the driver gate.
- TOML examples may look like a committed schema before validation exists.
- Driver comparison can understate host-specific setup costs.
- Result artifacts can leak private local context if evidence durability is
  not enforced later.

## Maintenance notes

Review this decision when a runner slice is implemented, when a first driver is
selected, when Agent Equipment Config provides threshold and provider config,
or when Harness Capability lifecycle work consumes this bundle.
