# Closeout Evidence Plan: Vanilla Harness Capability Profiles

Status: Equipment Blueprint
Promotion state: specified

## Durable evidence

Durable closeout evidence includes:

- final Vanilla Harness Capability Profiles;
- profile schema and migration records;
- Manager Core command summaries and JSON-compatible result summaries;
- selected research notes;
- selected study reports when they support material claims;
- audit summaries for manual refresh;
- Forge Domain Model Review disposition;
- issue projection records for the epic and child stories;
- security/control classification updates;
- documentation closeout notes for affected Forge Canon and human-facing docs.

## Scratch evidence

Scratch evidence includes raw scout output, fetched page bodies, fixture logs,
temporary local observations, live-study transcripts, local cache files, and
temporary generated reports. Scratch evidence is summarized by scope,
disposition, and durable conclusion before closeout. It is not committed unless
explicitly promoted as portable review evidence.

## Security closeout

Before merge-readiness for slices that implement network scouting, local
probing, live-study effects, or profile mutation, record the applicable
security/control classification, commands run, findings, fixes, deferred risks,
and any operator-approved limitations.

The migration/validation slice records why no broader security scan is needed
if it only performs local deterministic reads/writes and validation.

## Documentation closeout

Inspect and update affected docs near the end of each cohesive change set:

- `CONTEXT.md`;
- `docs/ubiquitous-language.md`;
- `docs/harness-capabilities.md`;
- `docs/agent-equipment-forge.md`;
- `docs/smith-runbook.md`;
- `specs/vanilla-harness-capability-profiles/`;
- `tools/validate_armory_integrity.py` usage references when changed.

If a plausible doc surface is unchanged, record the rationale in PR or final
closeout.

## Review closeout

Run the repo-required closeout gates from `docs/story-closeout.md` before
treating the epic or a cohesive story as merge-ready. Cross-Boundary Coherence
review must check agreement across profile schema, migrated profiles, manager
behavior, validation output, security/control evidence, docs, and issue
projection.

## Issue projection

After the design grill settles acceptance criteria, project the epic and child
stories into GitHub Issues. The projected issues should preserve blocking
status relative to Agent Equipment Config and distinguish the deferred periodic
refresh integration dependency on Periodic Actions.
