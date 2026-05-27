# Closeout Evidence Plan: Agent Test Jigs

Status: Equipment Blueprint
Promotion state: specified

## Current issue evidence

The #61 PR body should record:

- branch and PR identifier;
- issue #61 scope statement;
- summary of glossary, design bundle, and ADR changes;
- validation command results;
- Change Set Security Closeout;
- Change Set Documentation Closeout;
- Ralph Review Until Clean results for the design package;
- Cross-Boundary Coherence Ralph Review result;
- Story Quality Ralph Review result;
- follow-up issue links for deferred implementation work.

## Durable project evidence

Durable evidence for this issue consists of:

- `CONTEXT.md` glossary updates;
- this Equipment Design Bundle;
- ADR 0022;
- created follow-up GitHub issues;
- PR body closeout evidence;
- issue closeout comment or closure state.

## Portable review evidence

Portable review evidence may include summarized command outputs, security
scan disposition, documentation closeout rationale, and reviewer findings.
These belong in the PR body or final issue comments, not as raw local logs.

## Instance-scoped scratch

Do not commit or project raw local scratch as project truth:

- terminal transcripts;
- local absolute paths beyond repo-relative references;
- raw model outputs;
- raw runner outputs from future exploratory runs;
- screenshots, audio, video, or trace files;
- temporary worktrees, cache directories, and scan artifact folders.

If any scratch artifact becomes necessary durable evidence, move it to a
neutral project path and record scope, review status, disclosure limits, and
staleness boundaries.

## Follow-up issue projection

Created follow-up issues are listed in dependency order where practical. Native
issue dependencies remain authoritative for blocked work:

- [#162](https://github.com/nisavid/agent-armory/issues/162): Jig Test Plan
  TOML schema and fixture examples;
- [#163](https://github.com/nisavid/agent-armory/issues/163): first Jig Driver
  implementation after ADR gate application;
- [#165](https://github.com/nisavid/agent-armory/issues/165): deterministic
  Assertion Provider library;
- [#164](https://github.com/nisavid/agent-armory/issues/164): Jig Runner CLI
  and structured result output;
- [#166](https://github.com/nisavid/agent-armory/issues/166): local inference
  service adapter and Learned Oracle providers;
- [#167](https://github.com/nisavid/agent-armory/issues/167): Harness Test
  Suite integration with Harness Capability lifecycle work;
- [#168](https://github.com/nisavid/agent-armory/issues/168): Codex
  disagreement adjudication workflow;
- [#169](https://github.com/nisavid/agent-armory/issues/169): optional review
  report or static viewer after structured results exist.

Follow-up issue bodies should be current-state briefs. They should not include
local-only false starts, raw chat history, or scratch paths.

## Closeout checks

Before merging:

- confirm no runner, driver, validator, or provider implementation was added
  in #61;
- confirm follow-up issues carry the implementation work;
- confirm issue #62 can consume the design package or explicitly defer the
  relevant parts;
- confirm raw assertion handoff material is summarized as design input rather
  than copied wholesale into durable docs.
