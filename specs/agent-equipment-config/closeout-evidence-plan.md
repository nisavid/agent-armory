# Closeout Evidence Plan: Agent Equipment Config

Status: Equipment Blueprint
Promotion state: planned

This Forge Entry Bundle describes desired behavior only. It does not implement Agent Equipment, publish assets, or provide a runtime config engine.

## Closeout scope

The first #23 change set closes only the contract-first bundle and validator
gate. It does not close the full Agent Equipment Config story.

## Required evidence

Record:

- design decisions resolved through the `grill-with-docs` loop;
- source-shape migration from `specs/agent-equipment-config.md` to
  `specs/agent-equipment-config/`;
- validator and test changes;
- validation commands and results;
- security review scope, artifact disposition, and findings disposition;
- documentation closeout scope and unchanged rationale where applicable;
- child issue projection for follow-on implementation slices.

## Child issue projection

After the bundle lands, #23 should gain child issues for:

- deterministic effective-config engine;
- Issue Tracker Ops plain config and consumer integration;
- onboarding, re-onboarding, resume, and handoff flows;
- harness projection docs and enforcement support;
- audit, migration, and security hardening;
- publication and pressure validation after runtime behavior exists.

Each child issue should name the bundle files it depends on, the expected output
surface, security review trigger, and validation evidence needed for promotion.

## Security closeout

For this change set, security scope covers documentation and validator logic.
The closeout should state whether the action was a Codex Security diff scan or a
documented narrower security review. Raw local scan artifacts are instance
scoped unless a later decision promotes a specific report to a durable neutral
project path.

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
