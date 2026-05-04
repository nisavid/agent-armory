# Interface Decision Guide

Status: Forge Seed

Use this guide after the capability card identifies what the equipment must do. The goal is to put each requirement in the lowest reliable surface.

## Decision tree

1. Is violation dangerous, costly, irreversible, or security-relevant?
   Use a hook, permission, sandbox, approval gate, or policy-enforced config. Mention it in skills only for operator awareness.

2. Can the behavior be computed, validated, parsed, formatted, or selected deterministically?
   Use a script or tool. Have a skill call it when judgment is also needed.

3. Does the requirement expose external live state or an operation with typed inputs and outputs?
   Use MCP/tools. Add mutation gates for write behavior.

4. Is the knowledge repo-, module-, team-, or domain-local?
   Put it in local docs. Reference it from skills or root routing instead of copying it.

5. Does it vary by environment, user, machine, checkout, threshold, or mode?
   Put it in config. Use local overlays for machine-local choices.

6. Does the model need to apply procedural judgment?
   Use a skill. Keep the skill thin and point to docs, scripts, tools, and templates.

7. Does the task need a distinct identity, authority, context, model, or toolset?
   Use an Agent Profile.

8. Does the behavior need to run around lifecycle events?
   Use hooks.

9. Does the equipment need installation, versioning, sharing, or distribution as a bundle?
   Use a Harness Plugin.

## placement guide

| Requirement | Primary surface | Notes |
| --- | --- | --- |
| Hard invariant | Hook, permission, sandbox, approval gate | Fail closed when side effects or security risk require it. |
| Deterministic computation | Script or tool | Prefer stable output, clear exit codes, and safe defaults. |
| External live capability | MCP/tool | Classify read/write behavior, auth source, pagination, and side effects. |
| Project truth | Local docs | Keep current desired behavior here, not handoff history. |
| Environment choice | Config | Store typed parameters, not long policy prose. |
| Procedural judgment | Skill | Keep it concise and route to supporting surfaces. |
| Specialized worker | Agent Profile | Use when identity, tools, permissions, context, or model materially differ. |
| Lifecycle policy | Hook | Keep hooks narrow and explain allow/block/rewrite decisions. |
| Portable bundle | Harness Plugin | Bundle related skills, hooks, tools, Agent Profiles, scripts, docs, and config. |

Common anti-patterns:

- a god skill that contains policy, docs, scripts, command catalogs, and examples;
- hidden hook behavior that changes outcomes without a clear reason;
- production-looking examples without validation;
- config files used as long-form policy docs;
- duplicated local convention across docs, skills, hooks, and README surfaces.
