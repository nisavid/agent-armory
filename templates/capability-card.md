# Capability Card: <name>

Status: Template
Promotion state: <specified|planned|implemented|validated|example|published>

## Purpose

State the capability in one sentence. Name the user-visible outcome, not the
implementation surface.

## Users

- Human operator:
- Root agent:
- Specialist agent:
- External system:

## Target harnesses

List each harness where this capability is intended to project. Record whether
the target is required, optional, or deferred.

## Risks

- Security:
- Privacy:
- Reliability:
- Context budget:
- Human workflow:

## External systems

Name every service, local daemon, registry, API, filesystem area, or device the
capability may read from or write to.

## Side effects

Classify side effects as read-only, external disclosure, local write, network
write, process execution, privileged operation, or irreversible mutation.

## Needed Harness Components

- Skills:
- MCP/tools:
- Hooks:
- Agent Profiles:
- Plugins:
- Scripts:
- Config:
- Docs:

## Hard rules

List the rules that must hold across every projection of this capability.

## Deterministic checks

List validators, tests, schema checks, linters, dry runs, or policy scans that
must pass before promotion.

## Output contract

Define the artifact, response shape, file change, issue update, or operational
state the capability must produce.

## Failure modes

For each known failure, state whether the capability fails open, fails closed,
asks for approval, records evidence, or retries.

## Evidence

Classify evidence using `docs/evidence-taxonomy.md`. Prefer current source or
documentation evidence over memory and guesses.

## Open questions

Keep only decisions that block implementation, validation, or promotion.
