# Closeout Evidence Plan: Agent Equipment Config

Status: Equipment Blueprint
Promotion state: planned

This Forge Entry Bundle describes desired behavior and includes the first
standard-library runtime engine slice for effective-config, config-diff,
diagnostics, plain handoff promotion, authority checks, and projection
classification. It does not implement Agent Equipment beyond this runtime
slice, publish assets, resolve secrets, mutate source config, mutate external
systems, or implement harness controls.

## Closeout scope

The first #23 change set closes the contract bundle, validator gate, and first
portable runtime engine slice. It does not close the full Agent Equipment Config
story.

## Required evidence

Record:

- design decisions resolved through the `grill-with-docs` loop;
- source-shape migration from `specs/agent-equipment-config.md` to
  `specs/agent-equipment-config/`;
- validator and test changes;
- deterministic effective-config engine evidence through
  `python3.14 -m unittest tests.test_agent_equipment_config`;
- validation commands and results;
- security review scope, artifact disposition, and findings disposition;
- documentation closeout scope and unchanged rationale where applicable;
- child issue projection for follow-on implementation slices.
- focused security review conclusion for executable parsing, merge, diff,
  migration preview, plain handoff, authority, projection-classification, and
  secret-reference behavior.
- Change Set Security Closeout for the runtime slice, including scope, action
  performed, artifact durability classification, finding disposition, fixes,
  suppressions, deferments, or explicit non-applicability notes.
- Change Set Documentation Closeout for affected agent-facing and human-facing
  docs, including updated surfaces or a no-change rationale for each plausible
  affected surface.
- Full `docs/story-closeout.md` gate order before merge-readiness, including
  Intent Model Refresh, scope/validation coherence, security closeout,
  documentation closeout, projection draft or pending-projection rationale,
  Reflection Finding disclosure/routing, latest clean Cross-Boundary Coherence
  and Story Quality Ralph Review cycles, final validation, and publication
  readiness checks.

## Child issue projection

After the bundle lands, #23 should gain child issues for:

- Issue Tracker Ops plain config and consumer integration;
- onboarding, re-onboarding, resume, and handoff flows;
- harness projection docs and enforcement support;
- audit, migration, and security hardening;
- publication and pressure validation after runtime behavior exists.

Each child issue should name the bundle files it depends on, the expected output
surface, security review trigger, and validation evidence needed for promotion.

## Security closeout

For this change set, security scope covers documentation, validator logic, and
the portable runtime parser and merge engine slice. The closeout should state
whether the action was a Codex Security diff scan or a documented narrower
security review. Raw local scan artifacts are instance scoped unless a later
decision promotes a specific report to a durable neutral project path.

## Documentation closeout

Inspect affected agent-facing and human-facing docs before closeout:

- `AGENTS.md`
- `CONTEXT.md`
- `docs/ubiquitous-language.md`
- Forge Canon under `docs/`
- `specs/`
- `templates/`
- `examples/`
- validator tests and closeout/security docs when changed

Update stale references to the old flat Config spec path, or record why no
change is needed.

## Review closeout

Before treating the branch as merge-ready, run the repo-required review loops
from `docs/story-closeout.md`, including Cross-Boundary Coherence and Story
Quality Ralph Review, with reviewer guidance for agent-facing docs, human-facing
docs, skill-like instructions, Diataxis structure, and clear prose where those
surfaces are affected.
