# Validation Plan: Agent Test Jigs

Status: Equipment Blueprint
Promotion state: specified

This validation plan covers the #61 design package and the later implementation
slices it projects. The current issue validates design coherence, not executable
jig behavior.

## Current design-package validation

Run these checks before merge readiness:

```sh
python3.14 -m unittest
python3.14 tools/harness_capability_profiles.py validate --json
python3.14 tools/validate_armory_integrity.py --final-closeout --json
git diff --check
```

Review gates:

- Change Set Security Closeout against the repository threat model.
- Change Set Documentation Closeout for affected human-facing and agent-facing
  docs.
- Ralph Review Until Clean for this design bundle.
- Cross-Boundary Coherence Ralph Review.
- Story Quality Ralph Review with alignment to `docs/vision.md`.

## Later schema validation

The Jig Test Plan schema implementation should use TDD. First failing tests
should cover:

- required artifact metadata and schema version;
- target declarations for harness, equipment, Loadout, interaction, or
  Capability Surface;
- driver constraint declarations;
- explicit allowed and blocked effects;
- scenario setup, stimulus, expected observations, timeout, and budget fields;
- assertion rows with deterministic and learned provider kinds;
- artifact disposition and evidence durability fields;
- rejection of absolute paths, `..` paths, symlink escapes, and canonical repo
  overwrite paths.

## Later runner validation

Runner tests should verify public CLI behavior through real fixture plans:

- valid deterministic command scenario emits a structured `pass` result;
- command exit mismatch emits `fail` with stdout, stderr, and exit code;
- fixture setup failure emits `fixture_error`;
- driver setup or cleanup failure emits `infra_error` or `sandbox_error`;
- blocked network attempt is represented as an attempted external effect;
- missing local inference service does not collapse learned assertions to pass;
- disagreement remains a structured status with all oracle evidence.

## Later driver validation

First driver tests should prove only the controls the driver actually claims:

- setup creates a clean fixture root;
- teardown removes driver-owned state or records residue;
- command execution captures stdout, stderr, exit code, timing, and resource
  use;
- path restrictions reject root escapes and symlink escapes;
- unsupported controls are visible in driver capability output;
- mock service lifecycle starts and stops deterministically when included.

## Later assertion-provider validation

Deterministic assertion tests should cover exact, normalized, contains,
excludes, regex, structured output, numeric tolerance, state delta, tool-call,
trajectory, policy, and budget assertions as public provider behavior.

Learned Oracle provider tests should cover request schema, response schema,
model and prompt metadata, threshold and calibration metadata, input hashes,
timeout handling, cache behavior, `inconclusive`, `disagreement`, and
`oracle_error`.

## Later Harness Test Suite validation

Harness Test Suite validation should prove:

- one suite can reference multiple Jig Test Plans;
- per-harness evidence is not transferred across harnesses without an explicit
  analysis step;
- unsupported harness signals remain limitations;
- suite output can be consumed by Harness Capability lifecycle work without
  mutating profiles directly.

## Acceptance criteria

The current issue is valid when the design package agrees with `CONTEXT.md`,
`docs/vision.md`, the Capability Profiling Protocol, the repository threat
model, and the follow-up issue projection. Later implementation issues own
executable validation.
