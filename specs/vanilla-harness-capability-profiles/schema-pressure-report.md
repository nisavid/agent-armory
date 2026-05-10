# Schema Pressure Report: Harness Surfaces

Status: issue #44 schema pressure

## Research Scope

This report compares the six issue #44 research notes against the Vanilla Harness Capability Profile v1alpha1 schema. The scope is descriptive harness integration surfaces only: instructions/context, skills, MCP/tools, hooks/events, plugins/bundles, Agent Profiles/subagents, memory/context retrieval, config/settings, permissions/approvals/sandboxing, scheduling/automation, commands/shortcuts, providers/connectors, runtime modes, cross-harness import/compatibility, and lifecycle reload/update.

Issue #45 applies accepted findings from this report to the canonical profiles while keeping deferred, rejected, and needs-more-evidence findings explicit.

## Current Schema Comparison

The current schema records one flat claim per standard surface family, with status, statement, evidence references, applicability scope, capability origin, migration status, evidence basis, limitations, and uncertainty. That is sufficient for preserving migrated first-slice facts and for making unknowns visible.

The research notes show pressure where a flat family claim cannot describe integration shape without hiding important distinctions:

- version observations can drift independently from canonical profile mutations;
- evidence classifications need to attach to individual facts, not only whole profiles;
- component surfaces need load paths, activation triggers, mutability, scope, precedence, and reload/update behavior;
- cross-harness compatibility needs bridge fidelity fields;
- memory-like behavior needs persistence, retrieval, write-authority, freshness, and privacy fields;
- automation needs trigger, runner, permission, sandbox, missed-run, and output-delivery fields.

## Schema Pressure Findings

