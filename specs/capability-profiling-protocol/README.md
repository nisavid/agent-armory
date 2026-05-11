# Capability Profiling Protocol

Status: Equipment Blueprint
Promotion state: specified

The Capability Profiling Protocol is a descriptive reusable protocol for
studying Capability Surfaces. It supports Vanilla Harness, Effective Harness,
Equipment, clean-room jig, and hypothetical targets without creating separate
terminology for common study concepts.

The protocol does not execute live studies. It defines how to plan, constrain,
record, and report them so later Smiths can decide what a study proves, what it
does not prove, and whether the evidence should affect a Capability Profile.

## Purpose

A Capability Surface claim often depends on more than one state. A harness may
load a component during startup, alter behavior after activation, expose state
during agent invocation, and show reload behavior only after restart. The
protocol makes those states and observations explicit through a Capability
State Graph, then records one or more Capability Analysis Angles for studying
the same claim.

The protocol separates deterministic Manager Core behavior from agent-guided
judgment:

- Manager Core validation checks artifact presence, required fields,
  references, effect gates, control dispositions, and machine-readable shape.
- Agent-guided work selects study targets, compares Capability Analysis
  Angles, interprets observations, assigns confidence, and decides profile
  impact.

Manager Core validation does not execute studies or certify inference-heavy
conclusions; it validates protocol structure, permitted effects, and required
approval references.

## Study Target Declaration

Every study target declaration records:

- target type: `vanilla_harness_surface`, `effective_harness_surface`,
  `equipment_surface`, `clean_room_jig_surface`, or `hypothetical_surface`;
- target scope and target state or Capability State Graph;
- claims under study and required evidence;
- allowed effects and blocked effects;
- available controls, missing controls, and operator preferences;
- advised rigor, selected rigor, and selected-rigor rationale.

The target declaration names what is being studied. It does not state the
study result.

## Capability State Graph

A Capability State Graph is a sequence or directed acyclic graph of
capability-relevant states and transitions. States may describe a harness,
equipment, component, jig, config root, external system, or other
capability-bearing condition. Transitions describe how the study moves between
states.

Observation points attach expected evidence to graph states. A claim may have
multiple observation points, and one observation point may support more than
one claim when the evidence genuinely overlaps.

## Capability Analysis Angles

A Capability Analysis Angle records one way to model, probe, or judge a claim.
Study plans can compare multiple angles for the same claim by recording cost,
control, observation strength, contamination risk, expected confidence, and
why one angle is selected or deferred.

This keeps the first plausible test design from becoming the only accepted
test design.

## Rigor Controls

Rigor axes are provisional and explicit:

- isolation;
- reproducibility;
- harness-state control;
- equipment-state control;
- config control;
- version pinning;
- provider/randomness control where available;
- subject/operator separation;
- network access;
- mutation allowance;
- observation quality.

Advised rigor is the control level implied by the claim, risk, and intended
use. Selected rigor is the actual study choice after cost, access,
operator preference, and jig limitations are applied.

## Effects

Effects are classified separately from rigor. The starter effect taxonomy is:

- `passive_scanning`;
- `active_non_mutating_use`;
- `local_mutation`;
- `profile_mutation`;
- `external_network_access`;
- `external_disclosure`;
- `process_execution`;
- `harness_runtime_state_change`.

Active local probing, mutating studies, process execution, external network
access, harness runtime-state changes, profile mutation, and external
disclosure require a security/control classification reference and an operator
approval reference before the study may proceed.

## Study Reports

A study report records what happened after execution. It distinguishes:

- observed results;
- claim confidence;
- test sufficiency;
- limitations;
- failed controls;
- artifact disposition;
- profile impact.

Reports may be durable project evidence only when they support a profile,
decision, audit, issue, or review surface. Raw transcripts, fixture logs, and
temporary output remain instance-scoped scratch unless explicitly promoted.

## Jig Adequacy Reports

The Standard Clean-Room Profiling Jig is the preferred ideal baseline for
official Vanilla Harness Capability Profiles. A Per-Harness Clean-Room Jig
records how closely a harness can approach that baseline.

Jig adequacy reports use the same protocol vocabulary because a jig is also a
Capability Surface. The minimal machine-readable report classifies controls as
`claimed`, `verified`, `unsupported`, or `unknown`, and records how each limit
affects selected rigor.

## Examples

Representative examples live under
`examples/capability-profiling-protocol/`:

- `vanilla-codex-skill-study-plan.toml`;
- `effective-loadout-memory-study-plan.toml`;
- `vanilla-codex-skill-study-report.toml`;
- `standard-clean-room-jig-adequacy-report.toml`.
