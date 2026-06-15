# Agent Equipment Config

Status: Published runtime slice
Promotion state: published

Agent Equipment Config is the shared configuration primitive for Agent
Equipment. The published runtime slice provides a local, standard-library
Python engine for loading authored TOML layers, composing schema fragments,
explaining effective configuration, comparing config outputs, and preserving
plain equipment-specific handoffs. It exposes fluent CLI operations for
resolve, validate, diff, onboarding, read-only authoring proposal and plan
generation, reviewed plan apply, and migration flows, plus reusable consumer
action decision output for importable consumers. The Config bundle also defines
deliberate edit boundaries for revision and MCP authoring surfaces.

Use this guide when a Smith is making Config-aware equipment or when a Wielder
needs to provide local or session configuration for equipment that already
declares a schema fragment.

Use the
[Config shop card](shop-cards/agent-equipment-config.md) when deciding whether
the stocked runtime slice fits a Wielder or Outfitter task. Use the
[Config integration guide](agent-equipment-config-integration.md) for the
Smith, Wielder, and Outfitter paths that connect equipment, harness surfaces,
and the current runtime.

## What to use

- Runtime: `tools/agent_equipment_config.py`
- Product requirements: `docs/prd/agent-equipment-config.md`
- Integration guide: `docs/equipment/agent-equipment-config-integration.md`
- Blueprint: `specs/agent-equipment-config/`
- MCP tool specs: `specs/agent-equipment-config/mcp-tools.md`
- Edit boundaries: `specs/agent-equipment-config/edit-boundaries.md`
- Authoring plan/apply model:
  `specs/agent-equipment-config/authoring-plan-apply-model.md`
- Example layer: `templates/config/agent-equipment-config-example.toml`
- Plain Issue Tracker Ops handoff:
  `templates/config/issue-tracker-ops-plain-handoff.toml`
- Generic config template: `templates/config/example.toml`

The runtime reads local files supplied by the caller and emits JSON to stdout.
It does not discover files by itself, resolve secret values, mutate external
systems, or enforce harness controls. Source mutation surfaces are
`migrate config apply`, which rewrites eligible local TOML sources after an
explicit authority gate, and `config apply`, which consumes reviewed
`patch-layer` and `create-layer` artifacts from a file or stdin. Both write
paths recheck preconditions and record audit evidence. The implementation
command `migration-apply --apply` remains available for debugging the migration
runtime path. Harnesses, skills, hooks, scripts, or operators choose which layer
paths to pass in and what to do with the resulting classification.

`config propose`, `config patch`, and `create-layer` emit authoring proposal or
reviewed plan artifacts. `config apply` is the only non-migration source write
surface and must consume those reviewed artifacts. Revision writes must follow
the edit boundary contract before they write any source.

Use the fluent CLI operations as the supported invocation surface:
`config resolve`, `config validate`, `config diff`, `config propose`,
`config patch`, `create-layer`, `config apply`, `onboard config`,
`migrate config preview`, and `migrate config apply`. The implementation
command names remain available as the debugging path. When a harness exposes
Config MCP tools, use
`config.resolve`, `config.validate`, `config.diff`, `config.propose`,
`config.patch`, `config.create_layer`, `config.apply`, `onboard.config`,
`migrate.config_preview`, and `migrate.config_apply` for the same operation
families. The importable runtime exposes tool metadata through
`mcp_tool_definitions()` and direct dispatch through `call_mcp_tool()`. The
standalone stdio MCP server is:

```bash
python3.14 tools/agent_equipment_config_mcp_server.py
```

The server is a protocol wrapper around the importable runtime. It does not
discover config paths, resolve secret values, call networks, or add a separate
Config product surface. Use the CLI commands above when the harness cannot
launch an MCP server or when command output is the clearer review artifact.
Local-write MCP tools still require their per-call authority and host approval
friction before a mutation-capable call.

## Load contract

Agent Equipment Config has an explicit-load contract. The core runtime never
walks the filesystem, imports plugins, scans packages, or chooses a default
config path. A script, hook, harness adapter, repository tool, or operator
discovers paths, selects the intended sources, orders same-precedence inputs,
registers schema fragments, and invokes the runtime.

