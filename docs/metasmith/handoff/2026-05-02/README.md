# Agent Armory Final Handoff Bundle

**Status:** proposed final draft  
**As-of date:** 2026-05-02 (America/New_York)  
**Target repository:** `nisavid/agent-armory`  
**Receiving Agent:** the first Metasmith

This bundle consolidates and refactors all prior handoff materials into a uniform, cohesive structure.

It is self-contained. The first Metasmith should not need the earlier drafts. The earlier drafts were consolidated into this set of files, with corrections and missing details restored.

## Reading order

1. `00-metasmith-handoff-prompt.md`
2. `01-executive-brief.md`
3. `02-ubiquitous-language.md`
4. `03-evidence-and-source-map.md`
5. `04-framework-architecture.md`
6. `05-decision-method-and-runbook.md`
7. `06-harness-capability-catalog.md`
8. `07-equipment-templates-and-examples.md`
9. `08-initial-smith-task-specs.md`
10. `09-repository-seed-plan.md`
11. `10-gap-resolution-and-design-notes.md`
12. `harness-capabilities.seed.toml`

## Document roles

- `00-metasmith-handoff-prompt.md` is the operational prompt to give the first Metasmith.
- `01-executive-brief.md` summarizes the assignment and desired outcome.
- `02-ubiquitous-language.md` establishes terms that Smiths and Metasmiths should use.
- `03-evidence-and-source-map.md` defines evidence standards and records sources.
- `04-framework-architecture.md` defines the Agent Equipment Framework.
- `05-decision-method-and-runbook.md` gives the core decision method and capability-creation workflow.
- `06-harness-capability-catalog.md` records harness-specific implementation facts as of this date.
- `07-equipment-templates-and-examples.md` provides templates and examples to seed the Armory.
- `08-initial-smith-task-specs.md` defines the first Smith tasks: Agent Ops, Periodic Actions, and Harness Refresh.
- `09-repository-seed-plan.md` proposes the initial repository structure and acceptance criteria.
- `10-gap-resolution-and-design-notes.md` explains what changed from earlier drafts and why.
- `harness-capabilities.seed.toml` is a structured seed file for the harness capability catalog.

## Important corrections included in this final draft

- MCP means **Model Context Protocol**.
- OpenClaw’s release state is represented carefully: GitHub shows `2026.4.29` as the latest non-prerelease release and `2026.5.2-beta.3` as the current top prerelease at the time checked.
- Claude Code’s version is recorded as `2.1.126` using Snyk package metadata because public npm search results were inconsistent. The receiving agent should verify locally with `claude --version`.
- OpenCode is recorded as `v1.14.33` based on GitHub releases checked on 2026-05-02.
- Cursor is recorded as `3.2` based on the official Cursor changelog.
- Codex is recorded as `0.128.0` stable, with `0.129.0-alpha.2` prerelease noted.
- Hermes Agent is recorded as `v0.12.0`.

## Operating stance

The Framework should not merely create plausible files. It should create a durable method for Smiths to create Agent Equipment while preserving evidence discipline, minimizing model context burden, and using the right harness component for each job.
