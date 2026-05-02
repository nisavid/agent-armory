# AGENTS.md

## Project Role

Agent Armory is a home for equipment for agents.

Do not narrow that purpose into a specific content model, methodology, directory structure, or toolchain before the repository itself does.

## Documentation Boundary

- Keep `README.md` human-facing and limited to the project's confirmed public shape.
- Keep `AGENTS.md` agent-facing and focused on durable guidance that is not obvious from scouting the files.
- Do not add inventories, command lists, setup notes, or status summaries here when an agent can discover them directly from the repository.

## Language and Concepts

- "Equipment for agents" means skills, MCPs, plugins, scripts, policy frameworks, workflows, agent roles, and other tools that an agent or agentic system can equip.
- Treat future terms of art as project vocabulary only after they appear in committed content or the user defines them.

## Commit and PR Policy

- Use Conventional Commit subjects.
- Prefer concise scopes that name the affected domain.
- Nested slash-separated scopes are welcome when they communicate the change more precisely, for example `docs/readme` or `skills/install`.
- Before pushing changes to repo content, ensure any related or referencing repo content is updated accordingly.
- Do not stage, commit, push, or force-push unless the user asks for it.

## Operating Policy

- This repository uses agentic engineering and operations. Agents should perform assigned tasks autonomously until they reach a boundary that requires stakeholder policy or an unavailable control surface.
- Escalate when a decision or action impacts stakeholder concerns and the stakeholder's policy is unknown or uncertain.
- Escalate when an action must be taken but the agent lacks an autonomous control surface for it.
- When escalating a decision and a set of plausible, distinct choices is known, use a multiple-choice input tool if one is available in the interactive context. Include a way for the human operator to provide custom input.
- When escalating an action with a known prescribed path, present the steps clearly for the human operator to perform. Prefer fewer steps; present commands in easily copyable blocks, and prefer a single one-line command when practical.
- For every escalation, make the return contract clear: state exactly what result, confirmation, artifact, or output is needed to hand control back to the agent, and make it easy to validate.
- Prefer verified repository facts over guesses or aspirational guidance.
- When adding new agent-facing instructions, ask whether the information is durable, non-obvious, and useful before scouting a task.
- Remove guidance that becomes redundant with ordinary file discovery.