Python callers import `tools.agent_equipment_config` and pass `Path` values plus
`SchemaFragment` objects to `effective_config`, `config_onboarding_plan`, or
`migration_apply`. Config-aware consumers can call `evaluate_consumer_config`
to load effective Config through the same explicit-load contract and receive a
consumer action decision, or call `consumer_action_decision` when they already
have effective-config output. CLI callers pass layer paths with `--layer`,
session handoff paths with `--plain-handoff`, and supported schema fragments
through explicit fragment flags. The current CLI exposes `--issue-tracker-ops`
as the bundled fragment flag; arbitrary schema-fragment CLI registration belongs
to a later CLI surface.

Every authored TOML layer passed through `--layer` must declare `name` and
`category`:

```toml
[agent_equipment_config.layer]
name = "repository policy"
category = "committed durable config"
```

`name` selects Layer Precedence. `category` selects the source category.
`trusted` is optional and defaults to `true`; set `trusted = false` for inputs
that may be useful for diagnostics but must not authorize mutation. The runtime
preserves provenance in effective-config fields, diagnostics, discovery
proposals, migration previews, refusals, and audit records.

| Source category | Input surface | Caller responsibility | Core discovery | Notes |
| --- | --- | --- | --- | --- |
| `committed durable config` | `--layer` or `layer_paths` | Discover, select, order, and pass source paths | None | Eligible for migration apply and reviewed plan-artifact apply after authority gates. |
| `local-only operator config` | `--layer` or `layer_paths` | Discover, select, order, and pass source paths | None | Eligible for migration apply and reviewed plan-artifact apply after authority gates; not project truth. |
| `checkout-local state` | `--layer` or `layer_paths` | Discover, select, order, and pass source paths | None | Read-only for Config source writes. |
| `generated cache or state` | `--layer` or `layer_paths` | Discover, select, order, and pass source paths | None | Read-only for Config source writes. |
| `secret reference source` | `--layer` or `layer_paths` | Discover, select, order, and pass source paths | None | Carries unresolved secret metadata, not secret values. |
| `session override` | `--layer`, `--plain-handoff`, `layer_paths`, or `plain_handoff_paths` | Discover, select, order, and pass source paths | None | Plain handoffs are promoted to session overrides with promotion provenance. |

Schema fragments must be available before validation. Equipment owns its
namespace, schema fields, defaults, semantic validators, and migrations. Shared
Config composes the fragments it receives; it does not discover fragments from
equipment packages, hook directories, plugins, or repository files.

The load contract does not resolve secrets, create or mutate config outside the
supported source-write operations, enforce harness controls, define universal
filenames, or decide whether a caller may proceed after a blocking
classification.

## Secret-reference provider boundary

Agent Equipment Config represents secrets as provider references, not as stored
secret values. A valid secret reference has:

- `kind`: `env`, `keychain`, `vault`, `harness-secret`, or `external`;
- `name`: the provider-local name or handle;
- optional `scope`: repository, organization, host, session, harness, or another
  provider-owned scope;
- optional `required_for`: the behavior that needs the secret.

The runtime reports recognized references as unresolved metadata and adds
`resolution_status = "unresolved"`. The importable Python result may carry
`kind`, `name`, `scope`, `required_for`, and `resolution_status` so a trusted
harness, tool, or adapter can resolve the value outside Config. The core Config
runtime never reads environment variables, keychains, vaults, harness secret
stores, external secret systems, or provider-specific credential files.

Provider resolution belongs to the surface that owns the provider. That surface
must own authentication, provider lookup, scope checks, retries, failure
classification, value lifetime, and any private audit trail. Config output is
only decision evidence for whether resolution is needed and which provider
handle the owner should use.

CLI and MCP output redact provider-local secret names before writing JSON to the
caller. Logs, diagnostics, audit previews, PR evidence, issue comments, and
handoffs must use the redacted form unless the artifact is explicitly private to
the provider owner. Effective-config and config-diff projections may report
reference kind, scope, required behavior, and unresolved status; they must not
publish secret values.

If a sensitive field supplies a direct value instead of a secret reference, or a
secret-reference table includes a direct value payload, Config classifies the
result as `unsafe`, emits a `secret boundary violation` diagnostic, and redacts
the value in effective-config output with
`redaction_status = "blocked_direct_secret_value"`.

## Consumption contract

Consuming equipment turns effective Config output into its own action decision.
Shared Config supplies typed fields, provenance, diagnostics, safety status,
migration previews, plain-handoff promotion records, and an enforcement
projection. The consumer owns the behavior-specific interpretation.

