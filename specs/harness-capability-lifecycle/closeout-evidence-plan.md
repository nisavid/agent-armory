# Closeout Evidence Plan: Harness Capability Lifecycle Methodology

Status: Equipment Blueprint
Promotion state: specified

## Current issue evidence

The #62 PR body should record:

- branch and PR identifier;
- issue #62 scope statement;
- child issue #63 through #67 completion mapping;
- summary of design bundle and discoverability changes;
- validation command results;
- Change Set Security Closeout;
- Change Set Documentation Closeout;
- UX and cognitive-load review disposition;
- Ralph Review Until Clean results for the design package;
- Cross-Boundary Coherence Ralph Review result;
- Story Quality Ralph Review result;
- follow-up issue links for implementation work;
- evidence durability classification;
- review-thread state, CI/check state, and rebase-merge readiness.

## Durable project evidence

Durable evidence for this issue consists of:

- this Equipment Design Bundle;
- `CONTEXT.md` glossary update for the methodology name;
- discoverability link from the Vanilla Harness Capability Profiles bundle;
- created follow-up GitHub issues;
- PR body closeout evidence;
- issue closeout comments or closure state.

## Portable review evidence

Portable review evidence may include summarized command outputs, security
review disposition, documentation closeout rationale, scenario review, and
reviewer findings. These belong in the PR body or final issue comments, not as
raw local logs.

## Instance-scoped scratch

Do not commit or project raw local scratch as project truth:

- terminal transcripts;
- local absolute paths beyond repo-relative references;
- raw source caches;
- raw model outputs;
- raw hook payloads;
- raw runner outputs from future exploratory runs;
- screenshots, audio, video, or trace files;
- temporary worktrees, cache directories, and scan artifact folders.

If scratch becomes necessary durable evidence, move it to a neutral project
path and record scope, review status, disclosure limits, and staleness
boundaries.

## Follow-up issue projection

Created follow-up issues:

- [#173](https://github.com/nisavid/agent-armory/issues/173): Manager Core
  lifecycle candidate records and JSON output.
- [#174](https://github.com/nisavid/agent-armory/issues/174): lifecycle
  disposition, schema pressure, and profile mutation gates.
- [#175](https://github.com/nisavid/agent-armory/issues/175): manual refresh
  workflow updates for lifecycle candidate handling.
- [#176](https://github.com/nisavid/agent-armory/issues/176): Issue Tracker
  Ops and Reflection Finding routing.
- [#177](https://github.com/nisavid/agent-armory/issues/177): Harness Test
  Suite result consumption after jig work exists.
- [#178](https://github.com/nisavid/agent-armory/issues/178): Config and
  Periodic Actions integration after #23 and #3 provide their required
  surfaces.

Native issue dependencies remain authoritative for blocked work.

## Closeout checks

Before merging:

- confirm no CLI/API/schema/tooling implementation was added in #62;
- confirm #61 is consumed as design input only;
- confirm #63 through #67 are fully represented by the design package and
  follow-up projection;
- confirm follow-up issues carry implementation work;
- confirm security and documentation closeout are recorded;
- confirm the latest Ralph cycles are clean;
- confirm raw scratch evidence is summarized rather than copied into durable
  docs.
