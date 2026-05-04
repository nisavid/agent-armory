# Interface Decision Record: Observability Investigation

Status: Forge Example
Promotion state: example

This Forge Example is not Published Agent Equipment and is not installable.
Trace: [capability card](capability-card.md) -> interface decision record -> [projected components](projected-components.md).

## Requirement

The observability investigation capability needs procedural investigation judgment, typed read-only observability tools, strict query bounds, redaction, audit evidence, local service knowledge, and a specialist profile with scoped access.

## Decision

Use a skill for the investigation sequence, MCP/tools for metrics, traces, logs, and deploy history, hooks for bounds and redaction gates, config for environment limits, local docs for service truth, scripts for deterministic summarization, and an Agent Profile for scoped investigator identity.

## Chosen surface

- Skill: investigation order, hypothesis discipline, and report format.
- MCP/tool: metrics, traces, logs, deploy history, service catalog.
- Hook: query-bound enforcement, redaction checks, and audit records.
- Agent Profile: read-only incident investigator with scoped tools and context.
- Plugin: deferred observability bundle.
- Script: trace summarizer, deploy mapper, evidence redactor.
- Config: allowed environments, service allowlist, lookback limits, escalation thresholds.
- Local docs: runbooks, service ownership, incident policy.

## Rationale

Observability data is live external state, so retrieval belongs in tools with typed inputs and outputs. Query bounds and redaction are hard controls, so they belong in hooks, config, and tool policy rather than only in a skill. The synthesis still needs model judgment, so a skill and specialist Agent Profile are appropriate.

## Evidence category

Implementation inference. The example demonstrates the Framework placement method without validating any observability integration.

## Harness-specific projection

- Codex: project to local runbook docs, scoped MCP tools where available, and a read-only investigator subagent profile.
- Claude Code: defer exact observability surface until tool and permission behavior is confirmed.
- Cursor: start with local docs and scripts; defer live observability access.
- Hermes Agent, OpenCode, OpenClaw: defer until credentials, tool schema, and audit surfaces are documented.

## Alternatives rejected

- Skill-only incident workflow: rejected because query bounds, redaction, and live data retrieval need enforceable surfaces.
- Raw log dump into context: rejected because it wastes context and risks secret exposure.
- General-purpose root agent access: rejected because incident investigation benefits from narrower tools, identity, and output contract.

## Risks

- Secret exposure from raw logs or traces.
- Overbroad production queries.
- Mistaking correlation for cause.
- Operational action creep if mitigation authority is not separated from investigation.

## Maintenance notes

Review this decision when observability providers change, when data-handling policy changes, when incident authority changes, or when repeated investigations show missing query bounds or weak redaction.