A Config-aware consumer must:

1. Register its schema fragment before validation.
2. Keep defaults, required fields, migrations, and semantic validators in its
   own namespace.
3. Request the behavior it is evaluating, such as advisory or mutation, before
   reading the effective output.
4. Read `safety_status`, diagnostics, policy authority evidence, secret
   reference metadata, and `enforcement_projection` before starting side
   effects.
5. Produce a consumer action decision before mutation, external calls, hook
   execution, workflow changes, or durable publication.

The consumer action decision states are:

| State | Meaning |
| --- | --- |
| `allowed` | The requested behavior may run. Effective Config is `usable`, required semantic validators pass, and the harness or equipment supports the needed capability. |
| `advisory` | Read-only, dry-run, explanation, or model-facing guidance may continue, but the decision does not authorize side effects. |
| `warning` | The requested behavior may run only with visible non-blocking diagnostics, such as deprecation or migration-preview evidence. |
| `blocking` | The requested behavior must not run. Mutation-capable behavior fails closed when effective Config is missing, incomplete, unsafe, stale, untrusted, conflicted, or missing required Policy Authority. |
| `unsupported` | The consumer or harness cannot apply a required capability. Mutation-capable behavior fails closed; the consumer may fall back to an explicit advisory or plain-handoff path when that path is safe. |

The runtime's `enforcement_projection` is decision evidence, not the whole
consumer decision. `consumer_action_decision` maps effective-config evidence,
consumer-required capabilities, supported capabilities, diagnostics, and
migration previews to `allowed`, `advisory`, `warning`, `blocking`, or
`unsupported`. `evaluate_consumer_config` combines explicit layer loading with
that decision helper for importable consumers.

Issue Tracker Ops is the current concrete adapter projection. When
`tools/issue_tracker_ops.py` receives Config input, it emits
`config.consumer_enforcement_projection` for
`issue_tracker_ops.github_api_mutation_preflight`. For `--execute` mutation
commands, `adapter_action = "allow"` permits the GitHub API call and
`adapter_action = "block"` refuses it before `gh` is called. The adapter has no
approval surface; approval behavior is reported as `not_supported`, and
blocking or unsupported Config output can only fall back to explicit advisory
dry-run behavior.

Fallback is progressive. When shared Config is absent, the consumer uses its
plain equipment-specific session handoff. When effective Config is present but
does not authorize the requested behavior, the consumer may continue only with
a narrower explicit behavior such as dry-run, read-only explanation, advisory
guidance, or no action. A fallback must not silently turn an unsupported or
blocking mutation into a write.

## MCP parity

The MCP surface mirrors the fluent CLI operation families instead of defining a
separate Config product. Each MCP tool has typed inputs and structured output,
and each tool definition records read/write classification, auth source, side
effects, approval requirements, mutation gates, and failure modes.

| MCP tool | Paired CLI | Class |
| --- | --- | --- |
| `config.resolve` | `config resolve` | read-only |
| `config.validate` | `config validate` | read-only |
| `config.diff` | `config diff` | read-only |
| `config.propose` | `config propose` | read-only |
| `config.patch` | `config patch` | read-only policy decision |
| `config.create_layer` | `create-layer` | read-only policy decision |
| `config.apply` | `config apply` | local write |
| `onboard.config` | `onboard config` | read-only |
| `migrate.config_preview` | `migrate config preview` | read-only |
| `migrate.config_apply` | `migrate config apply` | local write |

Authoring MCP parity uses the same operation family as the fluent CLI.
Proposal, patch-plan, and create-layer tools are read-only. `config.apply`
accepts only a reviewed plan artifact and is a local write. The runtime
preserves reviewed plan artifacts, precondition fingerprints, virtual
post-change effective Config validation, stable refusal codes, all-or-nothing
apply, durability classification, project-truth status, rollback stance, and
refusal of secret values, provider credential material, provider mutation, and
unsupported source categories.

