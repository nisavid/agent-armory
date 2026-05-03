# Gap Resolution and Design Notes

## Purpose

This document explains how the final handoff refactors and corrects earlier drafts.

## Earlier material roles

The earlier handoff materials had overlapping roles:

- `agent_armory_summary.md` was a broad research summary and guideline document.
- `agent_armory_handoff_prompt.txt` was an initial operational prompt.
- `agent_armory_gap_catalog.md` identified missing details.
- `agent_armory_research_addendum.md` restored evidence and implementation nuance.
- `agent_armory_templates_and_repo_strategy.md` introduced more concrete templates.
- `agent_armory_ubiquitous_language_addendum.md` added domain language.
- `agent_armory_harness_catalog_addendum.md` expanded harness coverage.
- `agent_armory_metasmith_followup_addendum.md` added post-Framework Smith tasks.
- `agent_armory_revised_handoff_prompt_v2.txt` combined later instructions.

This final bundle consolidates those roles into a consistent reading path.

## Key corrections

### MCP expansion

Earlier drafts accidentally expanded MCP as “Model Control Plane.” The correct expansion is **Model Context Protocol**.

### OpenClaw release state

Earlier drafts treated OpenClaw 2026.5.2 as simply the current latest release. The current GitHub release page checked on 2026-05-02 shows `2026.5.2-beta.3` as the top prerelease and `2026.4.29` as the latest non-prerelease release.

The final catalog records both.

### Claude Code version evidence

The final bundle records Claude Code 2.1.126 based on Snyk package metadata and requires local verification with `claude --version`, because public npm search results were inconsistent.

### OpenCode version

The final bundle records OpenCode v1.14.33 based on GitHub releases checked on 2026-05-02.

### Cursor evidence

The final bundle uses official Cursor docs and changelog for 3.2, project rules, MCP, CLI behavior, and background agents.

## Restored nuances

### Evidence taxonomy

The final bundle explicitly distinguishes:

- documentation-supported,
- source-supported,
- implementation inference,
- practitioner wisdom,
- hypothesis.

This prevents weak practitioner rules from being treated as facts.

### Skills are not static

The final bundle preserves that skills can include scripts, references, templates, and resources. The distinction is not “skills static, MCP dynamic.” The better distinction is:

```text
Skill = agent-facing procedural package.
MCP = protocolized capability boundary.
```

### Context-providing MCPs blur the boundary

The final bundle keeps the idea that retrieval, memory, docs, logs, metrics, and source search are context-providing tools that participate in the reasoning loop. Their quality depends on result formatting, metadata, pagination, summarization, and context packing.

### Hooks as middleware

The final bundle treats hooks as lifecycle middleware, not as skills or tools. Hooks enforce, observe, inject, rewrite, block, route, or record.

### Agent Profiles

The final bundle standardizes Agent Profile as the cross-harness term for Claude Code subagents, Codex roles, OpenCode agents, Cursor modes/subagents, and OpenClaw configured agents.

### Harness-specific scheduling

The final bundle avoids a single scheduling assumption. It defines an ordered fallback strategy for Periodic Actions.

## Design decisions

### Why split docs

The final bundle separates:

- operational prompt,
- executive brief,
- ubiquitous language,
- evidence,
- architecture,
- decision method,
- harness catalog,
- templates,
- specs,
- repo seed plan,
- gap notes.

This prevents the receiving Agent from treating a single long file as both instruction, background, and specification.

### Why self-contained

The final bundle does not require old drafts. It includes all essential definitions, architecture, method, harness facts, and tasks.

### Why version harness facts

Harnesses change rapidly. Versioned facts plus refresh policy are essential to keep the Framework from going stale.

### Why avoid production-looking stubs

The first Metasmith should not create fake implementations that later Smiths trust. Templates and examples should be clearly marked until tested.

## Remaining uncertainties

Smiths must still verify:

- current installed Claude Code version,
- current installed Codex version,
- whether Codex has durable periodic scheduling beyond goals,
- current Cursor hook semantics,
- current OpenCode scheduling options,
- current Hermes project-plugin security defaults,
- exact OpenClaw stable vs prerelease policy for this Armory.

These uncertainties should be represented in the harness capability catalog.
