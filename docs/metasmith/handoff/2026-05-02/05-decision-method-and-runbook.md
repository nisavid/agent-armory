# Decision Method and Smith Runbook

## Principle: least cognitive privilege

Put only the reasoning the model must actively apply into model-facing context.

Everything else should move to lower-overhead, more reliable layers:

```text
Enforce with hooks.
Compute with scripts.
Store local truth in docs.
Parameterize with config.
Teach with skills.
Delegate with Agent Profiles.
Act through tools/MCPs.
Package with plugins.
```

## Placement guide

| Requirement | Primary home |
|---|---|
| Hard invariant | Hook, permission, sandbox |
| Deterministic computation | Script or tool |
| External live capability | MCP/tool |
| Project policy | Local docs |
| Environment settings | Config |
| Procedural judgment | Skill |
| Specialized worker | Agent Profile |
| Distribution | Plugin |

## Decision tree

1. Is violation dangerous, costly, irreversible, or security-relevant?
   - Use hook, permission config, sandbox, or approval gate.
   - Mention in skills only for awareness.

2. Can the behavior be computed, validated, parsed, or formatted deterministically?
   - Use a script or tool.
   - Have the skill call it.

3. Is the knowledge repo-, module-, team-, or domain-local?
   - Put it in local docs.
   - Have the skill reference it.

4. Does it vary by environment, user, machine, or checkout?
   - Put it in config.
   - Use local untracked overlays for machine-local choices.

5. Does the model need to apply judgment?
   - Put it in the skill body.

6. Is it only needed after a task is selected?
   - Keep it out of always-visible references.
   - Put it in the skill body or docs.

7. Does the task need a distinct model, permissions, tools, persona, or context?
   - Create an Agent Profile.

8. Does it need automatic behavior around lifecycle events?
   - Use hooks.

9. Does it expose external state or operations?
   - Use MCP/tools.

10. Does it need sharing, installation, or versioning?
    - Package it as a Harness Plugin.

## Capability creation runbook

### Step 1: Capability card

Write a capability card before implementing anything.

Include:

- name,
- purpose,
- users,
- risks,
- external systems,
- side effects,
- needed tools,
- relevant local docs,
- deterministic checks,
- hard rules,
- output contract,
- failure modes,
- target harnesses,
- evidence level.

### Step 2: Interface decision record

Create an interface decision record.

For each requirement, decide whether it belongs in:

- skill,
- MCP/tool,
- hook,
- Agent Profile,
- plugin,
- script,
- docs,
- config.

### Step 3: Local docs

If humans also need the rule, create or update local docs first.

Examples:

- `AGENTS.md`,
- `docs/engineering/pr-review.md`,
- `ops/runbook.md`,
- module-local `AGENTS.md`.

### Step 4: Scripts/tools

For deterministic work, implement scripts with:

- `--help`,
- stable JSON output,
- safe defaults,
- explicit destructive flags,
- clear exit codes,
- tests or golden output where possible.

### Step 5: Config

Add config for:

- thresholds,
- timeouts,
- allowed domains,
- autonomy levels,
- tool enablement,
- hook enablement,
- scheduling periods,
- local install choices.

### Step 6: Hooks

Add hooks for non-negotiable policy.

Decide fail mode:

- security/destructive side effects: fail closed,
- observation/telemetry: fail open with warning,
- context enrichment: fail open unless strictly required.

### Step 7: Skill

Write a thin skill.

Recommended structure:

```text
Use when
Do not use when
Preflight
Procedure
Tool/script usage
Local docs to read
Output contract
Failure handling
Safety notes
```

The skill should be a map, not the territory.

### Step 8: Agent Profile

Create an Agent Profile if the task needs a distinct worker.

Profiles should specify:

- description,
- when to use,
- model/runtime if relevant,
- tools/MCPs,
- skills,
- permissions,
- hooks,
- autonomy,
- output contract.

### Step 9: Plugin

Package into a plugin if the equipment should be portable across repos or users.

A plugin may bundle:

- skill(s),
- hook(s),
- MCP/tool definitions,
- Agent Profiles,
- scripts,
- config defaults,
- docs.

### Step 10: Test and inspect

Before shipping:

- run script tests,
- dry-run hook decisions,
- validate config,
- review context budget,
- inspect active skills/tools/profiles,
- smoke-test the skill,
- record evidence.

## Anti-patterns

### God skill

A skill that contains every workflow, command, policy, and exception.

Fix: split into narrow skills. Move project truth to docs and deterministic logic to scripts.

### Hidden hook brain

A hook that injects long instructions or changes behavior without explanation.

Fix: keep hooks small and return clear reasons.

### Script nobody else can run

A hidden agent-only script with no docs or stable output.

Fix: provide `--help`, JSON output, tests, and documentation.

### Policy in config prose

A config file that contains long natural-language policy.

Fix: use config to select modes or point to docs.

### Role explosion

A separate Agent Profile for every small variation.

Fix: create profiles only for material differences in identity, tools, permissions, or context.

### Duplicated local convention

The same rule is copied into docs, skill, hook, and README.

Fix: choose one canonical source and reference or enforce it elsewhere.

## Review questions

Before accepting Agent Equipment:

- Is the equipment’s purpose clear?
- Does it use the right component type?
- Are hard policies enforceable?
- Are deterministic parts scripted or tool-backed?
- Is local policy in docs?
- Is config human-friendly and typed?
- Are skills thin and focused?
- Are Agent Profiles scoped?
- Are harness-specific claims versioned?
- Are limitations explicit?