MCP callers pass explicit `layer_paths`, optional `plain_handoff_paths`,
registered `fragments`, and the requested behavior. `config.diff` accepts
typed `before` and `after` effective-config objects. `migrate.config_apply`
uses the migration apply gates for eligible source category, trusted
provenance, usable projected Config, final source precondition checking, and
audit output. The MCP tool also requires per-call
`apply_authority = "operator"`. See [Migration apply](#migration-apply) for
detailed gate definitions and satisfaction criteria for `migrate.config_apply`;
`config.diff` remains a read-only comparison of supplied effective-config
objects.

Use MCP when a harness exposes these tools and the agent benefits from typed
input and output. Fall back to the fluent CLI when MCP is unavailable, when a
human needs a copyable command, or when command-line evidence comparison is
clearer for review.

## Smith path

When designing Config-aware equipment:

1. Define the equipment's plain session-scoped config shape first.
2. Register that shape as a namespaced schema fragment when shared Config is
   available.
3. Keep generic layering, Policy Authority, conflict diagnostics, migration
   previews, and effective-config explanation in Agent Equipment Config.
4. Keep equipment-specific behavior, defaults, and safety rules in the
   consuming equipment's schema fragment and semantic validators.
5. Keep provider secret resolution and harness blocking controls outside the
   core Config runtime unless a later projection slice explicitly owns them.

The schema fragment boundary prevents Agent Equipment Config from depending on
the equipment that consumes it.

## Wielder path

When supplying config:

- Put durable project policy in committed config.
- Put machine-local choices in local-only config.
- Put checkout-local state in checkout-local state.
- Put per-session choices in session overrides or a plain handoff.
- Use secret references instead of secret values; direct secret values make
  effective Config `unsafe`.
- Treat `blocking` projection output as a stop signal until the relevant
  policy owner or harness adapter decides otherwise.

Mutation-capable behavior should proceed only when the effective Config Safety
Status is `usable` and the required Policy Authority is present for the
requested behavior.

## Example layer

`templates/config/agent-equipment-config-example.toml` is a minimal
repository-policy layer. It demonstrates:

- layer metadata;
- fragment version metadata;
- a usable repository policy authority;
- non-overridable policy gates;
- equipment-specific values under the consuming equipment namespace.

Run it through the current Issue Tracker Ops pressure fragment with:

```bash
python3 tools/agent_equipment_config.py config resolve \
  --layer templates/config/agent-equipment-config-example.toml \
  --issue-tracker-ops \
  --requested-behavior advisory
```

The output should be `usable` for advisory dry-run behavior. Use
`config validate` when a script or hook needs the lower-noise pass/fail report
and exit status. It checks mutation readiness by default so authority and
semantic blockers are visible unless the caller explicitly requests advisory
validation with `--requested-behavior advisory`. Mutation behavior remains
governed by the consuming equipment's semantic validators and the selected
harness projection.

## Onboarding and authoring

Use `onboard config` when a Smith or Wielder needs machine-visible next steps
instead of hidden preference. The command reports:

- `onboarding_status` for missing shared Config, missing config data,
  interrupted partial output, resumed completion, restarted authoring,
  blocked config, or complete config;
- `partial_config` with schema-valid sections, missing required fields, and
  unsafe write modes blocked while policy is incomplete;
- `handoff_behavior` for plain session handoffs and mutation-capable behavior;
- `discovery_proposals` for committed durable config, local-only operator
  config, checkout-local state, generated cache or state, secret reference
  source, and session override categories supplied by the caller, including
  the explicit load-contract fields `core_discovery`, `caller_responsibility`,
  `input_surfaces`, `provenance_requirement`, and `secret_resolution`;
- `revision_plan` for re-onboarding selected sections while preserving
  unrelated policy.

When shared Config is absent, omit layer and plain-handoff paths; the runtime
fails instead of returning a plan that ignores supplied inputs.

Example:

```bash
python3 tools/agent_equipment_config.py onboard config \
  --layer templates/config/agent-equipment-config-example.toml \
  --issue-tracker-ops \
  --requested-behavior mutation \
  --onboarding-state resume \
  --revise-section issue_tracker_ops
```

Smiths author the equipment namespace: schema fragments, defaults, semantic
validators, policy gates, and any equipment-specific safety rules. Wielders
supply local, checkout, or session values without weakening committed policy
authority. Re-onboarding should revise the selected section and preserve
unselected sections unless a policy owner deliberately changes them. Unknown
section names fail before emitting a plan.

## Authoring CLI workflow

Use the authoring CLI when a Smith or Wielder needs to propose or apply a
non-migration Config source change. The workflow is proposal, reviewed plan,
then apply. The proposal and plan commands write no sources. `config apply` is
the only non-migration authoring command that writes local TOML, and it accepts
only reviewed `patch-layer` or `create-layer` JSON artifacts from `--plan PATH`
or `--plan -`.

This workflow documents current CLI/runtime and MCP authoring parity behavior.
Revision writes and richer audit/query behavior remain outside the #23 blocking
path unless the Config PRD scope changes.

Start with a target-agnostic proposal:

```bash
python3.14 tools/agent_equipment_config.py config propose \
  --issue-tracker-ops \
  --set issue_tracker_ops.mode=execute \
  --set issue_tracker_ops.external_disclosure=allowed \
  --rationale "enable reviewed live tracker mutation"
```

The proposal names affected fields and possible target categories, but it does
not select a source:

```json
{
  "operation": "config propose",
  "plan_surface": "proposal",
  "source_target": null,
  "possible_target_categories": [
    "committed durable config",
    "local-only operator config"
  ],
  "refusal_codes": []
}
```

After review, select one eligible authored source and emit a reviewed
`patch-layer` plan artifact. A committed durable Config target is project truth
after a successful apply:

```bash
python3.14 tools/agent_equipment_config.py config patch \
  --layer configs/agent-equipment.toml \
  --source-target configs/agent-equipment.toml \
  --issue-tracker-ops \
  --set issue_tracker_ops.mode=execute \
  --set issue_tracker_ops.external_disclosure=allowed \
  --plan-authority operator \
  --rationale "enable reviewed live tracker mutation" \
  > /tmp/config-patch-plan.json
```

A local-only operator target follows the same reviewed plan contract, but the
source category and audit evidence classify it as local evidence, not project
truth. Set `OPERATOR_CONFIG` to a caller-discovered local-only directory and do
not commit it as project policy:

```bash
python3.14 tools/agent_equipment_config.py create-layer \
  --destination "$OPERATOR_CONFIG/agent-equipment.toml" \
  --layer-name "user/operator local overrides" \
  --source-category "local-only operator config" \
  --issue-tracker-ops \
  --set issue_tracker_ops.mode=dry-run \
  --set issue_tracker_ops.external_disclosure=blocked \
  --plan-authority operator \
  > /tmp/config-create-layer-plan.json
```

Plan artifacts are review records and apply inputs. They include the plan kind,
source target, source category, source identity, precondition fingerprint, diff
or create payload, authority evidence, validation result, virtual post-change
effective Config, audit preview, refusal codes, durability classification, and
rollback stance.

Apply a reviewed plan from a file:

```bash
python3.14 tools/agent_equipment_config.py config apply \
  --plan /tmp/config-patch-plan.json \
  --apply-authority operator
```

Apply can also read the reviewed plan from stdin:

```bash
python3.14 tools/agent_equipment_config.py create-layer \
  --destination "$OPERATOR_CONFIG/agent-equipment.toml" \
  --layer-name "user/operator local overrides" \
  --source-category "local-only operator config" \
  --issue-tracker-ops \
  --set issue_tracker_ops.mode=dry-run \
  --set issue_tracker_ops.external_disclosure=blocked \
  --plan-authority operator |
python3.14 tools/agent_equipment_config.py config apply \
  --plan - \
  --apply-authority operator
```

Successful apply output records mutation audit evidence:

```json
{
  "operation": "config apply",
  "plan_kind": "patch-layer",
  "applied": true,
  "result": "applied",
  "refusal_codes": [],
  "audit_records": [
    {
      "action": "config authoring apply mutation",
      "result": "applied",
      "source_artifact_durability": "durable project evidence",
      "project_truth_after_apply": true,
      "rollback": "atomic source write completed; rollback by reverting committed config or restoring the local operator file"
    }
  ]
}
```

Refusal output uses stable codes so tools can route failures without parsing
prose. For example, a generated cache target refuses before any write:

```json
{
  "operation": "config patch",
  "plan_kind": "patch-layer",
  "source_category": "generated cache or state",
  "refusal_codes": ["source_category_ineligible"],
  "audit_preview": {
    "result": "refused",
    "project_truth_after_apply": false,
    "rollback": "no source write has occurred; apply rechecks the reviewed plan before mutation"
  }
}
```

Secret-reference authoring may write a whole pointer object in an eligible
authored Config layer, such as `{"kind":"env","name":"GH_TOKEN"}`. Config
redacts the provider-local name in CLI output. Direct secret values, value
payloads inside a secret-reference object, and nested provider-metadata edits
such as `issue_tracker_ops.github_token.name=GH_TOKEN` refuse with
`secret_boundary_violation`. Config does not perform provider lookup,
authentication, secret creation, rotation, deletion, or provider configuration
mutation.

## Edit and mutation boundaries

Use the edit-boundary contract when a Smith designs a Config-aware source edit
surface or when a Wielder evaluates whether an agent may change config. The
supported edit intents are:

| Intent | Current boundary |
| --- | --- |
| `propose` | Target-agnostic candidate output only; no source write. |
| `patch` | Read-only `patch-layer` plan artifacts with source selection, validation, authority, virtual post-change effective Config, diff, and audit preview; no source write. |
| `migrate` | Supported through `migrate config preview` and `migrate config apply` for registered schema migrations. |
| `revise` | Supported as `onboard config` section selection; source writing is deferred. |
| `apply` | Supported for reviewed `patch-layer` and `create-layer` plan artifacts through `config apply`, and for registered migrations through `migrate config apply`. |

Only `committed durable config` and `local-only operator config` are eligible
for the current migration apply write path. `checkout-local state`, `generated
cache or state`, `secret reference source`, `session override`, untrusted
layers, and externally owned sources are read-only to Config write surfaces.
Config may emit proposals or diagnostics for those sources, but the owning
tool, generator, secret provider, handoff owner, or external system must perform
any source mutation through its own audited path.

A source write must have explicit intent, selected source target, reviewable
diff or change set, provenance, applicable authority, schema and semantic
validation, a clean Config Safety Status for the requested behavior, final
source precondition checking, and audit records. Refusals must identify the
source, category, namespace, authority evidence, and reason. A write must stop
when it would cross source ownership, secret, authority, validation, or
harness-support boundaries.

The current authoring surfaces use deterministic JSON reviewed plan artifacts.
`config propose` stays target-agnostic. `config patch` selects one existing
source and emits a `patch-layer` artifact. `create-layer` emits a
`create-layer` artifact for a new authored layer. These artifacts carry the plan
kind, source target, source category, precondition fingerprint, diff or create
payload, authority evidence, validation result, virtual post-change effective
Config status, audit preview, refusal codes, durability classification, and
rollback stance. `config apply` accepts a reviewed artifact from a file or
stdin, rechecks the selected source or destination, authority, validation,
semantic safety, and secret boundaries, then writes only eligible
`committed durable config` or `local-only operator config` atomically with
all-or-nothing audit evidence.

Secret-reference authoring is limited to whole pointer objects in eligible
authored config. Nested provider-metadata patch paths and direct secret values
refuse with stable secret-boundary evidence.

## Migration apply

Use `migrate config preview` when stale schema metadata has a registered
migration and the operator wants a machine-readable dry run before any source
rewrite. Use `migrate config apply` for the authorized write path. It reports:

- exact field rename and fragment-version changes;
- the source layer, source category, and write target;
- refusal records for unsafe, incomplete, untrusted, stale-without-migration,
  ineligible, or authority-blocked inputs;
- audit records with artifact durability, project-truth status, authority, and
  rollback stance.

The apply boundary writes only eligible source categories:

- `committed durable config`, recorded as durable project evidence and project
  truth;
- `local-only operator config`, recorded as instance-scoped local evidence and
  not project truth.

`generated cache or state`, `checkout-local state`, `session override`,
`secret reference source`, and untrusted layers are read-only for migration
apply. A real write requires `migrate config apply` plus explicit operator
authority or a trusted configured `config_migration_apply` authority marker.

Example dry run:

```bash
python3 tools/agent_equipment_config.py migrate config preview \
  --layer templates/config/agent-equipment-config-example.toml \
  --issue-tracker-ops
```

## Review and maintenance

Update this guide when:

- a Config CLI operation changes its output shape or exit-code contract;
- an equipment line consumes Config directly;
- consumer action decision output changes;
- onboarding status, handoff, discovery, or revision output changes;
- a harness projection turns advisory classification into blocking behavior;
- secret-reference handling, provider boundaries, or redaction rules change;
- migration behavior begins writing source config.

Security closeout for Config publication must cover CLI output, diagnostics,
secret-reference redaction, direct-value blocking, local file reads, consumer
action decisions, and any new write or enforcement surface.
