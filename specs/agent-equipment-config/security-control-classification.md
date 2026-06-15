# Security and Control Classification: Agent Equipment Config

Status: Equipment Blueprint
Promotion state: planned

This Equipment Design Bundle describes desired behavior and includes the first
standard-library runtime engine slice for fluent CLI operations,
effective-config, config-diff, diagnostics, plain handoff promotion, authority
checks, projection classification, read-only authoring proposal and
plan-generation surfaces, reviewed plan-artifact apply, MCP parity tool
definitions, the standalone stdio MCP server wrapper, plus reusable consumer
action decisions. It does not implement Agent Equipment beyond this runtime slice, publish assets, resolve secrets,
mutate external systems, or implement harness controls. Source mutation is
limited to explicit migration apply and reviewed plan-artifact apply for
eligible local TOML sources.

## Scope

This classification covers the v0 contract, bundle source shape, deliberate
edit boundaries, and first portable parser, merge engine, migration apply, and
reviewed plan-artifact apply slice. It does not certify a hook, permission
gate, sandbox, approval integration, plugin, harness control, external write,
or secret provider.

## Assets

- Repository and organization policy.
- Local-only operator choices.
- Checkout-local state.
- Session overrides.
- Generated cache or state.
- Secret references and their resolution status.
- Schema fragments, semantic validators, migrations, and diagnostics.
- Effective-config, config-diff, and audit outputs.
- Edit plans, diffs, refusals, and mutation audit records.
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
- MCP client JSON-RPC messages over stdio to the standalone Config MCP server
  process.

## Operation classes

| Operation | Class | V0 control expectation |
| --- | --- | --- |
| Config discovery | Read | Classify source category and provenance. |
| Effective-config generation | Read or policy decision | Explain value provenance, safety status, and diagnostics. |
| Config-diff generation | Read | Explain changed values, policy effects, and unresolved conflicts. |
| Edit proposal | Read | Emit candidate changes, rationale, affected namespaces and fields, and possible target categories without selecting or writing a source target. |
| Config patch or revise plan | Policy decision | `config patch` emits read-only reviewed `patch-layer` plan artifacts with selected source, validation, virtual post-change effective Config, authority evidence, and refusal output before any write. `onboard config` emits revise plans without writing. |
| Config create-layer plan | Policy decision | `create-layer` emits read-only reviewed `create-layer` plan artifacts for new eligible authored layers before any write. |
| Migration preview | Read | Do not rewrite source config. |
| Source migration apply | Local write | Require eligible source category, trusted provenance, dry-run-first output, explicit authority, and audit records. |
| MCP Config parity tools | Read or local write | Mirror the current CLI/runtime operation families with typed schemas, MCP annotations, read/write classification, auth source, side-effect metadata, approval requirements, failure modes, and mutation gates. |
| Standalone MCP stdio server | Process wrapper | Keep stdout protocol-only, parse newline-delimited JSON-RPC, reject malformed envelopes, delegate tool definitions and calls to the runtime, and add no network, discovery, secret-provider, or approval-bypass behavior. |
| General config apply | Local write | `config apply` consumes reviewed `patch-layer` and `create-layer` plan artifacts and requires edit intent, source eligibility, diff or create payload, authority, precondition fingerprint, all-or-nothing atomic write, durability classification, rollback stance, and audit controls before writing. |
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
- MCP parity tools classify read-only versus mutation-capable behavior before
  publication and preserve runtime refusals, source category, authority, and
  audit evidence in structured output.
- The standalone MCP server writes only JSON-RPC responses to stdout, returns
  tool refusals as result-level `isError: true` objects, and leaves local-write
  authorization to the existing runtime and host approval controls.
- MCP authoring parity keeps `config.propose`, `config.patch`, and
  `config.create_layer` read-only, and classifies `config.apply` as a local
  write that requires per-call operator authority plus harness approval when
  the MCP host supports approval friction.
- General source edits must identify intent, target, source category,
  provenance, diff or create payload, authority, validation result,
  precondition fingerprint, virtual post-change effective Config,
  all-or-nothing behavior, durability classification, rollback stance, and
  audit record before writing.
- Checkout-local state, generated cache or state, secret reference sources,
  session overrides, untrusted layers, and externally owned sources are
  read-only for Config source writes unless a future owner-specific surface
  establishes its own authority and audit boundary.
- Secret-reference edits may write metadata pointers only in eligible authored
  config; they must not write secret values or mutate a provider.
- Untrusted config cannot authorize mutation-capable behavior.
- Later or lower-authority layers cannot mint authority for an earlier Policy
  Authority gate.
- Consumers classify requested behavior as `allowed`, `advisory`, `warning`,
  `blocking`, or `unsupported` before mutation, external calls, hook execution,
  workflow changes, or durable publication.
- Issue Tracker Ops consumes effective-config evidence through a concrete
  adapter preflight projection before GitHub issue mutation. The projection
  fails closed when Config is incomplete, unsafe, conflicted, stale, untrusted,
  missing authority, unsupported, or malformed.
- Fallback behavior must not silently convert an `unsupported` or `blocking`
  mutation into a write operation; the consumer must fail closed, escalate, or
  surface a diagnostic instead.
- Harness projections must state whether controls are blocking or advisory.
- Direct secret values or secret-reference tables with embedded value payloads
  produce `secret_boundary_violation` diagnostics, redacted effective-config
  output, and an `unsafe` Config Safety Status.

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
The runtime may carry provider-local names in importable output for trusted
adapters, but CLI, MCP, log, audit, issue, PR, and handoff surfaces redact those
names before publication. Provider-specific fetching belongs to harness
projections, tools, or adapters, not to the core Config merge engine.

| Reference kind | Provider owner | Config responsibility |
| --- | --- | --- |
| `env` | Harness, script, shell, or operator-owned process environment | Preserve unresolved metadata and never read the environment variable. |
| `keychain` | Host keychain integration or operator-owned tool | Preserve unresolved metadata and never call the keychain. |
| `vault` | Vault client, harness plugin, or organization secret tooling | Preserve unresolved metadata and never authenticate to the vault. |
| `harness-secret` | Harness-native secret store or adapter | Preserve unresolved metadata and never call harness secret APIs. |
| `external` | Named external provider adapter | Preserve unresolved metadata and require the adapter to own lookup, auth, and value lifetime. |

## Known gaps

- The parser, merge behavior, and consumer decision helper are limited to the
  tested portable runtime slice.
- No hook or approval gate consumes these diagnostics yet; Issue Tracker Ops
  enforces only its adapter-owned GitHub API mutation preflight.
- No provider-specific secret resolver exists yet.
- No general source patch or revision writer exists yet.
- Onboarding output is deterministic JSON; no interactive harness projection
  consumes it yet.
- No harness projection has been verified against current harness versions for
  this equipment.

## Security decision

The current runtime slice is acceptable as a deterministic local parser, merge,
diff, migration-preview, migration-apply, plain-handoff, authority,
projection-classification, consumer action decision, edit-boundary reference,
and secret-reference reporting surface. Later implementation slices that add
provider-specific secret resolution, external mutation, broader source mutation,
or harness controls must receive their own security review.
