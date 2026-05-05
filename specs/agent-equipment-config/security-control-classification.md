# Security and Control Classification: Agent Equipment Config

Status: Equipment Blueprint
Promotion state: planned

This Forge Entry Bundle describes desired behavior only. It does not implement Agent Equipment, publish assets, or provide a runtime config engine.

## Scope

This classification covers the v0 contract and bundle source shape. It does not
certify a future effective-config engine, config mutation command, hook,
permission gate, sandbox, approval integration, plugin, or secret provider.

## Assets

- Repository and organization policy.
- Local-only operator choices.
- Checkout-local state.
- Session overrides.
- Generated cache or state.
- Secret references and their resolution status.
- Schema fragments, semantic validators, migrations, and diagnostics.
- Effective-config, config-diff, and audit outputs.
- Enforcement projections to hooks, permissions, approvals, sandboxes, tools,
  and advisory model-facing guidance.

## Trust boundaries

- Human-authored TOML to deterministic parser.
- Equipment schema fragment to shared Config merge behavior.
- Semantic validator diagnostics to mutation decision.
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
| Source migration apply | Local or network write | Require explicit audited mutation. |
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
- Config mutations produce decision/mutation audit records.
- Untrusted config cannot authorize mutation-capable behavior.
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

- No parser or merge engine exists yet.
- No hook or approval gate consumes these diagnostics yet.
- No provider-specific secret resolver exists yet.
- No onboarding flow produces partial valid config yet.
- No harness projection has been verified against current harness versions for
  this equipment.

## Security decision

The contract-first bundle is acceptable as planning and validation source. Later
implementation slices that add executable config parsing, migration, mutation,
secret resolution, or enforcement must receive their own security review.
