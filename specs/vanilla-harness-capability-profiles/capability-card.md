# Capability Card: Vanilla Harness Capability Profiles

Status: Equipment Blueprint
Promotion state: specified

## Purpose

Vanilla Harness Capability Profiles provide source-backed, per-harness
Capability Profiles for the default post-installation and onboarding capability
surface of each supported Agent Harness.

## Vision alignment

This capability supports the Armory's harness lifecycle and self-onboarding
goals. Smiths need current, evidence-backed harness facts before they can place
Agent Equipment responsibilities into the right harness surfaces. The Manager
Core keeps deterministic validation, migration, diffing, and audit behavior in
software, while agent-guided workflows handle judgment-heavy claim triage,
schema pressure, and study design.

## Users

- Human operator: reviews catalog changes, approves controlled effects, and
  decides when residual unknowns are acceptable.
- Forgewright: maintains the Forge capability model, schema, manager, and
  profiling protocol.
- Smith: reads Vanilla Harness Capability Profiles before projecting equipment
  requirements onto harness surfaces.
- Future Outfitter or evaluator: uses the base profiles as inputs to Effective
  Harness Capability Surface and memory-system evaluation work.

## Target harnesses

- Codex: required.
- OpenClaw: required.
- Hermes Agent: required.
- Claude Code: required.
- Cursor: required.
- OpenCode: required.

## Risks

- Security: network scouting, local probing, process execution, and controlled
  profile mutation can expose credentials, alter local state, or over-trust
  unvetted sources if not gated.
- Privacy: live-study artifacts and local observations can capture local paths,
  installed equipment, provider state, prompts, or configuration.
- Reliability: stale claims, untracked unsupported behavior, weak evidence, or
  split authored truth can mislead Smiths.
- Context budget: exhaustive claim analysis is intractable; workflows need
  Capability Claim Triage and pragmatic evidence reuse.
- Human workflow: refresh results must be reviewable and must not silently
  mutate canonical profile files.

## External systems

- First-party harness documentation, changelogs, release pages, and source
  repositories.
- Local harness installations and clean-room profiling fixtures when probing is
  allowed.
- GitHub Issues when residual unknowns, follow-ups, or projected child stories
  are published.

## Side effects

The migration and validation slice performs local repository reads and writes.
Manual refresh adds network reads, scratch/cache writes, controlled profile
updates after explicit apply, and optional local probing. Live-study slices may
invoke controlled harness instances and create fixture-local state. Externally
visible or privileged effects require explicit security/control classification
and operator approval.

## Needed Harness Components

- Skills: local workflow templates for research notes, Capability Claim
  Triage, schema pressure review, manual refresh review, and study-plan/report
  review.
- MCP/tools: none required for the first deterministic slice.
- Hooks: none required for the first deterministic slice.
- Agent Profiles: deferred until live-study fixtures need specialized agents.
- Plugins: deferred.
- Scripts: `tools/harness_capability_profiles.py` Manager Core.
- Config: deferred until Agent Equipment Config can provide shared config.
- Docs: per-harness vanilla profiles, schema docs, research notes, validation
  plan, security/control classification, and closeout evidence.

## Hard rules

- Vanilla Harness Capability Profiles describe harness capability surfaces; they
  do not prescribe how Smiths should use those surfaces.
- Per-harness Vanilla Harness Capability Profiles are the authored structured
  truth; retained aggregate catalog files are rejected as split truth.
- Material profile claims carry stable per-profile claim IDs and traceable
  evidence references.
- Profiles cover the standard surface-family rubric with supported,
  unsupported, unknown, or not-applicable claims.
- Scouting and analysis do not silently mutate canonical profiles.
- Raw scout, live-study, and fixture artifacts are scratch by default.
- Network scouting, local probing, live-study effects, and controlled profile
  mutation require security/control classification before implementation.

## Deterministic checks

- Unit tests for aggregate-to-profile migration.
- Unit tests for Manager Core validation and JSON output.
- Unit tests for profile metadata, standard surface-family coverage, stable
  claim IDs, evidence links, applicability scope, origin, and migration status.
- `tools/harness_capability_profiles.py validate`.
- Live repository validation command produced by the validation boundary
  refactor.
- `git diff --check`.

## Output contract

- `docs/harness-capabilities/vanilla/<harness-id>.toml` for each supported
  harness.
- `docs/harness-capabilities/schema/` for profile schema and migrations.
- `docs/harness-capabilities.md` generated or maintained from validated
  profile facts as the human-facing catalog front door.
- `tools/harness_capability_profiles.py` with stable JSON output for every
  command.
- Local workflow templates under
  `specs/vanilla-harness-capability-profiles/workflows/`.
- Research notes and curated evidence only when findings are recorded.

## Failure modes

- Missing profile coverage fails validation.
- Broken schema, duplicate claim IDs, missing evidence links, or unresolved
  material surface-family entries fail validation.
- Scout or analyze detects drift but no apply is approved; the manager records
  an audit summary and leaves canonical profiles unchanged.
- A claim cannot be verified; the profile records an explicit unknown or
  unsupported claim and routes material follow-up into issues or accepted
  non-blocking closeout.
- A live-study design risks contaminating the investigator harness; the study
  uses a separate controlled instance or records the limitation.

## Evidence

Evidence follows `docs/evidence-taxonomy.md` and the Harness Evidence Source
Policy. First-party sources are the baseline. Local observations, selected
study reports, curated evidence notes, and explicitly marked hypotheses or
unknowns are allowed evidence classes when scoped correctly.

## Open questions

- What exact TOML shape should the first-slice claim-centered schema use?
- Which Manager Core subcommands belong in the first read-only slice beyond
  `migrate` and `validate`?
- Which parts of the Capability Profiling Protocol need machine-readable schema
  in this epic versus prose templates?
