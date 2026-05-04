# Agent Ops Spec

Status: Equipment Blueprint
Promotion state: specified

This spec describes desired behavior for future Agent Equipment. It does not implement Agent Equipment, publish installable assets, or establish a final config schema.

## Purpose

Agent Ops provides a repository framework for agentic operations. It lets a repo declare how agent operators should discover operations, read and write local settings, honor autonomy levels, and enforce policy through the harness mechanisms available in that environment.

Agent Ops should support extension systems that reuse core Agent Ops behavior for more specific operations. Extensions may define additional config keys, runbooks, hooks, periodic actions, or workflow equipment, but they must not override core ownership, approval, and safety rules.

## User stories

### Agent discovers operations

As an agent strapped into a harness equipped with Agent Ops, I can readily find:

- the repo's operations runbook paths,
- the autonomy level that governs my work,
- the durable settings that apply to the current checkout,
- the local-only settings that should not be committed.

### Durable version-controlled config

As a repo owner, I can store Agent Ops settings in TOML files that are durable across sessions and trackable in version control when appropriate.

Agent Ops config supports keys from:

- Agent Ops core,
- Agent Ops extensions,
- the repo,
- the local checkout.

The config model prevents key conflicts between layers and between distinct members of the same layer. It supports multiple extensions and chains of repo forks without forcing unrelated projects to share a namespace.

### Policy enforcement

As a repo owner, I can define policy settings that an equipped harness uses for policy enforcement.

If a harness can block a violating action, the projection blocks it. If a harness cannot block, the projection uses the strongest advisory fallback available and documents that limitation in the relevant projection.

### Safe defaults

As a repo owner or operator, I can equip a harness with Agent Ops without enabling unexpected automations in unconfigured repos or repos where I am not an owner. Safe defaults require advance approval before Agent Ops automations run in those cases.

### Enablement declaration

As a repo owner, I can declare that a repo uses Agent Ops, agentic operations, or an equivalent project term.

The declaration may specify an autonomy level. If it does not, the harness should prompt for one, preferably through an interactive menu when available. The selected value is stored in Agent Ops config.

## Acceptance criteria

- Agent Ops defines autonomy levels for `off`, `advisory`, `assisted`, `supervised`, `autonomous`, and `forbidden`, or records a reasoned refinement before implementation.
- Agent Ops config uses TOML, human-readable filenames, human-readable keys, and sensibly typed values.
- Agent Ops config can drive agent behavior, hook behavior, and other configurable Agent Ops behavior.
- Committed config and local-only config are separated clearly.
- Ownership config can name an owner through stable identifiers such as GitHub users.
- Runbook config can list exact paths and controlled globs.
- Extension config is namespaced so unrelated extensions do not collide.
- Fork-aware repo config has a namespace that can differ from local checkout config.
- Safe defaults prevent unapproved automation in unconfigured repos and non-owner repos.
- Policy enforcement behavior is explicit for every harness projection.
- Advisory fallbacks are labeled as weaker than blocking controls.

An initial config shape may look like:

```toml
[agent_ops.core]
enabled = true
autonomy = "assisted"

[agent_ops.core.owners]
github_users = ["nisavid"]

[agent_ops.core.runbooks]
paths = ["ops/runbook.md", "ops/*.md"]

[agent_ops.extension.periodic_actions]
enabled = true

[agent_ops.repo.nisavid_agent_armory]
policy_doc = "ops/agent-ops.md"

[agent_ops.local.this_checkout]
install_periodic_actions = "ask"
```

## Harness projections

Every Agent Ops implementation must define projections for:

- Codex,
- OpenClaw,
- Hermes Agent,
- Claude Code,
- Cursor,
- OpenCode.

Each projection must describe:

- where the harness discovers Agent Ops config,
- how the harness loads committed and local-only settings,
- which actions can be blocked,
- which actions are advisory only,
- how owner checks are performed,
- how runbook paths are surfaced before work starts,
- how autonomy levels influence agent behavior.

## Non-goals

- Agent Ops does not make unowned repositories agent-operated by default.
- Agent Ops does not guarantee blocking policy enforcement in harnesses that expose only advisory controls.
- Agent Ops does not require all harnesses to use the same storage internals when their native controls differ.
- Agent Ops does not treat this Seed spec as a final schema contract.

## Open questions

- What exact local file should store machine-specific Agent Ops choices?
- Should extension namespaces include package identities, repository paths, or both?
- Which config keys should be core keys, and which should belong to the first extension specs?
