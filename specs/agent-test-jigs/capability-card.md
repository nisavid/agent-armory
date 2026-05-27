# Capability Card: Agent Test Jigs and Harness Testing System

Status: Equipment Blueprint
Promotion state: specified

## Purpose

Agent Test Jigs provide controlled local validation for Agent Harnesses, Agent
Equipment, Loadouts, interactions, and Harness Capability claims.

## Vision alignment

This capability supports the Armory vision by moving repeatable parsing,
execution, observation, assertion, evidence capture, and policy gates out of
model memory and into inspectable equipment surfaces. It gives Agents stronger
evidence before they rely on harness capabilities or promote equipment.

## Users

- Human operator: reviews plans, approves effectful studies, and evaluates
  follow-up issue projection.
- Root agent: invokes the Jig Runner, reads structured results, and routes
  durable evidence.
- Specialist agent: designs test plans, adjudicates disagreements, or reviews
  fixture and driver adequacy.
- External system: a local inference service, mock service, harness CLI, or
  future scheduler may participate only through explicit contracts.

## Target harnesses

- Codex: required as the first Codex-mediated invocation path.
- OpenClaw: required research reference and later harness target.
- Hermes Agent: required research reference and later harness target.
- Claude Code, Cursor, and OpenCode: deferred harness targets through Harness
  Capability lifecycle work.

## Risks

- Security: process execution, filesystem writes, network access, external
  disclosure, prompt injection, local credential exposure, and confused-deputy
  behavior.
- Privacy: raw traces, local paths, model transcripts, screenshots, and local
  observations may contain user-specific or private material.
- Reliability: flaky harness behavior, nondeterministic model outputs, fixture
  contamination, cleanup failure, and hidden host-state dependency.
- Context budget: raw logs and oracle outputs can overwhelm later agents unless
  summarized and structured.
- Human workflow: overly broad reports can hide the decision the reviewer needs
  to make.

## External systems

- Local harness processes and CLIs.
- Local filesystem, temporary worktrees, fixture directories, and caches.
- Optional local inference service.
- Optional mock services and network policy controls.
- GitHub Issues for follow-up routing.

## Side effects

- Read-only: fixture reads, profile reads, source inspection, result parsing.
- Local write: temporary fixtures, result artifacts, worktrees, cache entries,
  and later canonical evidence when explicitly promoted.
- Process execution: harness invocation, command scenarios, mock services, and
  inference calls.
- External disclosure: any network call, issue comment, PR body, or durable
  publication that carries test evidence.
- Network write: only when a study plan and approval explicitly allow it.
- Irreversible mutation: out of scope for the design package and unacceptable
  for first-slice implementation.

## Needed Harness Components

- Skills: design, triage, review, and later runner-use skills.
- MCP/tools: future typed runner and result-inspection tools.
- Hooks: future policy gates for effectful or disclosure-prone runs.
- Agent Profiles: future high-thinking adjudicator profile for disagreement
  review.
- Plugins: future portable bundle after runner, drivers, and docs mature.
- Scripts: deterministic runner, validators, and assertion providers.
- Config: thresholds, model endpoints, calibration profiles, driver policy,
  and local effect permissions after Agent Equipment Config is ready.
- Docs: this design bundle, ADRs, result contracts, and follow-up issues.

## Hard rules

- Do not call the jig itself an Agent Harness.
- Prefer deterministic assertions over Learned Oracles.
- Learned Oracle disagreement remains first-class and auditable.
- Driver controls must be explicit; unsupported controls are not silently
  treated as available.
- Raw logs, local paths, model transcripts, and scratch artifacts are
  instance-scoped unless deliberately promoted with durability and disclosure
  rationale.
- Runner output is structured; prose summaries are secondary.

## Deterministic checks

- Future Jig Test Plan schema validation.
- Future result schema validation.
- Future fixture path and symlink checks.
- Future effect approval checks.
- Current design-package closeout through repository tests and Armory Integrity
  Validation.

## Output contract

This issue outputs a design bundle, glossary terms, and ADR. Later
implementation issues output runner commands, driver registrations, structured
JSON results, assertion results, local inference-service calls, and
adjudication handoffs.

## Failure modes

- Unsupported driver control: fail closed for effectful claims and record the
  selected-rigor impact.
- Fixture setup failure: return `fixture_error` with captured setup evidence.
- Sandbox or isolation failure: return `sandbox_error` and block promotion of
  the result as capability evidence.
- Learned Oracle timeout or service failure: return `oracle_error`.
- Learned Oracle disagreement: return `disagreement` for Codex adjudication.
- Cleanup failure: record residue and prevent a clean result status.

## Evidence

- Source-supported: `CONTEXT.md`, Capability Profiling Protocol specs,
  Harness Capability Profile specs, repository threat model, and issue #61.
- Documentation-supported: first-party harness profiles and harness catalog
  summaries already maintained by the Armory.
- Practitioner wisdom: weakest reliable oracle, cognitive-load management, and
  explicit effect gates.
- Hypothesis: the first implementation driver may be a hybrid local driver,
  but ADR 0022 defers selection until the implementation gate applies the
  rubric.

## Open questions

- Which first driver should be implemented after the rubric is applied?
- Which subset of deterministic assertions forms the first useful vertical
  slice?
- Which local inference service contract should be implemented first, and how
  should calibration profiles be stored?
