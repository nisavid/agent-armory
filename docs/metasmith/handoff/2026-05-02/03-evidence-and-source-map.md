# Evidence Taxonomy and Source Map

## Purpose

Smiths must avoid presenting plausible-sounding rules as facts. This document defines the evidence categories and records source URLs for harness-specific claims.

## Evidence categories

### Documentation-supported

A claim supported by official documentation or first-party release notes.

Example:

> Claude Code supports scheduled tasks with `/loop`, Desktop tasks, and cloud Routines.

### Source-supported

A claim supported by first-party source code, schema definitions, or repository files.

Example:

> Codex has a stable `hooks` feature flag and a `plugin_hooks` feature.

### Implementation inference

A claim inferred from documented or source-supported behavior, but not explicitly stated as a rule.

Example:

> A Codex post-tool hook can provide feedback to the model and may serve as a retrieval-quality warning layer.

### Practitioner wisdom

A common practice or pattern that appears in implementation experience but lacks rigorous evidence.

Example:

> Narrow MCP servers are usually easier to govern than giant servers.

### Hypothesis

A plausible but unverified claim.

Example:

> Skills will generally produce lower context overhead than MCP tool lists in all clients.

Do not treat hypotheses as rules. Turn them into questions or tests.

## Source map

### Codex

- GitHub releases: https://github.com/openai/codex/releases
- Key release facts checked:
  - `0.129.0-alpha.2` prerelease dated 2026-05-01.
  - `0.128.0` latest stable dated 2026-04-30.
  - `0.128.0` notes mention persisted `/goal` workflows, permission profiles, plugin workflows, plugin-bundled hooks, hook enablement state, MultiAgentV2 configuration, and MCP/plugin edge fixes.

### OpenClaw

- GitHub releases: https://github.com/openclaw/openclaw/releases
- Key release facts checked:
  - `2026.5.2-beta.3` appears as current top prerelease on 2026-05-02.
  - GitHub marks `2026.4.29` as latest non-prerelease release in the fetched release page.
  - `2026.5.2` release-note heading mentions external plugin installation, plugin/ClawHub metadata, Gateway/cache improvements, Control UI/WebChat/Cron reliability, and provider/channel fixes.

### Hermes Agent

- GitHub releases: https://github.com/NousResearch/hermes-agent/releases
- Key release facts checked:
  - Hermes Agent v0.12.0 dated 2026-04-30.
  - Release notes mention the Curator, skill library maintenance, cron ticker, skills/references/templates handling, and self-improvement changes.

### Claude Code

- Official docs:
  - Skills: https://docs.claude.com/en/docs/claude-code/skills
  - Subagents: https://code.claude.com/docs/en/sub-agents
  - Hooks: https://code.claude.com/docs/en/hooks
  - Scheduled tasks: https://code.claude.com/docs/en/scheduled-tasks
  - Routines: https://code.claude.com/docs/en/web-scheduled-tasks
  - Plugins: https://docs.claude.com/en/docs/claude-code/plugins
- Version evidence:
  - Snyk package metadata reported `@anthropic-ai/claude-code@2.1.126` as latest and latest non-vulnerable, published about one day before 2026-05-02.
  - Public npm search results were inconsistent/stale. Smiths should verify locally with `claude --version`.

### Cursor

- Changelog: https://cursor.com/changelog
- Rules docs: https://docs.cursor.com/en/context
- MCP docs: https://docs.cursor.com/context/model-context-protocol
- Background agents docs: https://docs.cursor.com/en/background-agents
- CLI docs: https://docs.cursor.com/en/cli/using
- Key release facts checked:
  - Cursor 3.2 dated 2026-04-24.
  - Release notes mention multitask, async subagents, worktrees, multi-root workspaces, Agents Window.
  - Docs describe project rules in `.cursor/rules`, `AGENTS.md`, MCP, CLI rules, and background agents with isolated Ubuntu VMs.

### OpenCode

- GitHub releases: https://github.com/anomalyco/opencode/releases
- Skills docs: https://opencode.ai/docs/skills
- Plugins docs: https://opencode.ai/docs/plugins/
- Agents docs: https://opencode.ai/docs/agents/
- Config docs: https://opencode.ai/docs/config/
- Key release facts checked:
  - `v1.14.33` latest on 2026-05-02.
  - Release notes mention a fix for custom agents in plugins not loading.
  - Skills docs say OpenCode loads `SKILL.md` on demand via the native skill tool and searches `.opencode/skills`, `~/.config/opencode/skills`, `.claude/skills`, and `.agents/skills`.
  - Plugins docs say plugins extend OpenCode through hooks, custom tools, and integrations. Plugin events include `tool.execute.before`, `tool.execute.after`, session events, permission events, and more.

## Source hygiene rules

Smiths should:

1. prefer official docs and first-party source,
2. record the checked version and date,
3. cite source URLs in capability docs,
4. label evidence category for non-obvious claims,
5. refresh before relying on rapidly moving features,
6. never hide uncertainty when a harness source is stale, inconsistent, or unofficial.

## Review checklist

Before accepting a Smith-created equipment spec, ask:

- Does it distinguish documented facts from inferences?
- Does it name the harness version?
- Does it state which features are required?
- Does it include fallback behavior if a feature is unavailable?
- Does it avoid relying on a feature marked experimental, beta, or preview without a warning?
