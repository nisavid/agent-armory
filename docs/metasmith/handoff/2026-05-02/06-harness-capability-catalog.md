# Harness Capability Catalog

**Checked at:** 2026-05-02, America/New_York

This catalog records implementation-contingent harness facts. Harnesses change rapidly. Smiths must refresh this catalog before relying on a feature.

## Summary matrix

| Harness | Version basis | Current checked version |
|---|---|---|
| Codex | GitHub releases | 0.128.0 stable; 0.129.0-alpha.2 prerelease |
| OpenClaw | GitHub releases | 2026.4.29 latest non-prerelease; 2026.5.2-beta.3 top prerelease |
| Hermes Agent | GitHub releases | v0.12.0 |
| Claude Code | Snyk package metadata + official docs | 2.1.126, verify locally |
| Cursor | Official changelog | 3.2 |
| OpenCode | GitHub releases | v1.14.33 |

## Codex

### Version

- Stable: 0.128.0.
- Prerelease: 0.129.0-alpha.2.

### Center of gravity

Codex is a coding-agent harness with CLI, app-server/GUI/IDE integration, plugins, skills, MCP support, hooks, permission profiles, sandboxing, and emerging multi-agent/goal workflows.

### Component support

- Skills: supported.
- MCP/tools: supported.
- Hooks: supported. `hooks` is the stable feature. `codex_hooks` is a legacy alias.
- Plugin hooks: supported and increasingly important; verify exact version behavior before depending on them.
- Agent Profiles: Codex agent roles are Agent Profiles.
- Plugins: supported.
- Scheduling: persisted goals exist, but durable periodic scheduling should be verified for the installed version.

### Notable facts

Release notes for 0.128.0 mention:

- persisted `/goal` workflows,
- app-server APIs,
- model tools,
- runtime continuation,
- expanded permission profiles,
- marketplace installation,
- plugin-bundled hooks,
- hook enablement state,
- external-agent config import,
- MultiAgentV2 configuration,
- MCP/plugin cleanup and metadata fixes.

### Smith strategy

Use Codex skills for procedural knowledge and repo workflows.

Use Codex hooks for hard policy around tools, permission requests, and post-tool feedback.

Use MCP for typed external capabilities.

Use Codex Agent Profiles for specialist subagents.

Use plugins to bundle skills, hooks, MCPs, and profiles.

### Caveats

- Verify installed version with local CLI.
- Verify `plugin_hooks` semantics before using them as hard policy.
- Verify scheduling primitives before implementing Periodic Actions.

## OpenClaw

### Version

- Latest non-prerelease shown by GitHub release page: 2026.4.29.
- Top prerelease shown by GitHub release page: 2026.5.2-beta.3.
- The prerelease notes include a `2026.5.2` heading.

### Center of gravity

OpenClaw is a local-first personal-assistant gateway and control plane. It emphasizes sessions, channels, routing, tools, events, skills, plugins, companion apps, sandboxing, memory, cron, hooks, and runtime harnesses.

### Component support

- Skills: strong, with progressive disclosure and load-time gating.
- MCP: strong. It can act as an MCP server and maintain MCP server definitions for runtime adapters.
- Hooks: strong. Internal hooks and plugin hooks exist.
- Agent Profiles: configured agents and runtime policies are Agent Profile-like.
- Plugins: very broad.
- Scheduling: strong through cron and heartbeat-style background behavior.

### Notable facts

The 2026.5.2 prerelease notes mention external plugin installation, plugin/ClawHub metadata, Gateway/cache improvements, Control UI/WebChat/Cron reliability, and provider/channel fixes.

### Smith strategy

OpenClaw is a strong target for Agent Ops and Periodic Actions.

Use:

- plugins for broad bundles,
- skills for procedure,
- hooks for policy and routing,
- cron for periodic actions,
- heartbeat as fallback,
- gateway config for durable settings.

### Caveats

