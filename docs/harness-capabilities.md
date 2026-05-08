# Harness Capability Catalog

Status: Forge Canon

This catalog is the human-facing front door for source-backed Vanilla Harness Capability Profiles that Smiths may use when designing Agent Equipment. Harness capabilities move quickly, so each profile states when its facts were checked, what source supports them, and what remains uncertain.

The structured source of truth is `docs/harness-capabilities/vanilla/`. Each supported harness has one per-harness Vanilla Harness Capability Profile. This Markdown document summarizes the validated profiles for humans and Agents.

The first-slice schema reference is [Vanilla Harness Capability Profile v1alpha1](harness-capabilities/schema/vanilla-profile-v1alpha1.md).

## Catalog policy

Use this catalog before making harness-specific claims in Forge Canon, Equipment Blueprints, templates, examples, or equipment implementation plans.

Treat every profile as versioned state. A Smith must refresh the relevant harness profile before relying on recently changed scheduling, hook, plugin, MCP, permission, or Agent Profile behavior. Record local CLI observations separately from public source facts.

Use first-party sources where available. Use third-party fallback metadata only when first-party evidence is unavailable or clearly insufficient, and label it as fallback evidence in the profile's source, uncertainty, or refresh notes.

## Refresh summary

Checked at: 2026-05-03T09:25:05-04:00.

The profiles preserve source-backed version, component, scheduling, limitation, uncertainty, refresh-note, and local-observation fields. No local harness binaries, workspace configs, gateways, plugin installs, cloud agents, or automation state were inspected during the migrated seed refresh.

Documentation indexes can lag behind current release evidence. For version anchors, prefer GitHub releases or official changelogs over generated indexes or secondary metadata.

## Harness matrix

| Harness | Profile | Version basis | Checked version | Evidence | Scheduling posture |
| --- | --- | --- | --- | --- | --- |
| Codex | [Codex profile](harness-capabilities/vanilla/codex.toml) | GitHub releases for openai/codex, plus first-party OpenAI Codex docs. | 0.128.0 stable; 0.129.0-alpha.2 prerelease observed | source-supported | App automations and external schedulers around codex exec; keep stable and prerelease claims separate. |
| Claude Code | [Claude Code profile](harness-capabilities/vanilla/claude_code.toml) | Official Claude Code changelog entry dated 2026-05-01, with first-party documentation for capabilities. | 2.1.126 | documentation-supported | Routines, Desktop scheduled tasks, and session-scoped scheduled tasks. |
| Cursor | [Cursor profile](harness-capabilities/vanilla/cursor.toml) | Official Cursor changelog and first-party docs. | 3.2 numbered release; changelog state checked through 2026-05-01 | documentation-supported | Cloud Agent Automations with schedule and event triggers. |
| Hermes Agent | [Hermes Agent profile](harness-capabilities/vanilla/hermes_agent.toml) | GitHub latest release v2026.4.30 and tag-pinned first-party docs. | 0.12.0 (v2026.4.30) | source-supported | Cron jobs, gateway cron ticker, curator schedule, hooks, and terminal background processes. |
| OpenCode | [OpenCode profile](harness-capabilities/vanilla/opencode.toml) | GitHub latest release for anomalyco/opencode and first-party OpenCode docs. | 1.14.33 | source-supported | GitHub Actions cron or external schedulers around opencode run; no verified native durable scheduler. |
| OpenClaw | [OpenClaw profile](harness-capabilities/vanilla/openclaw.toml) | GitHub latest non-prerelease v2026.5.2 and tag-pinned source/docs. | 2026.5.2 | source-supported | Cron jobs, heartbeat turns, hooks, webhooks, and plugin background services. |

## Harness notes

### Codex

The [Codex profile](harness-capabilities/vanilla/codex.toml) preserves source-backed component, scheduling, limitation, uncertainty, refresh-note, source, and local-observation records.

Scheduling support: App automations and external schedulers around codex exec; keep stable and prerelease claims separate.

Limitations: Hooks require the relevant hook feature support and should not be treated as a complete enforcement boundary without verification. Some app-server and plugin APIs remain experimental, and unattended automations still run under sandbox and approval constraints.

Key sources:

- [stable release version, release date, and release notes](https://github.com/openai/codex/releases/tag/rust-v0.128.0)
- [latest observed prerelease version](https://github.com/openai/codex/releases/tag/rust-v0.129.0-alpha.2)
- [Codex change history](https://developers.openai.com/codex/changelog)
- [skill support](https://developers.openai.com/codex/skills)
- [plugin support](https://developers.openai.com/codex/plugins)
- [plugin authoring support](https://developers.openai.com/codex/plugins/build)

### Claude Code

The [Claude Code profile](harness-capabilities/vanilla/claude_code.toml) preserves source-backed component, scheduling, limitation, uncertainty, refresh-note, source, and local-observation records.

Scheduling support: Routines, Desktop scheduled tasks, and session-scoped scheduled tasks.

Limitations: Session-scoped scheduled tasks require a supporting Claude Code version and expire after a bounded period. Routines are preview-like cloud infrastructure. Desktop scheduled tasks require the Desktop app and an awake machine. Plugin-loaded agents can have restrictions on hooks, MCP servers, and permission modes.

Key sources:

- [latest Claude Code version and release date](https://code.claude.com/docs/en/changelog)
- [first-party changelog mirror](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)
- [skill support](https://code.claude.com/docs/en/skills)
- [MCP support](https://code.claude.com/docs/en/mcp)
- [hook support](https://code.claude.com/docs/en/hooks)
- [subagent support](https://code.claude.com/docs/en/sub-agents)

### Cursor

The [Cursor profile](harness-capabilities/vanilla/cursor.toml) preserves source-backed component, scheduling, limitation, uncertainty, refresh-note, source, and local-observation records.

Scheduling support: Cloud Agent Automations with schedule and event triggers.

Limitations: Cloud Agent execution and some hooks are plan- or environment-dependent. Slack triggers can be limited by channel type. Parallel subagents increase token and cost pressure. Marketplace plugins should be reviewed as third-party code before trusted use.

Key sources:

- [latest official changelog state](https://cursor.com/changelog)
- [Cursor 3.2 numbered release](https://cursor.com/changelog/04-24-26)
- [latest observed unnumbered changelog entry](https://cursor.com/changelog/05-01-26)
- [rules and AGENTS.md support](https://cursor.com/docs/rules)
- [Agent Skills support](https://cursor.com/docs/skills)
- [MCP support](https://cursor.com/docs/mcp)

### Hermes Agent

The [Hermes Agent profile](harness-capabilities/vanilla/hermes_agent.toml) preserves source-backed component, scheduling, limitation, uncertainty, refresh-note, source, and local-observation records.

Scheduling support: Cron jobs, gateway cron ticker, curator schedule, hooks, and terminal background processes.

Limitations: Profiles are separate state directories, not hard isolation boundaries. Cron jobs cannot recursively create cron jobs. Some workdir jobs are sequential because process cwd is global. Delegated subagents are synchronous and not durable if the parent is interrupted. Project plugins require explicit enablement.

Key sources:

- [release version, date, and release notes](https://github.com/NousResearch/hermes-agent/releases/tag/v2026.4.30)
- [package version](https://github.com/NousResearch/hermes-agent/blob/v2026.4.30/pyproject.toml)
- [documentation index](https://hermes-agent.nousresearch.com/docs/llms.txt)
- [skill support](https://github.com/NousResearch/hermes-agent/blob/v2026.4.30/website/docs/user-guide/features/skills.md)
- [MCP support](https://github.com/NousResearch/hermes-agent/blob/v2026.4.30/website/docs/user-guide/features/mcp.md)
- [hook support](https://github.com/NousResearch/hermes-agent/blob/v2026.4.30/website/docs/user-guide/features/hooks.md)

### OpenCode

The [OpenCode profile](harness-capabilities/vanilla/opencode.toml) preserves source-backed component, scheduling, limitation, uncertainty, refresh-note, source, and local-observation records.

Scheduling support: GitHub Actions cron or external schedulers around opencode run; no verified native durable scheduler.

Limitations: Default permission posture can be broad unless configured. Legacy tools permission is deprecated in favor of permission. MCP servers can create context pressure. npm plugins auto-install with Bun and can define tools and hooks; review plugins as executable third-party code.

Key sources:

- [release version, date, and release notes](https://github.com/anomalyco/opencode/releases/tag/v1.14.33)
- [active repository identity](https://github.com/anomalyco/opencode)
- [documentation index](https://opencode.ai/docs/)
- [CLI and run support](https://opencode.ai/docs/cli/)
- [skill support](https://opencode.ai/docs/skills/)
- [plugin and hook support](https://opencode.ai/docs/plugins/)

### OpenClaw

The [OpenClaw profile](harness-capabilities/vanilla/openclaw.toml) preserves source-backed component, scheduling, limitation, uncertainty, refresh-note, source, and local-observation records.

Scheduling support: Cron jobs, heartbeat turns, hooks, webhooks, and plugin background services.

Limitations: Compatible Codex, Claude, and Cursor bundles are partial bridges, not full harness equivalence. MCP bridge behavior has limits around route metadata, live event queues, push/edit/react support, and approval visibility. Multi-agent workspaces are not hard OS sandboxes unless sandboxing is configured. Some plugin changes require Gateway restart.

Key sources:

- [release version, date, and release notes](https://github.com/openclaw/openclaw/releases/tag/v2026.5.2)
- [package version](https://github.com/openclaw/openclaw/blob/v2026.5.2/package.json)
- [adjacent prerelease context](https://github.com/openclaw/openclaw/releases/tag/v2026.5.2-beta.3)
- [feature overview](https://github.com/openclaw/openclaw/blob/v2026.5.2/docs/concepts/features.md)
- [skill support](https://github.com/openclaw/openclaw/blob/v2026.5.2/docs/tools/skills.md)
- [plugin support](https://github.com/openclaw/openclaw/blob/v2026.5.2/docs/tools/plugin.md)

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

The catalog is versioned state, not timeless documentation. Refresh the affected harness profile when:

- a Smith spec or implementation depends on a harness capability listed here;
- the source's release or changelog has moved since the checked-at timestamp;
- a capability is marked experimental, preview-like, prerelease, plan-dependent, or locally unobserved;
- local installation state can materially differ from public documentation;
- a downstream change needs a hard security, scheduling, hook, MCP, or plugin claim.

At minimum, a refreshed profile records version or version basis, checked-at timestamp, first-party sources, evidence category, component support, scheduling support, limitations, uncertainty, and local observations when local state was inspected.