| ID | Disposition | Affected harnesses | Motivating evidence | Example claim shape | Proposed validation rule | Migration impact |
| --- | --- | --- | --- | --- | --- | --- |
| SP-001 | accepted | codex, claude_code, hermes_agent, opencode, openclaw | Current releases differ from migrated profile versions: [Codex](https://github.com/openai/codex/releases/tag/rust-v0.130.0), [Claude Code](https://github.com/anthropics/claude-code/releases/tag/v2.1.138), [Hermes](https://github.com/NousResearch/hermes-agent/releases/tag/v2026.5.7), [OpenCode](https://github.com/anomalyco/opencode/releases/tag/v1.14.46), [OpenClaw](https://github.com/openclaw/openclaw/releases/tag/v2026.5.7) | `[[version_observation]] observed_version = "rust-v0.130.0"; canonical_profile_change = true` | Require checked-at, source URL, observed version, and whether the observation changes canonical profile claims. | Canonical profiles carry one current version observation per supported harness. |
| SP-002 | accepted | all | [Issue #44](https://github.com/nisavid/agent-armory/issues/44) requires source-backed facts, local observations, implementation inferences, hypotheses, unsupported claims, unknowns, and not-applicable surfaces. Research notes record each category explicitly. | `fact.evidence_class = "source_backed"; fact.source_ids = ["ev-..."]` | Require every enriched fact or detail to carry one evidence classification from a controlled value set. | Existing profile-level `evidence_category` remains but cannot be the only evidence classifier after enrichment. |
| SP-003 | accepted | all | Skills, plugins, subagents, commands, MCP, hooks, and config surfaces all need load path, activation, scope, and reload detail, for example [Claude Code skills](https://code.claude.com/docs/en/skills) and [Cursor plugins](https://cursor.com/docs/plugins). | `[[claim.detail]] component = "skills"; load_scope = ["project", "user"]; activation = ["implicit", "explicit"]` | For supported claims with structured details, require component, load or attachment point, activation, mutability, scope, and evidence references when known. | Future migration should add optional nested detail tables while preserving stable family claim IDs. |
| SP-004 | accepted | cursor, openclaw, codex, claude_code | Cursor describes Agent Skills as an open standard, while OpenClaw documents compatible Codex, Claude, and Cursor bundles. Codex and Claude Code support skills/plugins but do not prove reciprocal import. Sources: [Cursor skills](https://cursor.com/docs/skills), [OpenClaw compatible bundles](https://github.com/openclaw/openclaw/blob/v2026.5.2/docs/plugins/bundles.md). | `[[claim.compatibility_bridge]] imported_from = "cursor"; fidelity = "partial"; surviving_components = ["skills"]` | Cross-harness import claims require source harness, imported convention, supported components, activation/disable behavior, fidelity limits, and evidence. | Enrichment must not convert compatibility bridges into native support claims. |
| SP-005 | accepted | hermes_agent, openclaw, codex, cursor, opencode, claude_code | Hermes release notes identify `/goal`, checkpoints, and session keys; OpenClaw release notes identify Active Memory; Codex automations preserve thread context; Cursor subagents isolate context; OpenCode snapshots need review; Claude Code routines persist prompt/config state. Sources include [Hermes release](https://github.com/NousResearch/hermes-agent/releases/tag/v2026.5.7), [OpenClaw release](https://github.com/openclaw/openclaw/releases/tag/v2026.5.7), [Codex automations](https://developers.openai.com/codex/app/automations), [Cursor subagents](https://cursor.com/docs/subagents). | `[[claim.memory_like_surface]] persistence_scope = "session"; retrieval_trigger = "implicit"; write_authority = "agent"` | Memory-like surfaces require persistence scope, retrieval trigger, mutability/write authority, freshness, privacy boundary, API stability, and evidence or explicit unknowns. | The current `memory_context_retrieval` family remains, but enrichment should add nested memory-like records rather than inventing one shared memory API. |
| SP-006 | accepted | codex, claude_code, cursor, hermes_agent, openclaw | Scheduling surfaces differ by app automation, cloud routine, desktop task, cron, heartbeat, Kanban worker, GitHub Action, and external runner. Sources include [Codex automations](https://developers.openai.com/codex/app/automations), [Claude Code routines](https://code.claude.com/docs/en/routines), [OpenClaw cron](https://github.com/openclaw/openclaw/blob/v2026.5.2/docs/automation/cron-jobs.md). | `[[claim.automation_surface]] trigger = "cron"; runner_locus = "cloud"; approval_context = "default_sandbox"` | Automation details require trigger class, runner locus, recurrence shape, permission/sandbox context, catch-up or missed-run behavior when known, and delivery/output behavior. | Migrated `summary_scheduling` stays human-facing; profile enrichment should move durable scheduling facts into structured details. |
| SP-007 | deferred | all | The notes identify multiple valid Capability Analysis Angles and Capability State Graphs for the same claim, but [issue #46](https://github.com/nisavid/agent-armory/issues/46) owns the Capability Profiling Protocol. | `[[analysis_angle]] preferred = "automation_runner"; deferred_reason = "protocol story"` | Defer machine-readable angle/state-graph schema until the study artifact story; require issue #44 notes to record preferred or deferred angle rationale in prose. | No profile migration in issue #44. Issue #46 should define study-plan/report schemas. |
| SP-008 | needs more evidence | codex, claude_code, cursor, opencode, openclaw, hermes_agent | Hook/event surfaces exist across harnesses, but event names, enforcement authority, HTTP hooks, shell hooks, native hooks, and plugin hooks do not share a proven vocabulary. Sources include [Codex hooks](https://developers.openai.com/codex/hooks), [Claude Code hooks](https://code.claude.com/docs/en/hooks), [Cursor hooks](https://cursor.com/docs/hooks), [OpenClaw hooks](https://github.com/openclaw/openclaw/blob/v2026.5.2/docs/automation/hooks.md). | `event_kind = "pre_tool_use"; authority = "advisory&#124;blocking&#124;approval"` | Do not adopt a shared hook value set until the profile enrichment pass compares event names and authority semantics source by source. | Keep hooks supported/unknown at family level until richer event taxonomy is proven. |
| SP-009 | needs more evidence | codex, claude_code, cursor, opencode, hermes_agent, openclaw | Provider and connector surfaces include model providers, MCP connectors, GitHub/Slack/Sentry/webhook integrations, media/search providers, and channels. Sources include [Cursor MCP](https://cursor.com/docs/mcp), [Claude Code routines](https://code.claude.com/docs/en/routines), [OpenCode GitHub](https://opencode.ai/docs/github/), [Hermes release](https://github.com/NousResearch/hermes-agent/releases/tag/v2026.5.7). | `[[claim.connector]] connector_kind = "mcp&#124;channel&#124;model_provider&#124;vcs&#124;webhook"` | Defer a connector taxonomy until more sources distinguish provider, connector, channel, and integration terms. | Future enrichment may add connector details, but issue #44 should not force one taxonomy. |
| SP-010 | rejected | all | Profiles are descriptive records of harness surfaces; downstream Forge consumption logic belongs outside Vanilla Harness Capability Profiles. The bundle boundary is in [the README](README.md). | `recommended_equipment = "..."` | Reject fields that prescribe Smith choices, Forge projection behavior, or equipment recommendations. | No migration. Keep downstream consumption logic out of profile schema. |

## Cross-Harness Import And Compatibility

Cross-harness import and compatibility must be first-class because OpenClaw has explicit compatible bundle surfaces and Cursor frames Agent Skills as an open standard. Compatibility claims need to identify the imported convention and fidelity limits. A profile must not equate compatibility with native support, and "same standard shape" must remain distinct from "this harness can import and activate another harness's bundle."

## Memory-Like Surfaces

The supported harnesses expose memory-like behavior through different shapes: Codex thread automations and memory-like context retrieval, Claude Code routines and MCP resources, Cursor subagent context isolation, Hermes `/goal` and checkpoints, OpenCode snapshots, and OpenClaw Active Memory. The schema should record memory-like facts without assuming a common API.

## Analysis Angles And State Graphs

Multiple Capability Analysis Angles can model the same claim. Scheduling can be studied through trigger semantics, runner locus, or output delivery. Memory can be studied through persistence, retrieval, or privacy. Cross-harness compatibility can be studied through package format, activation, or behavioral fidelity. Issue #44 records those choices in prose; issue #46 should own machine-readable Capability State Graph structure.

## Migration Implications

Issue #45 enriches profiles without replacing stable family claim IDs. Each current `claim-<harness>-<family>` row remains and records Capability Claim Triage, evidence basis, integration-surface fields, and explicit unknowns where source evidence is insufficient.

The accepted profile fields are `[[version_observation]]`,
`[[harness_extension]]`, `[[claim.detail]]`,
`[[claim.memory_like_surface]]`, `[[claim.automation_surface]]`, and
`[[claim.compatibility_bridge]]`. SP-007 remains deferred to the Capability
Profiling Protocol story. SP-008 and SP-009 remain needs-more-evidence and are
recorded as claim uncertainty rather than flattened into shared hook or
connector taxonomies. SP-010 remains rejected.

## Ralph Review Disposition

Ralph Review Cycle 1: findings fixed before publication in this report.

Findings:

- The first report draft risked turning schema pressure into downstream Smith guidance. Fixed by rejecting downstream consumption fields in SP-010.
- The first report draft did not separate external scheduler support from native scheduler support. Fixed by SP-006 and the OpenCode note.
- The first report draft treated memory-like surfaces as one family. Fixed by SP-005 and the per-harness memory-like notes.

Ralph Review Cycle 2: clean. No open findings for issue #44 schema-pressure publication. Accepted findings are applied by issue #45 where they fit the current profile boundary.

## Scratch Artifact Disposition

Raw GitHub release API responses and Firecrawl extraction output are instance-scoped scratch. Durable project evidence is limited to source URLs, curated research-note facts, the schema-pressure findings table, and the review disposition above.
