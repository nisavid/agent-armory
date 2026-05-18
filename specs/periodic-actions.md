# Periodic Actions Spec

Status: Equipment Blueprint
Promotion state: specified

This spec describes desired behavior for future Agent Equipment. It does not implement Agent Equipment, install scheduled work, or select a final harness mechanism.

## Purpose

Periodic Actions provide a cross-harness equipment layer for recurring agent actions. They let a repo request recurring agent work while preserving local operator approval, harness-specific capability limits, and auditable state.

## User stories

### Implement periodic action

As an agent strapped into a harness equipped with Periodic Actions, when a repo requires an agent action to occur periodically, I can implement that action so it runs as faithfully to the requested periodicity as my harness supports.

### First-session install prompt

As a repo owner with a Repo Ops repo freshly cloned on a new machine, if the repo defines periodic actions, my first agent session shows a first-session install prompt.

The choice is persisted locally only and must not be committed by default.

### Manage actions

As a repo user, I can list periodic actions with:

- repo,
- extension or module,
- action name,
- period,
- installed status,
- last run timestamp,
- terse summary of the last result.

I can view a periodic action with:

- all list fields,
- human-friendly description,
- configuration,
- engine type,
- entrypoint script or prompt,
- last result details.

I can manage each action with:

- install,
- uninstall,
- trigger-now when supported,
- edit-period when allowed by the action definition.

## Acceptance criteria

- Periodic Actions never install recurring work without local approval.
- The first-session install prompt appears when a configured repo has periodic actions and no local installation choice exists.
- The local installation choice is persisted locally only and is never stored in committed repo config.
- The list command exposes repo, extension or module, action name, period, installed status, last run timestamp, and terse summary.
- The view command exposes the complete action detail needed to audit what will run.
- Install and uninstall are supported for every action that has an available harness mechanism.
- trigger-now is supported when the harness can safely invoke the action on demand.
- edit-period is supported only when the action definition allows local period changes.
- Run results are recorded with enough detail for a later agent to inspect the last execution.
- Mechanism selection order is applied at install time unless the user explicitly overrides it.

The mechanism selection order is:

1. Native scheduled agent actions.
2. Active loop or heartbeat.
3. Suitable hook.
4. Inference-driven pre/post task check.

Suggested storage lives under `.repo-ops/`:

```text
.repo-ops/
  periodic-actions.toml
  local.periodic-actions.toml
  state/
    periodic-actions.jsonl
```

## Harness projections

Periodic Actions must define projections for:

- Codex,
- OpenClaw,
- Hermes Agent,
- Claude Code,
- Cursor,
- OpenCode.

Starting points:

- OpenClaw: cron first; heartbeat fallback.
- Hermes Agent: cron first; hooks fallback.
- Claude Code: Routines or Desktop tasks first; `/loop` for session-scoped work.
- Cursor: Automations or background agents where appropriate; rules or hooks fallback after verification.
- Codex: verify current scheduling or goal support; otherwise use hooks or rules fallback.
- OpenCode: plugin or external scheduler first; otherwise hooks or rules fallback.

Each projection must state the chosen engine type, installation surface, uninstallation path, state file behavior, and known limitations.

## Non-goals

- Periodic Actions do not guarantee exact wall-clock execution when a harness lacks native scheduling.
- Periodic Actions do not bypass OS permissions, harness approvals, or Repo Ops policy.
- Periodic Actions do not require every harness to support trigger-now or edit-period.
- Periodic Actions do not store local machine installation choices in committed files by default.

## Open questions

- Should the state log be append-only JSONL, summarized TOML, or both?
- Should trigger-now require separate approval for actions with network, write, or credential access?
- Which action fields belong in core Periodic Actions versus Repo Ops extension metadata?
