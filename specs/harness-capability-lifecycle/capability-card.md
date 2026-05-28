# Capability Card: Harness Capability Lifecycle Methodology

Status: Equipment Blueprint
Promotion state: specified

## Purpose

Harness Capability Lifecycle Methodology gives the Armory a repeatable way to
discover, define, reanalyze, refine, deprecate, remove, and project Harness
Capability work after the first Vanilla Harness Capability Profiles exist.

## Vision alignment

This capability supports the Armory vision by keeping current harness facts
evidence-backed, reviewable, and usable by Smiths and Outfitters without
requiring each agent to rediscover every capability boundary from scratch. It
keeps deterministic validation in Manager Core, judgment-heavy comparison in
agent-guided workflows, and high-risk local execution in future Jig-backed
evidence paths.

## Users

- Human operator: reviews profile-impact decisions, approves effectful studies,
  and accepts or redirects projected implementation issues.
- Forgewright: maintains profile schema, Manager Core, workflow, and
  validation boundaries.
- Smith: checks capability lifecycle state before projecting Agent Equipment
  responsibilities onto a harness surface.
- Outfitter: uses future Effective Harness Capability work without confusing
  default profile facts with local configured state.
- Reviewer: checks whether evidence, schema pressure, security, docs, and
  issue projection are coherent before closeout.
- Future automation: consumes structured candidate, disposition, and refresh
  records after implementation issues land.

## Target harnesses

- Codex: required.
- OpenClaw: required.
- Hermes Agent: required.
- Claude Code: required.
- Cursor: required.
- OpenCode: required.
- Later harnesses: allowed only after onboarding creates source-backed Vanilla
  Harness Capability Profile coverage.

## Risks

- Security: hook, MCP/tool, process, network, approval, sandbox, managed
  policy, plugin, and automation claims can cause unsafe equipment projection
  if they are flattened or overgeneralized.
- Privacy: local observations, raw transcripts, screenshots, profile diffs,
  and test artifacts can expose private paths, prompts, tokens, or configured
  equipment.
- Reliability: stale docs, release drift, local-only behavior, compatibility
  bridges, and superficial naming similarity can mislead Smiths.
- Context budget: lifecycle reports can hide decisions under excessive source
  notes and raw logs.
- Human workflow: unclear projection granularity can create giant follow-up
  issues that future agents cannot validate cleanly.

## External systems

- First-party harness docs, changelogs, releases, schemas, source
  repositories, and package metadata.
- GitHub Issues and PRs for projection, review, and closeout.
- Future local harness instances, Jig Drivers, Harness Test Suites, and
  inference-backed assertion providers.
- Future Agent Equipment Config and Periodic Actions surfaces.

## Side effects

The design package performs repository documentation edits and GitHub issue
projection. It does not execute harnesses, mutate profiles, change schema,
write validators, or schedule recurring jobs.

Later implementation work may add:

- read-only source and profile discovery;
- local scratch artifacts for candidate records and analysis reports;
- profile mutation through Manager Core apply gates;
- issue writes for Reflection Findings and follow-up projection;
- controlled local process or network effects when future studies or jigs
  allow them.

## Needed Harness Components

- Skills: lifecycle scouting, grill, design, triage, review, and future
  candidate-routing guidance.
- MCP/tools: future typed Manager Core operations for candidate, disposition,
  schema-pressure, and issue-projection records.
- Hooks: future policy or disclosure gates for effectful studies and profile
  mutation.
- Agent Profiles: future high-thinking reviewer or adjudicator roles for
  cross-harness equivalence and evidence disputes.
- Plugins: deferred until lifecycle tooling is validated and portable.
- Scripts: future standard-library Manager Core slices and validators.
- Config: future effect policy, source policy, cadence, projection, and
  evidence-retention settings after Agent Equipment Config is ready.
- Docs: this design bundle, manual workflow updates, profile schema docs, PR
  closeout, and projected implementation issues.

## Hard rules

- Do not mutate canonical Vanilla Harness Capability Profiles during discovery.
- Do not treat a compatibility bridge as native support for every imported
  component.
- Do not claim cross-harness equivalence when activation, authority, side
  effects, scope, or failure semantics are unknown.
- Do not add downstream Smith instructions to Vanilla Harness Capability
  Profiles.
- Do not treat future jig validation as available until runner, driver, suite,
  and adequacy evidence exist.
- Preserve evidence class and selected-rigor limitations when routing a
  candidate.
- Project implementation work in scoped issues instead of a single broad
  catch-all.

## Deterministic checks

- Future candidate-record schema validation.
- Future lifecycle disposition validation.
- Future Manager Core JSON output validation.
- Future profile-diff and precondition-hash validation.
- Current repository validation through unit tests, Harness Capability Profile
  validation, Armory Integrity Validation, and `git diff --check`.

## Output contract

This issue outputs a design bundle, discoverability links, scoped follow-up
issue projection, and closeout evidence. Later implementation issues output
candidate artifacts, workflow checklists, schema updates, Manager Core
commands, validation fixtures, issue-routing behavior, and optional
Jig-backed evidence integration.

## Failure modes

- False equivalence: route to harness-specific variant or unresolved rather
  than promoting a common capability.
- Stale evidence: require source refresh or record `unknown` disposition.
- Unsupported schema representation: route schema pressure before profile
  mutation.
- Deprecated upstream feature: distinguish deprecated-but-present from removed.
- Unavailable jig path: record limitation and use source refresh or study
  report evidence instead.
- Overbroad follow-up: split by Manager Core, schema, workflow, validation,
  Config, Periodic Actions, Issue Tracker Ops, or jig integration.
- Unsafe artifact publication: keep raw evidence scratch unless durability and
  disclosure review promote it.

## Evidence

- Source-supported: current Armory docs, `CONTEXT.md`, Vanilla Harness
  Capability Profile specs, Capability Profiling Protocol, Agent Test Jigs
  design package, Story Closeout, and repository threat model.
- Official documentation pressure: Codex config, hooks, matcher, transcript,
  sandbox, and approval docs checked on 2026-05-28.
- Practitioner judgment: cognitive-load controls, narrow issue projection, and
  Review Until Clean closeout.
- Hypothesis: Manager Core should eventually own typed lifecycle candidate
  artifacts, pending implementation issue design and TDD.

## Open questions

- Which candidate artifact fields should become the first Manager Core schema?
- Which lifecycle dispositions should become profile-schema fields, if any,
  instead of remaining workflow-only decisions?
- Which future Harness Test Suite result fields are sufficient for profile
  mutation without raw runner output?