- Do not treat one OpenClaw gateway as hostile multi-tenant isolation.
- Preserve its personal-assistant trust model.
- Distinguish stable release from prerelease when generating equipment.

## Hermes Agent

### Version

- Hermes Agent v0.12.0, release dated 2026-04-30.

### Center of gravity

Hermes Agent is a self-improving personal agent/gateway with persistent memory, skills, plugins, MCP integration, cron scheduling, messaging surfaces, toolsets, and a learning loop.

### Component support

- Skills: strong.
- MCP: strong.
- Hooks: strong, with gateway hooks, plugin hooks, and shell hooks.
- Agent Profiles: personality/toolset/delegation presets are Agent Profile-like.
- Plugins: strong Python plugin system.
- Scheduling: strong through cron.

### Notable facts

The v0.12.0 release notes mention the Curator, a background agent on the gateway’s cron ticker, skill library grading/pruning/consolidation, references/templates handling, and self-improvement changes.

### Smith strategy

Hermes is an excellent target for Agent Ops and Periodic Actions.

Use cron first for periodic work.

Use plugin `pre_tool_call` or shell hooks for blocking where possible.

Use skill config for non-secret skill-specific settings.

### Caveats

- Verify project-local plugin defaults before relying on project plugins.
- Preserve user approval around automations in unconfigured repos.

## Claude Code

### Version

- Package version checked: 2.1.126 according to Snyk metadata.
- Official docs should be treated as the primary source for behavior.
- Verify locally with `claude --version`.

### Center of gravity

Claude Code is a coding harness spanning CLI, desktop, IDE, web/cloud, routines, skills, subagents, hooks, MCP, permissions, and plugins.

### Component support

- Skills: strong. Skills are discovered from personal, project, and plugin sources.
- MCP: strong. MCP tools can be used by the main Agent and subagents.
- Hooks: very strong. Supports command, HTTP, MCP tool, prompt, and agent hooks.
- Agent Profiles: Claude Code subagents are Agent Profiles.
- Plugins: strong. Plugins can provide commands, agents, hooks, skills, and MCP servers.
- Scheduling: strong. Supports `/loop`, scheduled tasks, Desktop scheduled tasks, and cloud Routines.

### Notable facts

Claude docs say:

- subagents have separate context windows, custom prompts, tool access, and independent permissions;
- project subagents live in `.claude/agents/`, user subagents in `~/.claude/agents/`;
- Claude Code hooks include events such as PreToolUse, PostToolUse, UserPromptSubmit, Stop, SubagentStop, PreCompact, and SessionStart;
- scheduled tasks require Claude Code v2.1.72 or later;
- scheduling options include cloud tasks, desktop tasks, and `/loop`;
- Routines are research preview and run on Anthropic-managed infrastructure.

### Smith strategy

Claude Code is a strong target for the Framework.

Use:

- skills for complex reusable procedures,
- subagents as Agent Profiles,
- hooks for policy and verification,
- MCP for external integrations,
- Routines or scheduled tasks for Periodic Actions.

### Caveats

- Routines are research preview.
- `/loop` is session-scoped and expires after seven days.
- Verify plugin-provided subagent limitations before relying on plugin-scoped permissions or MCP config.

## Cursor

### Version

- Cursor 3.2, changelog dated 2026-04-24.

### Center of gravity

Cursor is an IDE and agent execution runtime with foreground agents, CLI agent, rules, MCP, background agents, cloud agents, automations, plugins/marketplace, subagents, worktrees, multi-root workspaces, and an Agents Window.

### Component support

- Rules: strong. `.cursor/rules` and `AGENTS.md` are key project-policy surfaces.
- Skills: present in current ecosystem, but verify exact format and discovery before relying on them.
- MCP: strong. Cursor supports stdio, SSE, and Streamable HTTP.
- Hooks: less clearly documented in fetched sources; verify before using as hard policy.
- Agent Profiles: custom modes, background agents, cloud agents, and subagents are Agent Profile-like.
- Plugins: marketplace/MCP apps exist.
- Scheduling: strong through Automations and cloud/background agent triggers.

