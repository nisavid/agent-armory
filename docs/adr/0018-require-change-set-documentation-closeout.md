# Require Change Set Documentation Closeout

Every change set must inspect agent-facing and human-facing docs that the change could plausibly affect before merge-readiness. Agents must update stale claims, gaps, inaccuracies, and appropriate mentions of deliverables, then Ralph-review the documentation changes with the applicable doc-writing guidance.

## Considered Options

- Require affected-doc closeout for every change set.
- Update only docs directly touched by implementation.
- Leave doc synchronization to later cleanup tasks.

## Consequences

- Agent-facing docs stay current without becoming broad status dumps.
- Human-facing docs can mention established deliverables when relevant without exposing maintainer-only machinery.
- Early seed-era language that says the repository has no established structure must be revised once the Framework Seed creates real precedents.
- Durable documentation closeout evidence can live in the PR body, final change summary, issue tracker, or a neutral committed closeout document when the evidence should persist with the project.
- Doc closeout reviews must include `honing-agent-facing-docs` guidance for agent-facing docs, `honing-human-facing-docs` guidance for human-facing docs, `writing-skills` guidance for skill docs or skill-like instructions, `documentation-writer` guidance for Diataxis structure, and `writing-clearly-and-concisely` guidance for clear prose when those audiences are in scope.
