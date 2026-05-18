# Security and Control Classification: Agent Equipment Config

Status: Equipment Blueprint
Promotion state: planned

This Equipment Design Bundle describes desired behavior and includes the first
standard-library runtime engine slice for effective-config, config-diff,
diagnostics, plain handoff promotion, authority checks, and projection
classification. It does not implement Agent Equipment beyond this runtime
slice, publish assets, resolve secrets, mutate external systems, or implement
harness controls. Source mutation is limited to explicit migration apply for
eligible local TOML sources.

## Scope

This classification covers the v0 contract, bundle source shape, and first
portable parser, merge engine, and migration-apply slice. It does not certify a
hook, permission gate, sandbox, approval integration, plugin, harness control,
external write, or secret provider.

## Assets

- Repository and organization policy.
- Local-only operator choices.
- Checkout-local state.
- Session overrides.
- Generated cache or state.
- Secret references and their resolution status.
- Schema fragments, semantic validators, migrations, and diagnostics.
- Effective-config, config-diff, and audit outputs.
- Consumer action decisions derived from effective Config output.
- Enforcement projections to hooks, permissions, approvals, sandboxes, tools,
  and advisory model-facing guidance.

## Trust boundaries

- Human-authored TOML to deterministic parser.
- Equipment schema fragment to shared Config merge behavior.
- Semantic validator diagnostics to mutation decision.
- Effective-config evidence to consumer action decision.
- Committed config to local-only and session-scoped overrides.
- Policy Authority to later overrides and lower-authority layers.
- Secret reference metadata to harness-specific secret resolution.
- Effective-config output to Agents, humans, tools, hooks, and review evidence.
- Issue Tracker Ops policy to external GitHub mutation behavior.

## Operation classes

| Operation | Class | V0 control expectation |
| --- | --- | --- |
| Config discovery | Read | Classify source category and provenance. |
| Effective-config generation | Read or policy decision | Explain value provenance, safety status, and diagnostics. |
| Config-diff generation | Read | Explain changed values, policy effects, and unresolved conflicts. |
| Migration preview | Read | Do not rewrite source config. |
| Source migration apply | Local write | Require eligible source category, trusted provenance, dry-run-first output, explicit authority, and audit records. |
| Consumer action decision | Policy decision | Fail closed for mutation-capable behavior unless effective Config is usable, authority and semantics pass, and the required capability is supported. |
| Enforcement projection | Advisory or blocking control | Label blocking support versus advisory fallback. |
| Secret reference resolution | Sensitive read | Report reference and status, never secret value. |

## Controls

- Secret references store typed pointers, not secret values.
- Config Safety Status is machine-visible.
- Mutation-capable behavior fails closed unless status is `usable`.
- Blocked overrides remain visible as conflict diagnostics.
- Same-precedence collisions remain unresolved until the operator, policy, or a
  higher-authority layer resolves them.
- Read-time migrations do not mutate source config.
- Migration apply writes only eligible local TOML sources and produces
  decision/mutation audit records.
- Untrusted config cannot authorize mutation-capable behavior.
- Later or lower-authority layers cannot mint authority for an earlier Policy
  Authority gate.
- Consumers classify requested behavior as `allowed`, `advisory`, `warning`,
  `blocking`, or `unsupported` before mutation, external calls, hook execution,
  workflow changes, or durable publication.
- Fallback behavior must not silently convert an `unsupported` or `blocking`
  mutation into a write operation; the consumer must fail closed, escalate, or
  surface a diagnostic instead.
- Harness projections must state whether controls are blocking or advisory.

## Conflict diagnostics

V0 diagnostics cover:

- blocked override,
- same-precedence collision,
- schema conflict,
- semantic conflict,
- missing authority.

Diagnostics are structured outputs. They do not silently repair config or hide a
blocked value.

## Secret references

Valid secret references are typed pointers with:

- `kind`, such as `env`, `keychain`, `vault`, `harness-secret`, or `external`;
- `name`, the provider-local secret name;
- optional `scope`, such as repository, organization, host, session, or harness;
- optional `required_for`, the behavior that needs it.

Effective-config output reports reference identity and resolution status only.
Provider-specific fetching belongs to harness projections or future tools, not
to the v0 contract itself.

## Known gaps

- The parser and merge behavior are limited to the tested portable CLI slice.
- No hook or approval gate consumes these diagnostics yet.
- No provider-specific secret resolver exists yet.
- Onboarding output is deterministic JSON; no interactive harness projection
  consumes it yet.
- No harness projection has been verified against current harness versions for
  this equipment.

## Security decision

The current runtime slice is acceptable as a deterministic local parser, merge,
diff, migration-preview, migration-apply, plain-handoff, authority,
projection-classification, and secret-reference reporting surface. Later
implementation slices that add provider-specific secret resolution, external
mutation, broader source mutation, or harness controls must receive their own
security review.
