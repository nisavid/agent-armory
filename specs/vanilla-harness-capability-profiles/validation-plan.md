# Validation Plan: Vanilla Harness Capability Profiles

Status: Equipment Blueprint
Promotion state: specified

## Prerequisite implementation slice

Use spec-driven TDD for the validation boundary refactor before Manager Core
validation integrates with repository validation.

1. Add failing tests that classify existing validation checks by live boundary.
2. Add failing tests for Armory Integrity Validation and Forge Integrity
   Validation command names, JSON output, and help text.
3. Add failing tests for the absence of transient compatibility markers in
   live surfaces at story closeout.
4. Remove or re-home Seed-only validation checks according to the classified
   boundary.
5. Verify active docs, tests, and closeout commands no longer use Seed
   Validation as the live umbrella.

## Manager Core implementation slice

Use spec-driven TDD for migration and validation before research enrichment.

1. Add failing tests for `tools/harness_capability_profiles.py migrate`.
2. Add failing tests for profile validation and JSON output.
3. Add failing tests for integration from the live repository validation
   command produced by the validation boundary refactor.
4. Implement the Manager Core migration and validation behavior.
5. Migrate the current aggregate TOML into six vanilla profile files.
6. Remove `docs/harness-capabilities.toml` as authored truth.
7. Verify the human-facing summary remains aligned with validated profiles.

## Manager Core checks

The first Manager Core validation covers:

- required profile metadata;
- vanilla profile scope;
- standard surface-family coverage;
- stable per-profile claim IDs;
- supported, unsupported, unknown, and not-applicable claim status;
- evidence references for material claims;
- applicability scope;
- capability origin;
- limitations or uncertainty;
- migration status for aggregate-imported claims;
- stable JSON output for command results.

## Repository validation integration

The live repository validation command produced by the validation boundary
refactor should call or require Manager Core validation instead of duplicating
detailed profile schema rules.

## Research notes and schema pressure slice

Use source-backed research and review before enriching profile claims.

1. Add failing deterministic checks for required research-note sections.
2. Add failing deterministic checks for required schema-pressure report
   sections and disposition values.
3. Record one durable research note for each supported harness.
4. Record a schema pressure report that covers uniform capabilities,
   harness-specific extensions, bespoke capabilities, cross-harness import,
   and memory-like surfaces.
5. Ralph-review the schema pressure report before accepted findings feed the
   profile enrichment slice.

The deterministic checks validate structure and required evidence references;
they do not certify the correctness of inference-heavy conclusions.

The implemented Manager Core validation now requires:

- `specs/vanilla-harness-capability-profiles/research-notes/<harness-id>.md`
  for every supported harness;
- `specs/vanilla-harness-capability-profiles/schema-pressure-report.md`;
- checked-at, version-basis, source set, surface findings, evidence
  classification, compatibility, memory-like, schema-pressure, analysis-angle,
  local-observation, uncertainty, and scratch-disposition sections in every
  research note;
- every standard surface family to appear explicitly in every research note;
- schema-pressure finding rows with affected harnesses, motivating evidence,
  example claim shape, proposed validation rule, migration impact, and one of
  `accepted`, `deferred`, `rejected`, `needs more evidence`, or
  `needs-more-evidence`.

## Profile enrichment and six-profile refresh slice

Use accepted schema pressure findings and current evidence to refresh
canonical profiles.

1. Add failing tests for accepted schema additions and migration behavior.
2. Add failing tests for profile extension shape and standard-family coverage.
3. Add failing tests for summary alignment after aggregate retirement.
4. Refresh all six profiles against current evidence.
5. Run Capability Claim Triage for retained, changed, new, unsupported, and
   unknown material claims.
6. Validate profile schema, migrations, evidence references, claim-id
   stability, summary alignment, and unknown disposition.

The implemented profile enrichment validation now checks:

- stable evidence IDs derived from source URL and claim scope;
- canonical profiles to include non-empty `[[version_observation]]` records
  with `id`, `observed_version`, `checked_at`, `source_url`, `source_kind`,
  `canonical_profile_change`, and `evidence_class` fields, with `source_url`
  and `source_kind` required except for `local_observation` records, where
  they are omitted;
- canonical profiles to include non-empty `[[harness_extension]]` records with
  evidence references and schema-pressure IDs;
- migration-generated base profiles to validate through the migration path
  before canonical enrichment is added;
- refreshed claims to carry Capability Claim Triage, triage rationale,
  install/activation, configuration, reload/update fields, and at least one
  `[[claim.detail]]` row;
- `[[claim.memory_like_surface]]`, `[[claim.automation_surface]]`, and
  `[[claim.compatibility_bridge]]` records when refreshed memory,
  scheduling, or cross-harness compatibility claims require those
  family-specific tables;
- nested claim records to validate their required descriptive fields and
  evidence references.

## Capability Profiling Protocol slice

Use machine-readable study artifacts to support future live-study evidence
without requiring active probes in this slice.

1. Add failing tests for study target declarations.
2. Add failing tests for Capability State Graph structure.
3. Add failing tests for study-plan, study-report, and jig-adequacy schemas.
4. Add representative validated examples for vanilla, effective or
   equipment-composed, and jig-adequacy studies.
5. Validate that mutating or externally disclosing studies require explicit
   security/control classification and approval references.

The implemented Manager Core validation checks:

- required protocol spec and schema-reference files under
  `specs/capability-profiling-protocol/`;
- representative examples under `examples/capability-profiling-protocol/`;
- study target declarations for target type, scope, target state, claims under
  study, required evidence, operator preferences, and selected rigor;
- matching target-level and rigor-table selected rigor;
- provisional rigor axes and required allowed or blocked study-effect lists,
  including effect taxonomy and overlap checks;
- security/control and operator-approval references for effectful studies;
- Capability State Graph state and transition references, including acyclic
  graph shape;
- claim, observation-point, and Capability Analysis Angle references;
- study report plan references, evidence, observed-result,
  claim-assessment, artifact disposition, failed-control, sufficiency, and
  profile-impact structure;
- jig adequacy target type and control rows for claimed, verified,
  unsupported, and unknown controls.

The deterministic checks prove structure and safety gates. They do not execute
studies or certify inference-heavy conclusions.

## Manual refresh and study execution validation

Later stories validate:

- manual refresh staged commands;
- effect gating and approval references;
- stale-plan refusal;
- evidence promotion;
- diff output;
- audit output;
- selected study execution results where live-study evidence supports profile
  claims.

## Closeout and issue projection validation

Before issue projection and story closeout, validate:

- Forge Domain Model Review disposition;
- Ralph-reviewed child-story acceptance criteria;
- issue dependency graph and projected issue contents;
- documentation agreement on live vocabulary and validation boundaries;
- explicit deferment of periodic refresh integration;
- remaining unknowns and follow-up issue links;
- Cross-Boundary Coherence and Story Quality Ralph Review results.

## Required commands

The exact command names are finalized during implementation. Expected closeout
commands include:

```sh
python3.14 -m unittest
python3.14 tools/harness_capability_profiles.py validate --json
python3.14 tools/validate_armory_integrity.py
git diff --check
```

## Completion criteria before returning to Config

Manual refresh is complete enough to unblock Agent Equipment Config when all
six vanilla profiles exist in the new schema, all standard surface families are
covered, material claims have evidence or explicit unsupported/unknown status,
Capability Claim Triage has run against current first-party evidence, pressure
research notes exist, manager validation and audit pass, and remaining
unknowns are issue-tracked or accepted as non-blocking.
