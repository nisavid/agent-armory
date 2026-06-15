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

Checked at: 2026-05-10T19:13:40-04:00 to 2026-06-15T08:13:00-04:00.

The profiles preserve source-backed version, component, scheduling, limitation, uncertainty, refresh-note, local-observation, claim-triage, and enrichment fields. Local observations are recorded per profile; workspace configs, gateways, plugin installs, cloud agents, and automation state remain profile-scoped evidence surfaces.

Documentation indexes can lag behind current release evidence. For version anchors, prefer GitHub releases or official changelogs over generated indexes or secondary metadata.

## Harness matrix

| Harness | Profile | Version basis | Checked version | Evidence | Scheduling posture |
| --- | --- | --- | --- | --- | --- |
| Codex | [Codex profile](harness-capabilities/vanilla/codex.toml) | GitHub release rust-v0.139.0 for openai/codex, local codex-cli 0.139.0 observation, plus first-party OpenAI Codex docs for integration surfaces. | 0.139.0 (rust-v0.139.0) | source-supported | Codex supports app automations and noninteractive runs that can be scheduled externally; both inherit Codex sandbox and approval constraints. |
| Claude Code | [Claude Code profile](harness-capabilities/vanilla/claude_code.toml) | GitHub release v2.1.138 for anthropics/claude-code, plus first-party Claude Code docs for integration surfaces. | 2.1.138 | documentation-supported | Claude Code supports cloud routines, desktop scheduled tasks, and session scheduled tasks with distinct runner loci and permission contexts. |
| Cursor | [Cursor profile](harness-capabilities/vanilla/cursor.toml) | Official Cursor changelog through the 2026-05-07 Cursor 3.3 entry, plus first-party Cursor docs for integration surfaces. | 3.3 changelog state through 2026-05-07 | documentation-supported | Cursor Cloud Agent automations support schedule and event triggers; plan parallelism, PR review, and multitask surfaces are current changelog-backed runtime surfaces. |
| Hermes Agent | [Hermes Agent profile](harness-capabilities/vanilla/hermes_agent.toml) | GitHub release v2026.5.7, named Hermes Agent v0.13.0, plus first-party Hermes docs carried by the migrated profile. | 0.13.0 (v2026.5.7) | source-supported | Hermes supports cron, no_agent cron mode, curator/background processes, Kanban workers, gateway ticks, and heartbeat-like multi-agent worker flows. |
| OpenCode | [OpenCode profile](harness-capabilities/vanilla/opencode.toml) | GitHub release v1.14.46 for anomalyco/opencode, plus first-party OpenCode docs for integration surfaces. | 1.14.46 | source-supported | OpenCode has source-backed external scheduling through GitHub Action integration; no native durable scheduler is proven by checked sources. |
| OpenClaw | [OpenClaw profile](harness-capabilities/vanilla/openclaw.toml) | GitHub release v2026.5.7 for openclaw/openclaw, plus tag-pinned first-party docs carried by the migrated profile. | 2026.5.7 | source-supported | OpenClaw supports cron, heartbeat turns, hooks, webhooks, background services, and release-backed cron JSON status surfaces. |

## Harness notes

### Codex

The [Codex profile](harness-capabilities/vanilla/codex.toml) preserves source-backed component, scheduling, limitation, uncertainty, refresh-note, source, and local-observation records.

Scheduling support: Codex supports app automations and noninteractive runs that can be scheduled externally; both inherit Codex sandbox and approval constraints.

Limitations: Plugin, hook, MCP, app-server, and marketplace behavior is component-specific. Plugin-bundled hooks require trust review, unattended runs still need sandbox and approval controls, and no checked source proves native import of another harness bundle convention.

Key sources:

