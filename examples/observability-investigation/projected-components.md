# Projected Components: Observability Investigation

Status: Framework Example
Promotion state: example

This Framework Example is not Published Agent Equipment and is not installable.
Trace: [capability card](capability-card.md) -> [interface decision record](interface-decision-record.md) -> projected components.

## Components

| Surface | Example projection | Promotion note |
| --- | --- | --- |
| Local docs | `docs/ops/observability-investigation.md` | Incident workflow, service ownership, and evidence rules. |
| Skill | `observability-investigation` | Investigation sequence and report contract. |
| MCP/tool | Metrics reader | Bounded time-series queries. |
| MCP/tool | Trace reader | Bounded trace lookup and summarization input. |
| MCP/tool | Log reader | Bounded log query with redaction expectations. |
| MCP/tool | Deploy history reader | Correlates incidents with deploys and config changes. |
| Hook | `hooks/observability-query-boundary` | Blocks overbroad queries and unauthorized environments. |
| Hook | `hooks/observability-redaction-gate` | Requires redaction before durable reporting. |
| Script | `scripts/summarize-traces --json` | Deterministic span grouping. |
| Script | `scripts/map-deploys --window --json` | Deterministic deploy timeline. |
| Agent Profile | `agents/latency-investigator.toml` | Read-only specialist profile. |
| Config | `config/observability-investigation.toml` | Lookback, service allowlist, and escalation thresholds. |
| Plugin | `agent-armory-observability` | Deferred portable bundle after validation. |

## Minimal Smith Path

1. Confirm the investigation scope in the [capability card](capability-card.md).
2. Keep this [interface decision record](interface-decision-record.md) aligned with tool and data-handling choices.
3. Implement config and local docs before enabling live queries.
4. Add query-bound and redaction gates before exposing log or trace output.
5. Validate against a synthetic incident dataset before connecting to sensitive environments.

## Non-Published Boundary

This example does not provide credentials, live observability integrations, incident authority, or deploy/rollback controls. A Smith must design and validate those surfaces before any publication step.