### Notable facts

Cursor docs say:

- project rules live in `.cursor/rules`, are version-controlled, and can be Always, Auto Attached, Agent Requested, or Manual;
- Cursor supports `AGENTS.md` as a simple instruction format;
- Cursor CLI supports the same rules system and respects `mcp.json`;
- background agents run in isolated Ubuntu-based machines with internet access and can auto-run terminal commands;
- Cursor 3.2 introduced multitask with async subagents, improved worktrees, and multi-root workspaces.

### Smith strategy

For Cursor, project rules are the safest default projection for framework guidance and repo-local policy.

Use MCP for external capabilities.

Use custom modes/subagents/background agents as Agent Profiles.

Use Automations for Agent Ops and Periodic Actions when cloud execution is acceptable.

### Caveats

- Background agents can auto-run commands and have internet access. Treat them as higher risk.
- Verify hook support before depending on hooks for hard policy.

## OpenCode

### Version

- OpenCode v1.14.33 latest on 2026-05-02.

### Center of gravity

OpenCode is an open-source provider-agnostic coding agent with TUI, desktop beta, client/server architecture, built-in agents, configurable agents, subagents, skills, MCP, plugins, permissions, LSP, and config layering.

### Component support

- Skills: strong. `SKILL.md` files are loaded on demand via the native `skill` tool.
- MCP: strong.
- Hooks: strong through plugins.
- Agent Profiles: strong. OpenCode supports agents and subagents.
- Plugins: strong. Plugins extend OpenCode with hooks, custom tools, and integrations.
- Scheduling: no verified first-class durable scheduler. Use plugins, hooks, or external schedulers.

### Notable facts

OpenCode docs say:

- skills are discovered in `.opencode/skills`, `~/.config/opencode/skills`, `.claude/skills`, and `.agents/skills`;
- skill frontmatter recognizes `name`, `description`, `license`, `compatibility`, and `metadata`;
- OpenCode lists skills in the native `skill` tool description and loads them on demand;
- plugins can load from `.opencode/plugins`, global config, or npm;
- plugin events include `tool.execute.before`, `tool.execute.after`, session events, permission events, TUI events, and more;
- release v1.14.33 fixed custom agents in plugins not loading.

### Smith strategy

Use:

- `.opencode/skills` for skills,
- `opencode.json` for MCP/config/agents/permissions,
- `.opencode/plugins` for hooks and custom tools,
- agent Markdown or config for Agent Profiles.

For Periodic Actions, prefer a plugin or external scheduler if available. Otherwise use hooks or inference-driven checks.

### Caveats

- Confirm exact plugin and scheduling support locally.
- Large MCP servers can create context pressure; keep MCP surfaces narrow where possible.

## Periodic Actions projection order

For each harness, choose the first available mechanism:

1. native durable scheduler or automation,
2. native local scheduled task,
3. active loop or heartbeat,
4. suitable hook,
5. inference-driven pre/post task check.

Recommended starting choices:

- OpenClaw: cron → heartbeat → hooks → rules.
- Hermes: cron → plugin/gateway hooks → rules.
- Claude Code: Routines/Desktop scheduled tasks → `/loop` → hooks → rules.
- Cursor: Automations/background agents → rules/hooks after verification.
- Codex: verify goals/scheduling → hooks → rules.
- OpenCode: plugin/external scheduler → hooks → rules.

## Refresh requirement

The Armory must treat this catalog as versioned state.

At minimum, track:

- version,
- checked-at timestamp,
- sources,
- skills support,
- MCP support,
- hook support,
- Agent Profile support,
- plugin support,
- scheduling support,
- limitations,
- evidence level.

When depended-on capabilities change, create a high-priority issue or issue candidate.
