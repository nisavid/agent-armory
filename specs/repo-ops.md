# Repo Ops Spec

Status: Equipment Blueprint
Promotion state: specified

This spec describes desired behavior for future Agent Equipment. It does not implement Agent Equipment, publish installable assets, or establish a final config schema.

## Purpose

Repo Ops provides a repository framework for agentic operations. It lets a
repository declare how agent operators should discover operations, read and
write Repo Ops settings, honor autonomy levels, and enforce policy through the
harness mechanisms available in that environment.

Repo Ops consumes lower-level equipment rather than owning it. Issue Tracker
Ops, or Issue Ops for short, owns issue-tracked operations. Agent Equipment
Config owns the shared configuration primitive. Repo Ops may use both, but it
must not make either depend on Repo Ops.

Repo Ops is complete for repositories that are not forks. Fork Ops is a planned
Repo Ops add-on for fork-specific operations, not a replacement for the core
repository-operations layer. Fork Ops may extend Repo Ops with upstream,
downstream, divergence, selective-upstreaming, and fork-publication behavior.

Repo Ops should support extension systems that reuse core Repo Ops behavior for
more specific operations. Extensions may define additional config keys,
runbooks, hooks, periodic actions, or workflow equipment, but they must not
override core ownership, approval, and safety rules.

Agent Ops is the generic term for operations work performed agentically. It is
not the name of this repository-operations equipment line.

## User stories

### Agent discovers operations

As an agent strapped into a harness equipped with Repo Ops, I can readily find:

- the repo's operations runbook paths,
- the autonomy level that governs my work,
- the durable settings that apply to the current checkout,
- the local-only settings that should not be committed.

### Durable Repo Ops config

As a repo owner, I can store Repo Ops settings in TOML files that are durable
across sessions and trackable in version control when appropriate.

Repo Ops defines its own config shape for:

- Repo Ops core,
- Repo Ops extensions,
- the repo,
- the local checkout.

When Agent Equipment Config is equipped, Repo Ops contributes this shape as a
namespaced schema fragment and relies on Agent Equipment Config for layering,
conflict reporting, migration, governance, and effective-config output.

When Agent Equipment Config is absent, Repo Ops still describes enough of its
plain config shape to support session-scoped operation, handoff, and later
ingestion.

### Policy enforcement

As a repo owner, I can define policy settings that an equipped harness uses for policy enforcement.

If a harness can block a violating action, the projection blocks it. If a harness cannot block, the projection uses the strongest advisory fallback available and documents that limitation in the relevant projection.

### Safe defaults

As a repo owner or operator, I can equip a harness with Repo Ops without
enabling unexpected automations in unconfigured repos or repos where I am not
an owner. Safe defaults require advance approval before Repo Ops automations
run in those cases.

### Enablement declaration

As a repo owner, I can declare that a repo uses Repo Ops, agentic operations, or
an equivalent project term.

The declaration may specify an autonomy level. If it does not, the harness
should prompt for one, preferably through an interactive menu when available.
The selected value is stored in Repo Ops config when durable config is
available, or in session policy when it is not.

### Fork Ops extension

As a repo owner operating a fork, I can add Fork Ops to Repo Ops so fork-specific
behavior extends the same discovery, config, policy, hook behavior, and
autonomy model without making non-fork repositories carry fork concepts.

Fork Ops owns fork-specific requirements such as upstream remotes, fork
ancestry, divergence inventories, sync policy, upstream contribution policy,
publication boundaries, and selective upstreaming. Repo Ops owns the generic
repository operations substrate those behaviors use.

## Acceptance criteria

- Repo Ops defines autonomy levels for `off`, `advisory`, `assisted`, `supervised`, `autonomous`, and `forbidden`, or records a reasoned refinement before implementation.
- Repo Ops defines a plain config shape that uses TOML, human-readable
  filenames, human-readable keys, and sensibly typed values.
- Repo Ops publishes a schema fragment for Agent Equipment Config when the
  shared config equipment is available.
- Repo Ops config can drive agent behavior, hook behavior, and other
  configurable Repo Ops behavior.
- Committed config and local-only config are separated clearly.
- Ownership config can name an owner through stable identifiers such as GitHub users.
- Runbook config can list exact paths and controlled globs.
- Extension config is namespaced so unrelated extensions do not collide.
- Fork Ops can add fork-aware config without making fork-specific keys part of
  Repo Ops core.
- Safe defaults prevent unapproved automation in unconfigured repos and non-owner repos.
- Policy enforcement behavior is explicit for every harness projection.
- Advisory fallbacks are labeled as weaker than blocking controls.
- Intake planning covers the generic repository-operations behavior already
  scattered across Armory-adjacent docs and the generic behavior currently
  mixed into Fork Ops source material.

An initial plain config shape may look like:

```toml
[repo_ops.core]
enabled = true
autonomy = "assisted"

[repo_ops.core.owners]
github_users = ["nisavid"]

[repo_ops.core.runbooks]
paths = ["ops/runbook.md", "ops/*.md"]

[repo_ops.extension.periodic_actions]
enabled = true

[repo_ops.repo.nisavid_agent_armory]
policy_doc = "ops/repo-ops.md"

[repo_ops.local.this_checkout]
install_periodic_actions = "ask"

[repo_ops.extension.fork_ops]
enabled = false
```

## Harness projections

Every Repo Ops implementation must define projections for:

- Codex,
- OpenClaw,
- Hermes Agent,
- Claude Code,
- Cursor,
- OpenCode.

Each projection must describe:

- where the harness discovers Repo Ops config,
- how the harness loads committed and local-only settings,
- how the projection uses Agent Equipment Config when it is available,
- how the projection operates from explicit session policy when Agent Equipment
  Config is absent,
- which actions can be blocked,
- which actions are advisory only,
- how owner checks are performed,
- how runbook paths are surfaced before work starts,
- how autonomy levels influence agent behavior.

## Non-goals

- Repo Ops does not make unowned repositories agent-operated by default.
- Repo Ops does not own the generic Agent Equipment configuration system.
- Repo Ops does not make Issue Ops depend on Repo Ops.
- Repo Ops does not guarantee blocking policy enforcement in harnesses that expose only advisory controls.
- Repo Ops does not require all harnesses to use the same storage internals when their native controls differ.
- Repo Ops does not absorb fork-specific behavior into core when Fork Ops should own it as an extension.
- Repo Ops does not treat this Seed spec as a final schema contract.
- Agent Ops does not name this equipment line.

## Open questions

- Which Repo Ops settings are core schema keys, and which belong to extension
  schema fragments?
- Which generic repository-operations behaviors currently implemented in Fork
  Ops should be extracted into Repo Ops before Fork Ops becomes a formal
  extension?
