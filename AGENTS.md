# AGENTS.md

## Project Role

Agent Armory is a home for equipment for agents.

Do not narrow that purpose into a specific content model, methodology, directory structure, or toolchain before the repository itself does.

## Documentation Boundary

- Keep `README.md` human-facing and limited to the project's confirmed public shape.
- Keep `AGENTS.md` agent-facing and focused on durable guidance that is not obvious from scouting the files.
- Do not add inventories, command lists, setup notes, or status summaries here when an agent can discover them directly from the repository.
- Keep durable committed docs in neutral project paths named for their repository role, such as `docs/plans/`, `docs/prd/`, `docs/adr/`, `docs/agents/`, `specs/`, `templates/`, or `examples/`.
- Do not place durable committed docs under a skill-, plugin-, tool-, or workflow-specific path unless the document is intrinsically about that specific skill, plugin, tool, or workflow.
- A neutral project doc may name the skill, plugin, tool, or workflow that should execute it; the file path should still reflect the document's repository role.

## Language and Concepts

- "Equipment for agents" means skills, MCPs, plugins, scripts, policy frameworks, workflows, agent roles, and other tools that an agent or agentic system can equip.
- Treat future terms of art as project vocabulary only after they appear in committed content or the user defines them.

## Forge Conveyor

Smiths creating or modifying Agent Equipment should start with:

- `docs/agent-equipment-forge.md` for the Forge overview.
- `docs/smith-runbook.md` for the equipment creation workflow.
- `docs/story-closeout.md` for closeout gate order, review sequencing, and rerun rules.
- If the current equipment task reveals an unsatisfied Tooling Gap, use `docs/smith-runbook.md` for Tooling Request before continuing.
- `docs/interface-decision-guide.md` for choosing skills, MCP/tools, hooks, Agent Profiles, plugins, scripts, docs, and config.
- `docs/harness-capabilities.md` before making harness-specific claims.
- `templates/` for seed templates.
- `examples/` for annotated Forge Examples.
- `specs/` for Equipment Blueprints.

## Agent skills

### Issue tracker

Issues and PRDs are tracked in GitHub Issues for `nisavid/agent-armory`. See `docs/agents/issue-tracker.md`.

### Triage labels

Use the default five-label triage vocabulary. See `docs/agents/triage-labels.md`.

### Domain docs

Use single-context domain docs. See `docs/agents/domain.md`.

## Commit and PR Policy

- Use Conventional Commit subjects.
- Prefer concise scopes that name the affected domain.
- Nested slash-separated scopes are welcome when they communicate the change more precisely, for example `docs/readme` or `skills/install`.
- Before pushing changes to repo content, ensure any related or referencing repo content is updated accordingly.
- Before treating a change set as merge-ready, perform the security analyses applicable to that change set and record the commands, artifacts, findings, fixes, suppressions, or explicit non-applicability in the closeout.
- Before committing or externally projecting closeout evidence, classify each evidence artifact by durability. Commit or publish durable project evidence and portable review summaries; summarize instance-scoped scratch artifacts by scope, disposition, and durable conclusions instead of treating raw logs, reports, local paths, or tool work directories as project truth.
- Security closeout evidence belongs in the PR body, final change summary, issue tracker, or a neutral committed security document when the evidence is durable project material. Do not bury it in transient tool logs.
- Use Codex Security workflows when they apply. A change set that introduces or materially changes executable code, hooks, MCP/tool definitions, permissions, secrets handling, network/file/process side effects, package metadata, or security policy must receive a Codex Security scan or a documented reason why a narrower security action is sufficient.
- Resolve reportable security findings before merge-readiness, or record a stakeholder-approved deferment with the tracking issue and risk rationale.
- Near the end of every cohesive change set, and before treating it as merge-ready, inspect every agent-facing and human-facing doc that the change could plausibly affect. Update gaps, inaccuracies, stale status language, and appropriate mentions of the change-set deliverables.
- Apply the repo's doc-honing standards to that inspection: agent-facing docs must stay narrow, durable, and discoverable; human-facing docs must stay audience-fit, current, and free of maintainer-only clutter.
- If the inspection changes no docs, record the rationale in the PR body, final change summary, issue tracker, or neutral committed closeout document.
- Documentation closeout evidence belongs in the PR body, final change summary, issue tracker, or a neutral committed closeout document when the evidence is durable project material.
- Ralph-review documentation closeout changes with reviewer guidance that includes the applicable doc-writing standards: `honing-agent-facing-docs` for agent-facing docs, `honing-human-facing-docs` for human-facing docs, `writing-skills` for skill docs or skill-like instructions, `documentation-writer` for Diataxis structure, and `writing-clearly-and-concisely` for clear prose.
- Follow `docs/story-closeout.md` for closeout gate order, interdependency rules, review sequencing, and rerun rules.
- Before story closeout, run a Cross-Boundary Coherence Ralph Review that checks behavior and evidence across PRD, specs, plan, implementation, validation, security, docs, issue/PR projection, and release or handoff surfaces.
- Before story closeout, run a Story Quality Ralph Review that checks DX, UX, code quality, architecture, robustness against unspecified interactions and attack paths, lessons from prior pathological dev/ops cycles, and alignment with the strategic vision.
- Once work is underway, agents may stage, commit, push, open PRs, update issues, and perform closeout steps when those actions advance the assigned work and respect the repository's current review, verification, and stakeholder boundaries.
- Do not force-push or perform destructive history operations unless the user explicitly asks for that action.

## Operating Policy

- This repository uses agentic engineering and operations. Agents should perform assigned tasks autonomously until they reach a boundary that requires stakeholder policy or an unavailable control surface.
- The user reserves authority over project initiatives and over initiation or continuation of work sessions. Within an active user-directed session, agents should drive execution, review loops, commits, publication steps, and cleanup unless escalation is required.
- Escalate when a decision or action impacts stakeholder concerns and the stakeholder's policy is unknown or uncertain.
- Escalate when an action must be taken but the agent lacks an autonomous control surface for it.
- When escalating a decision and a set of plausible, distinct choices is known, use a multiple-choice input tool if one is available in the interactive context. Include a way for the human operator to provide custom input.
- When escalating an action with a known prescribed path, present the steps clearly for the human operator to perform. Prefer fewer steps; present commands in easily copyable blocks, and prefer a single one-line command when practical.
- For every escalation, make the return contract clear: state exactly what result, confirmation, artifact, or output is needed to hand control back to the agent, and make it easy to validate.
- Prefer verified repository facts over guesses or aspirational guidance.
- When adding new agent-facing instructions, ask whether the information is durable, non-obvious, and useful before scouting a task.
- Remove guidance that becomes redundant with ordinary file discovery.
