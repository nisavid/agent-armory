# Security and Control

Status: Forge Seed

Security and control decisions belong in the equipment design, not only in final review. Smiths classify authority, side effects, and gates before implementation.

The persistent [Repository Threat Model](security/threat-model.md) is the baseline for Forge Seed security closeout and future security scans.

## least privilege

Use least privilege across model context, tools, credentials, filesystem access, network access, and mutation authority.

Grant only the tools, permissions, context, and secrets references needed for the capability. Prefer read-only defaults, scoped credentials, explicit allowlists, and narrower Agent Profiles for specialized work.

## mutation gates

Mutation gates protect actions that change files, issues, pull requests, repositories, external systems, schedules, credentials, or user-visible state.

Use hooks, permissions, sandboxes, approvals, dry runs, explicit destructive flags, and audit records according to blast radius. Fail closed for security-sensitive or destructive actions unless stakeholder policy says otherwise.

## secrets

Never put secrets, personal credentials, private tokens, or host-specific credential paths in Forge Canon, examples, templates, specs, skills, hooks, scripts, or config.

Use secret references or documented environment contracts. Redact secret-like values in logs, hook output, tool results, and examples.

## hooks

Hooks are appropriate for hard policy, lifecycle checks, approvals, redaction, and side-effect annotation.

Keep hooks narrow and observable. A hook should explain whether it allowed, blocked, rewrote, warned, or recorded an event. Long instructions and hidden reasoning belong in docs or skills, not hook payloads.

## MCP/tool side effects

Every MCP/tool definition records read/write classification, side effects, auth source, approval requirements, rate limits, pagination, failure modes, and rollback or cleanup expectations where applicable.

Mutation-capable tools need control surfaces outside model memory. Use permissions, hooks, approvals, sandboxing, or scoped credentials rather than relying on skill prose alone.

## reflection and cognition equipment

Reflection and cognition equipment can expose private session context, create
issue noise, change future routing, or mutate policy and priority surfaces.

Treat reflected content as sensitive until classified. Before projecting a
Reflection Finding outside the local session, decide what context may be
disclosed, whether the finding is advisory or authoritative, and which control
surface is allowed to route, prioritize, or mutate follow-up work.

## examples caveat

Forge Examples demonstrate the decision method. They are not installable, validated, or published equipment unless they move through the Equipment Promotion Path.

Examples must avoid production-looking authority, fake secrets, real credential paths, and claims that imply a harness feature was validated when it was only illustrated.
