# Validation Plan: Harness Capability Lifecycle Methodology

Status: Equipment Blueprint
Promotion state: specified

## Current design-package validation

Issue #62 is a documentation and issue-projection change. The required
validation before merge-readiness is:

- `python3.14 -m unittest`
- `python3.14 tools/harness_capability_profiles.py validate --json`
- `python3.14 tools/validate_armory_integrity.py --final-closeout --json`
- `git diff --check`

The validation run must use scratch cache or bytecode paths outside committed
truth when the local environment needs them.

## Scenario review

Before closeout, review the pressure scenarios for:

- new capability discovery;
- false cross-harness equivalence;
- compatibility bridges;
- schema pressure;
- deprecation and removal;
- unavailable jig validation;
- implementation projection sequencing;
- security-sensitive lifecycle claims.

This review may be manual in the design package. Later implementation issues
should convert the relevant scenarios into tests or fixtures.

## Documentation validation

The documentation closeout checks:

- the Vanilla Harness Capability Profiles bundle links to this lifecycle
  methodology;
- `docs/harness-capabilities.md` remains Manager-rendered profile summary
  output and is not hand-edited for lifecycle discoverability;
- `CONTEXT.md` contains only durable vocabulary and does not duplicate the
  methodology;
- no durable doc claims that Agent Test Jigs or Harness Test Suites are
  implemented;
- no durable doc adds downstream Smith guidance to Vanilla Harness Capability
  Profiles.

## Security validation

The current change set requires doc-only security closeout:

- compare changed docs against `docs/security/threat-model.md`;
- confirm no executable code, hook, MCP/tool, schema implementation,
  automation, permission change, or local harness invocation was added;
- scan changed docs for accidental secrets, raw local paths, private
  transcripts, and disclosure-prone artifacts;
- confirm future effectful work is routed through scoped issues and TDD.

If implementation enters scope later, the future change set must run the
appropriate Codex Security scan path for executable code, hooks, tools,
permissions, package metadata, secrets handling, network/file/process effects,
or security policy.

## Ralph Review gates

Run Review Until Clean on:

- the design bundle itself;
- Cross-Boundary Coherence across issue #62, child issues #63 through #67,
  specs, validation, security, docs, issue projection, and PR closeout;
- Story Quality across DX, UX, code quality where applicable, architecture,
  robustness against unspecified interactions and attack paths, prior
  pathological workflow lessons, and alignment with `docs/vision.md`.

The latest cycle must have no findings before merge-readiness.

## Future implementation validation

Future Manager Core work should add tests before implementation for:

- lifecycle candidate schema validation;
- evidence-class and disposition enum handling;
- JSON output for candidate, disposition, diff, and audit records;
- precondition hashes and profile mutation gates;
- schema-pressure fixture validation;
- issue-projection dry-run and apply behavior;
- security-control references for effectful or disclosure-prone candidates.

Future Harness Test Suite integration should add tests for:

- accepted Jig result statuses;
- unsupported driver controls;
- fixture and cleanup failures;
- selected-rigor limitations;
- durable evidence promotion from structured result summaries only.
