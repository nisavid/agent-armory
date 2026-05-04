# Harness Capability Catalog

Status: Forge Seed

This catalog records source-backed harness facts that Smiths may use when designing Agent Equipment. Harness capabilities move quickly, so the catalog states when each fact was checked, what source supports it, and what remains uncertain.

The structured source of truth is [docs/harness-capabilities.toml](harness-capabilities.toml). This Markdown document summarizes the same catalog for humans and Agents.

## Catalog policy

Use this catalog before making harness-specific claims in Forge Canon, Equipment Blueprints, templates, examples, or equipment implementation plans.

Treat every entry as versioned state. A Smith must refresh the relevant harness entry before relying on recently changed scheduling, hook, plugin, MCP, permission, or Agent Profile behavior. Record local CLI observations separately from public source facts.

Use first-party sources where available. Use third-party fallback metadata only when first-party evidence is unavailable or clearly insufficient, and label it as fallback evidence in the TOML entry's source, uncertainty, or refresh notes.

## Refresh summary

Checked at: 2026-05-03T09:25:05-04:00.

The seed refresh used first-party release pages, first-party documentation, and tag-pinned source where available. No local harness binaries, workspace configs, gateways, plugin installs, cloud agents, or automation state were inspected during this refresh.

Documentation indexes can lag behind current release evidence. For version anchors, prefer GitHub releases or official changelogs over generated indexes or secondary metadata.

## Harness matrix

| Harness | Version basis | Checked version | Evidence | Scheduling posture |
| --- | --- | --- | --- | --- |
| Codex | GitHub releases plus first-party OpenAI Codex docs | 0.128.0 stable; 0.129.0-alpha.2 prerelease observed | source-supported | App automations and external schedulers around codex exec; keep stable and prerelease claims separate. |
| Claude Code | Official Claude Code changelog and docs | 2.1.126 | documentation-supported | Routines, Desktop scheduled tasks, and session-scoped scheduled tasks. |
| Cursor | Official Cursor changelog and docs | 3.2 numbered release; changelog state checked through 2026-05-01 | documentation-supported | Cloud Agent Automations with schedule and event triggers. |
| Hermes Agent | GitHub release, pyproject version, and tag-pinned docs | 0.12.0 (v2026.4.30) | source-supported | Cron jobs, gateway cron ticker, curator schedule, hooks, and terminal background processes. |
| OpenCode | GitHub release for `anomalyco/opencode` and first-party docs | 1.14.33 | source-supported | GitHub Actions cron or external schedulers around opencode run; no verified native durable scheduler. |
| OpenClaw | GitHub release, package metadata, and tag-pinned docs | 2026.5.2 | source-supported | Cron jobs, heartbeat turns, hooks, webhooks, and plugin background services. |

## Harness notes

### Codex

Codex supports skills, plugins, MCP servers, hooks, app and connector surfaces, subagents, custom Agent Profiles, permission profiles, app-server APIs, noninteractive `codex exec`, GitHub Action workflows, automations, slash commands, web search, and persisted goals.

Scheduling support includes app automations and external schedulers around noninteractive execution. Hooks, app-server APIs, and plugin APIs still need version-specific checks before they carry hard policy or unattended behavior.

Key sources:

- [Codex 0.128.0 release](https://github.com/openai/codex/releases/tag/rust-v0.128.0)
- [Codex 0.129.0-alpha.2 prerelease](https://github.com/openai/codex/releases/tag/rust-v0.129.0-alpha.2)
- [Codex automations](https://developers.openai.com/codex/app/automations)
- [Codex hooks](https://developers.openai.com/codex/hooks)
- [Codex skills](https://developers.openai.com/codex/skills)
- [Codex plugins](https://developers.openai.com/codex/plugins)

### Claude Code

Claude Code supports skills, custom commands, MCP servers and tools, hooks, subagents, plugins, settings, slash commands, LSP servers, plugin monitors, output styles, and themes.

Scheduling support includes cloud Routines, Desktop scheduled tasks, and session-scoped scheduled tasks. Treat cloud Routines as preview-like infrastructure and verify plugin-loaded agent limits before depending on hooks, MCP servers, or permission modes from plugins.

Key sources:

- [Claude Code changelog](https://code.claude.com/docs/en/changelog)
- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [Claude Code hooks](https://code.claude.com/docs/en/hooks)
- [Claude Code subagents](https://code.claude.com/docs/en/sub-agents)
- [Claude Code scheduled tasks](https://code.claude.com/docs/en/scheduled-tasks)
- [Claude Code Routines](https://code.claude.com/docs/en/routines)

### Cursor

Cursor supports rules, `AGENTS.md`, Agent Skills, MCP servers and tools, hooks, subagents, plugins, CLI configuration, Cloud Agents, Automations, and SDK agents.

Scheduling support centers on Cloud Agent Automations with scheduled and event triggers. The latest numbered release and the latest changelog entry can differ, so record both when version-sensitive equipment depends on Cursor behavior. Review marketplace plugins as third-party code before trusting them.

Key sources:

- [Cursor changelog](https://cursor.com/changelog)
- [Cursor 3.2 changelog entry](https://cursor.com/changelog/04-24-26)
- [Cursor rules](https://cursor.com/docs/rules)
- [Cursor skills](https://cursor.com/docs/skills)
- [Cursor hooks](https://cursor.com/docs/hooks)
- [Cursor Automations](https://cursor.com/docs/cloud-agent/automations)

### Hermes Agent

Hermes Agent supports AgentSkills-compatible skills, agent-managed skills, read-only external skill directories, Skills Hub installs, MCP servers, MCP client toolsets, the Hermes MCP server, gateway hooks, plugin hooks, shell hooks, opt-in plugins, memory and context provider plugins, toolsets, profiles, subagents, delegation, terminal backends, and messaging gateways.

Scheduling support includes cron jobs, a gateway cron ticker, curator scheduling, hooks, and terminal background processes. Profiles are separate state directories, not hard isolation. Delegation is synchronous and not durable if the parent is interrupted.

Key sources:

- [Hermes Agent v2026.4.30 release](https://github.com/NousResearch/hermes-agent/releases/tag/v2026.4.30)
- [Hermes Agent pyproject.toml at v2026.4.30](https://github.com/NousResearch/hermes-agent/blob/v2026.4.30/pyproject.toml)
- [Hermes Agent skills docs](https://github.com/NousResearch/hermes-agent/blob/v2026.4.30/website/docs/user-guide/features/skills.md)
- [Hermes Agent hooks docs](https://github.com/NousResearch/hermes-agent/blob/v2026.4.30/website/docs/user-guide/features/hooks.md)
- [Hermes Agent cron docs](https://github.com/NousResearch/hermes-agent/blob/v2026.4.30/website/docs/user-guide/features/cron.md)
- [Hermes Agent curator docs](https://github.com/NousResearch/hermes-agent/blob/v2026.4.30/website/docs/user-guide/features/curator.md)

### OpenCode

OpenCode supports skills, plugins, plugin hooks, custom tools, MCP servers, primary agents, subagents, command templates, permissions, LSP integration, formatters, instruction files, snapshots, TUI, desktop mode, web mode, server mode, noninteractive `opencode run`, GitHub Action integration, and an ACP server.

Scheduling support comes from GitHub Actions cron or external schedulers around `opencode run`. No first-party native durable scheduler was verified. Keep MCP and plugin surfaces narrow because they can increase context and executable-code risk.

Key sources:

- [OpenCode v1.14.33 release](https://github.com/anomalyco/opencode/releases/tag/v1.14.33)
- [OpenCode docs](https://opencode.ai/docs/)
- [OpenCode skills docs](https://opencode.ai/docs/skills/)
- [OpenCode plugins docs](https://opencode.ai/docs/plugins/)
- [OpenCode agents docs](https://opencode.ai/docs/agents/)
- [OpenCode GitHub docs](https://opencode.ai/docs/github/)

### OpenClaw

OpenClaw supports skills, plugin-shipped skills, native plugins, compatible Codex, Claude, and Cursor bundles, MCP client and server surfaces, tools, hooks, webhooks, channels, model providers, media providers, search providers, multi-agent configs, per-agent skill allowlists, CLI and plugin commands, and configuration.

Scheduling support includes cron jobs with `at`, `every`, cron expressions, and time zones; heartbeat-driven periodic turns; hooks; webhooks; and plugin background services. Compatible bundles are partial bridges, not full harness equivalence. Some plugin changes require Gateway restart.

Key sources:

- [OpenClaw v2026.5.2 release](https://github.com/openclaw/openclaw/releases/tag/v2026.5.2)
- [OpenClaw package.json at v2026.5.2](https://github.com/openclaw/openclaw/blob/v2026.5.2/package.json)
- [OpenClaw features docs](https://github.com/openclaw/openclaw/blob/v2026.5.2/docs/concepts/features.md)
- [OpenClaw skills docs](https://github.com/openclaw/openclaw/blob/v2026.5.2/docs/tools/skills.md)
- [OpenClaw cron docs](https://github.com/openclaw/openclaw/blob/v2026.5.2/docs/automation/cron-jobs.md)
- [OpenClaw hooks docs](https://github.com/openclaw/openclaw/blob/v2026.5.2/docs/automation/hooks.md)

## Periodic Actions projection order

For each harness, choose the first available mechanism that satisfies the desired autonomy, visibility, control, and durability:

1. Native durable scheduler or automation.
2. Native local scheduled task.
3. Active loop or heartbeat.
4. Suitable hook.
5. Inference-driven pre/post task check.

Recommended starting choices:

| Harness | Projection order |
| --- | --- |
| OpenClaw | cron, heartbeat, hooks, then rules or equivalent instructions. |
| Hermes Agent | cron, plugin or gateway hooks, then rules or equivalent instructions. |
| Claude Code | Routines or Desktop scheduled tasks, session scheduled tasks, hooks, then rules or equivalent instructions. |
| Cursor | Automations or background agents, then rules or hooks after verification. |
| Codex | app automations or external schedulers around `codex exec`, then hooks, then rules or equivalent instructions. |
| OpenCode | GitHub Actions cron or external scheduler around `opencode run`, then plugin hooks, then rules or equivalent instructions. |

## Refresh requirement

The catalog is versioned state, not timeless documentation. Refresh the affected harness entry when:

- a Smith spec or implementation depends on a harness capability listed here;
- the source's release or changelog has moved since the checked-at timestamp;
- a capability is marked experimental, preview-like, prerelease, plan-dependent, or locally unobserved;
- local installation state can materially differ from public documentation;
- a downstream change needs a hard security, scheduling, hook, MCP, or plugin claim.

At minimum, a refreshed entry records version or version basis, checked-at timestamp, first-party sources, evidence category, component support, scheduling support, limitations, uncertainty, and local observations when local state was inspected.
