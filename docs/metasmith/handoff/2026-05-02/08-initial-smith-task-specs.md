# Initial Smith Task Specs

After the first Metasmith creates the Framework, it must create Smith task specs for these initial pieces of Agent Equipment.

## Task 1: Agent Ops

### Purpose

Agent Ops provides a framework for agentic operations in a repository.

The spec is open-ended and expected to grow substantially. It should likely gain an extension system that leverages core Agent Ops functionality to provide equipment for specific kinds of operations.

### User story: Agent discovers operations

As an Agent strapped with a harness equipped with Agent Ops, I know or can readily find out:

- how to perform any operation in my repo’s ops runbook(s),
- the degree of autonomy with which the repo’s settings specify I should do so,
- how to properly read and write the repo’s local Agent Ops settings.

### User story: durable version-controlled config

A harness equipped with Agent Ops provides a configuration system that is:

- durable across sessions,
- trackable in the repo’s version control,
- capable of driving Agent behavior, hook behavior, and other configurable aspects of Agent Ops.

Settings keys can be defined by:

- Agent Ops core,
- Agent Ops extensions,
- a repo,
- a local checkout.

The configuration must prevent conflicts between layers and between distinct members of a layer. It should support multiple extensions and chains of repo forks.

The config must use:

- TOML,
- human-friendly file names,
- human-friendly settings keys,
- sensibly typed values.

### User story: policy enforcement

If an Agent in an Agent Ops repo attempts to perform an action that violates local Agent Ops settings, the action is blocked if the harness provides any mechanism with which to do so.

If the harness lacks blocking, the projection must use the strongest available advisory fallback and document that limitation.

### User story: safe default

As a repo owner, after I equip my harness with Agent Ops, in a repo that has not been configured for Agent Ops, or in an Agent Ops repo of which I am not an owner, none of the Agent Ops automations are invoked without my advance approval.

### User story: enablement declaration

As a repo owner, after I equip my harness with Agent Ops, I can declare my repo to use “agent ops,” “agentic operations,” “operated agentically,” or similar.

I may optionally specify in that declaration the degree of autonomy with which I want Agent operators to act.

If I do not specify, I am prompted to choose an autonomy level, preferably via interactive menu if available.

My enablement declaration and autonomy selection are stored in Agent Ops config.

### Suggested autonomy levels

- `off`
- `advisory`
- `assisted`
- `supervised`
- `autonomous`
- `forbidden`

The Smith may refine these.

### Suggested config layout

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

### Harness projections

Agent Ops must define projections for:

- Codex,
- OpenClaw,
- Hermes Agent,
- Claude Code,
- Cursor,
- OpenCode.

## Task 2: Periodic Actions

### Purpose

Periodic Actions provide a cross-harness equipment layer for recurring agent actions.

### User story: implement periodic action

As an Agent strapped into a harness equipped with Periodic Actions, when I have a requirement for an agent action to occur periodically, I can use the equipment to implement that action so it runs as faithfully to the requested periodicity as my harness supports.

### User story: first-session install prompt

As a repo owner with an Agent Ops repo freshly cloned on a new machine, if it has periodic actions defined, then my first agent session prompts me whether they should be installed on this machine.

My choice is persisted locally only.

### User story: manage actions

As a repo user, I can list periodic actions with:

- repo,
- extension/module,
- action name,
- period,
- installed status,
- last run timestamp,
- terse summary of last result.

I can view an action with:

- all list-view fields,
- human-friendly description,
- configuration,
- engine type,
- entrypoint script or prompt,
- last result details.

I can:

- install,
- uninstall,
- optionally trigger now,
- optionally edit period if allowed.

### Mechanism selection

At install time, choose the best mechanism unless the user overrides it:

1. Native scheduled agent actions.
2. Active loop or heartbeat.
3. Suitable hook.
4. Inference-driven pre/post task check.

### Harness-specific starting points

- OpenClaw: cron first; heartbeat fallback.
- Hermes: cron first; hooks fallback.
- Claude Code: Routines/Desktop tasks first; `/loop` for session-scoped work.
- Cursor: Automations/background agents where appropriate; rules/hooks fallback after verification.
- Codex: verify current scheduling/goal support; otherwise hooks/rules fallback.
- OpenCode: plugin/external scheduler; otherwise hooks/rules fallback.

### Suggested storage

```text
.agent-ops/
  periodic-actions.toml
  local.periodic-actions.toml
  state/
    periodic-actions.jsonl
```

## Task 3: Harness Capability Refresh

### Purpose

The Armory must periodically refresh its view of supported harnesses and depended-on capabilities.

### Required harnesses

- Codex,
- OpenClaw,
- Hermes Agent,
- Claude Code,
- Cursor,
- OpenCode.

### Required tracked fields

For each harness:

- current version,
- checked-at timestamp,
- source URLs,
- supported Harness Component types,
- key affordances,
- known limitations,
- scheduling mechanisms,
- hook/event names,
- skill discovery paths,
- plugin interfaces,
- MCP behavior.

### Change response

When depended-on capabilities change, create a high-priority issue or issue candidate to update the Framework.

Suggested issue title:

```text
[high] Refresh Framework for <harness> <capability> change
```

Include:

- current version,
- previous version,
- capability affected,
- source evidence,
- expected Framework impact,
- suggested Smith task.

### Suggested issue fallback

If GitHub issue creation is unavailable, write a markdown issue candidate under:

```text
issues/pending/high/
```

### Refresh cadence

Start weekly.

Prioritize:

1. security-relevant behavior,
2. hook blocking semantics,
3. permissions and sandboxing,
4. scheduling,
5. skill discovery/context behavior,
6. plugin packaging,
7. MCP tool exposure and context bloat.
