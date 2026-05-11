# Capability Profiling Protocol v1alpha1

Status: Forge Canon

This schema reference describes the minimal machine-readable shape validated
by `tools/harness_capability_profiles.py`. The examples use
`schema_version = "capability-profiling-protocol.v1alpha1"`.

The schema is intentionally structural. It validates references, required
fields, effect approval gates, and control dispositions. It does not run
studies, decide whether a claim is true, or certify inference-heavy
conclusions.

## Common Fields

Every protocol artifact has:

- `schema_version`;
- `artifact_kind`;
- `id`;
- `title`;
- `status`;
- `protocol_version`.

Supported artifact kinds are `study_plan`, `study_report`, and
`jig_adequacy_report`.

## Study Plan

A `study_plan` records:

- `[target]` with type, surface, scope, state reference, claims under study,
  required evidence, operator preferences, and selected rigor;
- `[rigor]` with advised rigor, selected rigor, selected-rigor rationale, and
  the provisional rigor axes;
- `[effects]` with allowed and blocked effects;
- `[controls]` with available controls, missing controls, and operator
  preferences;
- `[approval]` with security/control classification and operator approval
  references when any non-passive effect is allowed;
- `[[state]]` rows for the Capability State Graph;
- `[[transition]]` rows for graph edges;
- `[[claim]]` rows for claims under study;
- `[[observation_point]]` rows linking claims to graph states and expected
  evidence;
- `[[analysis_angle]]` rows comparing Capability Analysis Angles.

Capability State Graph transitions must reference declared states and remain
acyclic. Observation points must reference declared states and claims. Analysis
Angles must reference declared claims and observation points. A study plan
selects one Capability Analysis Angle. It may record multiple angles when the
claim has meaningful alternative study designs. `target.selected_rigor` must
match `[rigor].selected_rigor`. `effects.allowed` and `effects.blocked` are
both required lists, and each effect token must come from the protocol effect
taxonomy.

## Study Report

A `study_report` records:

- `plan_id` and `plan_ref`;
- `[execution]` with execution timestamp, deviations, failed controls, and
  limitations;
- `[[evidence]]` rows for evidence used in the report;
- `[[observed_result]]` rows linking observed outcomes to claims, observation
  points, and evidence;
- `[[claim_assessment]]` rows with claim confidence, test sufficiency,
  limitations, failed controls, and profile impact;
- `[[artifact]]` rows with artifact disposition.

Study reports distinguish observed results, claim confidence, test
sufficiency, limitations, failed controls, artifact disposition, and profile
impact. Evidence references must point to evidence rows in the same report.
`plan_ref` must resolve to a `study_plan` artifact, `plan_id` must match the
referenced plan, and report claim or observation references must point to that
plan's declared claims and observation points.

## Jig Adequacy Report

A `jig_adequacy_report` records a clean-room jig Capability Surface as a study
target. Its target type must be `clean_room_jig_surface`. The artifact also
records:

- `[[state]]` rows for the jig state under review;
- `[[claim]]` rows for jig adequacy claims;
- `[[control]]` rows for claimed, verified, unsupported, and unknown controls.

Each control records `id`, `name`, `category`, `disposition`, `evidence_refs`,
and `selected_rigor_impact`. The report must represent all four dispositions:
claimed, verified, unsupported, or unknown.

## Effect Gate

The only effect that does not require an approval path is `passive_scanning`.
Any study plan that allows `active_non_mutating_use`, `local_mutation`,
`profile_mutation`, `external_network_access`, `external_disclosure`,
`process_execution`, or `harness_runtime_state_change` must include non-empty
`approval.security_classification_ref` and
`approval.operator_approval_ref`.
