# Adopt Agent-Operated Execution Policy

The repository is agent-operated once the human operator initiates or continues a work session. The operator reserves authority over project initiatives and session continuation, while agents drive execution, review loops, commits, publication steps, and cleanup until they reach a stakeholder decision boundary or lack an autonomous control surface.

## Considered Options

- Let agents drive assigned work after human initiation, including commits and closeout.
- Require explicit user permission before every stage, commit, push, or publication action.
- Allow agents to choose initiatives and continue sessions without human direction.

## Consequences

- Agents should not pause for routine execution steps when the work is already underway.
- Agents still escalate stakeholder decisions, unknown policy, destructive history operations, and unavailable controls.
- Root `AGENTS.md` must not contain blanket prohibitions on staging, committing, pushing, or closeout when those actions are part of assigned work.
