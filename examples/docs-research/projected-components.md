# Projected Components: Documentation Research

Status: Framework Example
Promotion state: example

This Framework Example is not Published Agent Equipment and is not installable.
Trace: [capability card](capability-card.md) -> [interface decision record](interface-decision-record.md) -> projected components.

## Components

| Surface | Example projection | Promotion note |
| --- | --- | --- |
| Local docs | `docs/engineering/documentation-research.md` | Source priority, evidence categories, and citation expectations. |
| Skill | `documentation-research` | Trigger and synthesis procedure. |
| Script | `scripts/dependency-versions --json` | Local version extraction before external lookup. |
| MCP/tool | Documentation lookup provider | Read-only current docs retrieval. |
| MCP/tool | Web search or scraper | Fallback for non-library docs and source pages. |
| Hook | `hooks/docs-evidence-gate` | Flags uncited version-sensitive claims where enforceable. |
| Agent Profile | `agents/docs-researcher.toml` | Read-only researcher profile with narrow external tools. |
| Config | `config/docs-research.toml` | Provider order and disclosure limits. |
| Plugin | `agent-armory-docs-research` | Deferred portable bundle after validation. |

## Minimal Smith Path

1. Confirm the capability in the [capability card](capability-card.md).
2. Keep this [interface decision record](interface-decision-record.md) aligned with provider and disclosure choices.
3. Implement local version discovery before broad external retrieval.
4. Add source metadata and citation checks before relying on the output.
5. Run pressure validation on a version-sensitive implementation task.

## Non-Published Boundary

This example describes a projection path. It does not provide live provider credentials, installable configuration, or validated harness behavior.