- [current stable release version, release date, and release notes](https://github.com/openai/codex/releases/tag/rust-v0.139.0)
- [Codex change history](https://developers.openai.com/codex/changelog)
- [skill support](https://developers.openai.com/codex/skills)
- [plugin support](https://developers.openai.com/codex/plugins)
- [plugin authoring support](https://developers.openai.com/codex/plugins/build)
- [hook support](https://developers.openai.com/codex/hooks)

### Claude Code

The [Claude Code profile](harness-capabilities/vanilla/claude_code.toml) preserves source-backed component, scheduling, limitation, uncertainty, refresh-note, source, and local-observation records.

Scheduling support: Claude Code supports cloud routines, desktop scheduled tasks, and session scheduled tasks with distinct runner loci and permission contexts.

Limitations: The latest release notes are internal-fix scoped, so surface claims rely on first-party docs. Routines, desktop tasks, and session tasks must remain distinct automation surfaces.

Key sources:

- [latest Claude Code release version and release date](https://github.com/anthropics/claude-code/releases/tag/v2.1.138)
- [skill support](https://code.claude.com/docs/en/skills)
- [MCP support](https://code.claude.com/docs/en/mcp)
- [hook support](https://code.claude.com/docs/en/hooks)
- [subagent support](https://code.claude.com/docs/en/sub-agents)
- [plugin support and limits](https://code.claude.com/docs/en/plugins-reference)

### Cursor

The [Cursor profile](harness-capabilities/vanilla/cursor.toml) preserves source-backed component, scheduling, limitation, uncertainty, refresh-note, source, and local-observation records.

Scheduling support: Cursor Cloud Agent automations support schedule and event triggers; plan parallelism, PR review, and multitask surfaces are current changelog-backed runtime surfaces.

Limitations: Cursor version evidence is changelog-based rather than a GitHub release tag. Team marketplace, admin model controls, plan gates, and Cloud Agent availability remain environment-scoped.

Key sources:

- [latest official changelog state through Cursor 3.3](https://cursor.com/changelog)
- [Cursor 3.3 changelog entry from 2026-05-07](https://cursor.com/changelog/05-07-26)
- [rules and AGENTS.md support](https://cursor.com/docs/rules)
- [Agent Skills support](https://cursor.com/docs/skills)
- [MCP support](https://cursor.com/docs/mcp)
- [hook support](https://cursor.com/docs/hooks)

### Hermes Agent

The [Hermes Agent profile](harness-capabilities/vanilla/hermes_agent.toml) preserves source-backed component, scheduling, limitation, uncertainty, refresh-note, source, and local-observation records.

Scheduling support: Hermes supports cron, no_agent cron mode, curator/background processes, Kanban workers, gateway ticks, and heartbeat-like multi-agent worker flows.

Limitations: Some detailed docs remain tag-pinned to the migrated version basis, while v2026.5.7 release notes supply current feature and lifecycle evidence. Cross-harness import fidelity remains unproven.

Key sources:

- [current release version, date, and release notes](https://github.com/NousResearch/hermes-agent/releases/tag/v2026.5.7)
- [documentation index](https://hermes-agent.nousresearch.com/docs/llms.txt)
- [skill support](https://github.com/NousResearch/hermes-agent/blob/v2026.4.30/website/docs/user-guide/features/skills.md)
- [MCP support](https://github.com/NousResearch/hermes-agent/blob/v2026.4.30/website/docs/user-guide/features/mcp.md)
- [hook support](https://github.com/NousResearch/hermes-agent/blob/v2026.4.30/website/docs/user-guide/features/hooks.md)
- [plugin support](https://github.com/NousResearch/hermes-agent/blob/v2026.4.30/website/docs/user-guide/features/plugins.md)

### OpenCode

The [OpenCode profile](harness-capabilities/vanilla/opencode.toml) preserves source-backed component, scheduling, limitation, uncertainty, refresh-note, source, and local-observation records.

Scheduling support: OpenCode has source-backed external scheduling through GitHub Action integration; no native durable scheduler is proven by checked sources.

Limitations: The current release includes security and compatibility fixes, including a Plan Mode security bypass fix. Native scheduling and lifecycle reload semantics remain unresolved.

Key sources:

- [current release version, date, and release notes](https://github.com/anomalyco/opencode/releases/tag/v1.14.46)
- [documentation index](https://opencode.ai/docs/)
- [CLI and run support](https://opencode.ai/docs/cli/)
- [skill support](https://opencode.ai/docs/skills/)
- [plugin and hook support](https://opencode.ai/docs/plugins/)
- [agent and subagent support](https://opencode.ai/docs/agents/)

### OpenClaw

The [OpenClaw profile](harness-capabilities/vanilla/openclaw.toml) preserves source-backed component, scheduling, limitation, uncertainty, refresh-note, source, and local-observation records.

Scheduling support: OpenClaw supports cron, heartbeat turns, hooks, webhooks, background services, and release-backed cron JSON status surfaces.

Limitations: Several detailed docs remain tag-pinned to v2026.5.2 while v2026.5.7 release notes add current security, memory, scheduling, and lifecycle evidence. Compatible-bundle support must not be treated as native support for every imported component.

Key sources:

- [current release version, date, and release notes](https://github.com/openclaw/openclaw/releases/tag/v2026.5.7)
- [feature overview](https://github.com/openclaw/openclaw/blob/v2026.5.2/docs/concepts/features.md)
- [skill support](https://github.com/openclaw/openclaw/blob/v2026.5.2/docs/tools/skills.md)
- [plugin support](https://github.com/openclaw/openclaw/blob/v2026.5.2/docs/tools/plugin.md)
- [plugin manifest support](https://github.com/openclaw/openclaw/blob/v2026.5.2/docs/plugins/manifest.md)
- [compatible bundle support](https://github.com/openclaw/openclaw/blob/v2026.5.2/docs/plugins/bundles.md)

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

At minimum, a refreshed profile records version, version basis, checked-at timestamp, first-party sources, evidence category, component support, scheduling support, limitations, uncertainty, and local observations when local state was inspected.
