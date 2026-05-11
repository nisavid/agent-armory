# Interface Decision Record: Vanilla Harness Capability Profiles

Status: Equipment Blueprint
Promotion state: specified

## Requirement

The Forge needs a source-backed, refreshable, per-harness representation of
Vanilla Harness Capability Surfaces so Smiths can reason from current harness
facts without relying on a flat, coarse catalog.

## Vision alignment

The decision supports least cognitive privilege. Deterministic profile
validation, migration, diffing, and audit behavior belongs in software.
Judgment-heavy analysis belongs in agent-guided workflows with explicit
evidence and rationale.

## Decision

Use per-harness Vanilla Harness Capability Profile files, a deterministic
standard-library Python Manager Core, and local agent-guided workflow templates
for research, triage, schema pressure, and manual refresh review.

## Chosen surface

- Skill: local workflow templates for agent-guided analysis steps.
- MCP/tool: none in the first implementation slice.
- Hook: none in the first implementation slice.
- Agent Profile: deferred until live-study fixtures need specialized agents.
- Plugin: deferred.
- Script: `tools/harness_capability_profiles.py`.
- Config: deferred until Agent Equipment Config is available.
- Local docs: bundle docs, per-harness profiles, schema docs, research notes,
  study artifacts, protocol examples, and closeout evidence.

## Rationale

Per-harness profiles keep refresh diffs reviewable and avoid split authored
truth. A single Manager Core script keeps schema loading, profile discovery,
JSON output, migration, validation, and dry-run/apply behavior consistent.
Agent-guided workflows keep inference-bearing work visible instead of hiding
judgment inside a deterministic script.

## Evidence category

Implementation inference and accepted design decision. Profile facts are
authored in per-harness Vanilla Harness Capability Profiles, summarized through
the Harness Capability Catalog, and maintained through Manager Core validation
and manual refresh.

## Harness-specific projection

All six supported harnesses receive one Vanilla Harness Capability Profile:
Codex, OpenClaw, Hermes Agent, Claude Code, Cursor, and OpenCode. Onboarding
variants live inside the profile unless a variant produces a substantially
different vanilla surface.

## Alternatives rejected

- Keep one aggregate TOML file: rejected because it makes review diffs noisy
  and encourages coarse claim structure.
- Keep aggregate TOML as compatibility authored truth: rejected because split
  authored truth invites drift.
- Make the Manager Core the whole manager: rejected because triage, schema
  pressure, source interpretation, and study design require agent inference.
- Encode all future study-plan/report semantics in the first slice: rejected
  because the first slice only needs migration and validation to unlock
  research enrichment.

## Risks

- The first-slice schema can become sticky if migrated claims are treated as
  final rather than marked for schema pressure.
- Agent-guided workflows can drift if they remain prose-only and are not later
  tested or promoted where appropriate.
- Manual refresh can overreach if network scouting or local probing is added
  before security/control classification.

## Maintenance notes

Review this decision when the profile schema stabilizes, when the Capability
Profiling Protocol receives machine-readable plan/report schemas, when Agent
Equipment Config can supply shared config, or when Effective Harness
Capability Surface tooling becomes active.

The current Capability Profiling Protocol surface validates study-plan,
study-report, and jig-adequacy structure through the Manager Core while leaving
inference-heavy study design and claim interpretation to agent-guided review.
