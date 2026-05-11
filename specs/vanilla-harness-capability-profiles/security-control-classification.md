# Security and Control Classification: Vanilla Harness Capability Profiles

Status: Equipment Blueprint
Promotion state: specified

## Scope

This classification covers the Harness Capability Profile Manager system:
per-harness Vanilla Harness Capability Profiles, the deterministic Manager
Core, agent-guided manual refresh workflows, evidence scouting, local probing,
Capability Profiling Protocol study artifacts, profile mutation, and audit
output.

## Control classes

### Migration and validation

- Behavior: local repository reads and writes.
- Risk: malformed migration, profile overwrite, stale authored truth, or
  inconsistent summary generation.
- Controls: tests first, dry-run output, explicit apply for mutations, stable
  JSON output, `git diff --check`, and integration with the active repository
  integrity validation command.

### Network scouting

- Behavior: network reads from first-party or allowed fallback sources.
- Risk: source spoofing, stale generated docs, rate limits, changed page shape,
  tracking URLs, or accidental trust in third-party metadata.
- Controls: source-kind labeling, first-party preference, source URL and claim
  scope recording, scratch/cache defaults, and durable evidence export only
  through audit or curated notes.

### Local probing

- Behavior: local filesystem reads, local process execution, harness CLI
  inspection, fixture-local writes, and optional agent invocation.
- Risk: credential exposure, local path disclosure, investigator-harness
  contamination, fixture leakage, or mutation of user harness state.
- Controls: security/control classification before implementation, explicit
  selected-rigor record, separate controlled instances for active tests, and
  scoped local observations.

### Profile mutation

- Behavior: controlled writes to `docs/harness-capabilities/vanilla/` and
  schema paths.
- Risk: unreviewed canonical claim changes, broken claim IDs, lost evidence
  links, or generated-summary drift.
- Controls: staged `scout`, `analyze`, `plan`, `apply`, and `audit`; no
  mutation during scout or analyze; explicit apply; audit summary; tests and
  active repository integrity validation.

### Live-study effects

- Behavior: controlled usage or modification of harness fixtures, possible
  network calls, provider calls, config changes, equipment installation, or
  agent invocations.
- Risk: external disclosure, externally visible mutation, nondeterministic
  results, insufficient isolation, and contamination of the investigator or
  orchestrator agent.
- Controls: Capability Profiling Protocol, Standard Clean-Room Profiling Jig,
  Per-Harness Clean-Room Jig limits, advised and selected rigor, permitted
  effects, Capability State Graph, observation points, study plan, and study
  report.

### Protocol artifact validation

- Behavior: local repository reads of protocol specs and machine-readable study
  examples.
- Risk: treating a structurally valid study as proven, allowing effectful
  studies without an approval path, or promoting scratch observations as
  durable profile evidence.
- Controls: Manager Core structural validation, required effect approval
  references, explicit artifact disposition, and a boundary that keeps claim
  interpretation in agent-guided review rather than deterministic validation.

## Mutation gates

The Manager Core defaults to non-mutating commands. Canonical profile writes
require explicit apply behavior. Network scouting and local probing do not
write canonical profile files. Privileged operations, externally visible
mutations, or user-harness modifications require operator approval and a study
plan that names the permitted effects.

Study plans that allow active non-mutating use, local mutation, profile
mutation, external network access, external disclosure, process execution, or
harness runtime-state changes require both a security/control classification
reference and an operator approval reference.

## Evidence durability

Raw scout output, transcripts, fixture logs, and temporary local observations
are instance-scoped scratch by default. Durable project evidence is limited to
profile claims, curated evidence notes, selected study reports, audit
summaries, and reviewable source or claim summaries.

## Open security questions

- Which network source adapters are safe enough for the first manual refresh
  story?
- Which local probing operations can run against this Codex harness as passive
  observation without contaminating the investigator?
- Which live-study effects require a separate harness instance, container,
  fixture home directory, or provider seed control?
