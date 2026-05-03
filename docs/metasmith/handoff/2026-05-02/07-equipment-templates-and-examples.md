# Equipment Templates and Examples

## Template: capability card

```markdown
# Capability Card: <name>

## Purpose

## Users

## Target harnesses

## Risks

## External systems

## Side effects

## Needed Harness Components

- Skills:
- MCP/tools:
- Hooks:
- Agent Profiles:
- Plugins:
- Scripts:
- Config:
- Docs:

## Hard rules

## Deterministic checks

## Output contract

## Failure modes

## Evidence

## Open questions
```

## Template: interface decision record

```markdown
# Interface Decision Record: <capability>

## Requirement

## Decision

## Chosen surface

- Skill:
- MCP/tool:
- Hook:
- Agent Profile:
- Plugin:
- Script:
- Config:
- Local docs:

## Rationale

## Evidence category

## Harness-specific projection

## Alternatives rejected

## Risks

## Maintenance notes
```

## Template: skill reference

Keep skill references short.

```markdown
---
name: pr-review
description: Review pull requests and diffs for correctness, maintainability, security, and repo conventions.
---
```

## Template: skill body

```markdown
# Skill: <name>

## Use when

## Do not use when

## Preflight

1. Identify repo root.
2. Read relevant local docs.
3. Run deterministic helper scripts if available.
4. Check permissions and autonomy.

## Procedure

## Tool and script usage

## Local docs to read

## Output contract

## Failure handling

## Safety and policy notes
```

## Template: hook

```typescript
/**
 * Hook: <name>
 * Event: <event>
 * Purpose: <policy or automation>
 * Fail mode: fail-open | fail-closed
 */

export async function handle(event: unknown): Promise<unknown> {
  // 1. Parse and validate event.
  // 2. Decide whether to allow, block, rewrite, or warn.
  // 3. Return a clear reason.
  return { allow: true };
}
```

## Template: Agent Profile

```toml
name = "pr-reviewer"
description = "Review pull requests and diffs with read-only repository and GitHub access."
nickname_candidates = ["Reviewer", "Critic"]

[model]
preference = "inherit"

[skills]
allow = ["pr-review", "docs-search"]

[tools]
allow = ["git-read", "github-read", "test-read"]
deny = ["deploy", "merge", "post-comment-without-approval"]

[permissions]
mode = "read-only"

[output]
format = "review-report"
```

## Template: Harness Plugin manifest

```toml
name = "observability-investigation"
version = "0.1.0"
description = "Tools, skills, hooks, and profiles for incident investigation."

[components.skills]
paths = ["skills/observability-investigation"]

[components.hooks]
paths = ["hooks/redact-logs", "hooks/bound-observability-queries"]

[components.agent_profiles]
paths = ["profiles/latency-investigator.toml"]

[components.mcp]
servers = ["observability"]

[config]
default_lookback_hours = 2
require_approval_for_wide_queries = true
```

## Template: deterministic script contract

A script used by Agents should provide:

- `--help`,
- machine-readable output,
- clear exit codes,
- safe defaults,
- explicit destructive flags,
- terse error messages.

Example:

```sh
scripts/test-targets --changed-files changed-files.json --json
```

Example output:

```json
{
  "tests": ["npm test -- packages/api"],
  "confidence": "medium",
  "reason": "Changed files map to packages/api."
}
```

## Template: MCP/tool definition notes

Document:

- tool name,
- purpose,
- read/write classification,
- input schema,
- output schema,
- auth source,
- rate-limit behavior,
- pagination,
- side effects,
- approval requirements,
- example calls,
- failure modes.

## Template: config

```toml
[agent_ops.core]
enabled = true
autonomy = "assisted"

[agent_ops.core.runbooks]
paths = ["ops/runbook.md"]

[agent_ops.extension.periodic_actions]
enabled = true

[agent_ops.local.this_checkout]
install_periodic_actions = "ask"
```

## Example: PR review

### Components

- Skill: `pr-review`
- MCP/tool: GitHub API or `gh` CLI
- Local docs: `AGENTS.md`, `docs/engineering/pr-review.md`, module-local docs
- Scripts: `changed-modules`, `test-targets`, `check-review-policy`
- Hooks: block merges/comments without approval
- Agent Profile: `pr-reviewer`

### Skill body outline

```markdown
# Skill: PR Review

## Use when
Reviewing a PR, local diff, patch, or branch.

## Preflight
- Read repo `AGENTS.md`.
- Read nearest module policy.
- Fetch PR metadata and changed files.
- Run `scripts/changed-modules --json` if present.
- Run `scripts/test-targets --json` if present.

## Procedure
- Classify changes by module and risk.
- Inspect tests and CI.
- Check API compatibility and migrations.
- Prioritize findings by severity.

## Output contract
- Summary
- Blocking issues
- Non-blocking suggestions
- Tests checked
- Unknowns
```

## Example: documentation search

### Components

- MCP/tool: Context7 or equivalent docs lookup
- Skill: `docs-search`
- Local docs: dependency version policy
- Script: package version inspector
- Hook: warn if docs lack source/version metadata
- Agent Profile: `docs-researcher`

### Skill body outline

```markdown
# Skill: Documentation Search

## Use when
The task depends on library, API, or framework behavior that may have changed.

## Preflight
- Inspect local dependency versions.
- Identify exact library and version.
- Ask for ambiguity only when retrieval cannot resolve it.

## Procedure
- Fetch version-specific docs.
- Prefer primary docs.
- Cite sources and versions.
- Do not rely on stale memory when docs are available.
```

## Example: observability investigation

### Components

- MCP/tools: logs, traces, metrics, deploy history
- Skill: `observability-investigation`
- Config: allowed environments, lookback windows, service allowlist
- Scripts: span summarizer, deploy mapper
- Hooks: secret redaction, query bounds, audit logging
- Agent Profile: `latency-investigator`

### Skill body outline

```markdown
# Skill: Observability Investigation

## Use when
Investigating production latency, errors, regressions, or service incidents.

## Preflight
- Determine service and environment.
- Read incident/runbook docs.
- Check Agent Ops autonomy settings.
- Use configured lookback window.

## Procedure
- Start with metrics.
- Correlate traces and logs.
- Check recent deploys.
- Build timeline.
- State confidence and next checks.

## Output contract
- Timeline
- Suspected cause
- Evidence
- Mitigations
- Unknowns
```
