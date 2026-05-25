# Edit Boundaries: Agent Equipment Config

Status: Equipment Blueprint
Promotion state: planned

This Equipment Design Bundle document defines deliberate Agent Equipment Config
edit and mutation boundaries. It does not implement Agent Equipment. The current
implemented migrate surface is `migrate config preview` as dry-run output and
`migrate config apply` as the only mutating path. Broader edit surfaces must
follow this contract when later tools, MCP functions, skills, hooks, or guides
expose them.

## Purpose

Config edits change the policy that other Agent Equipment may rely on for
mutation-capable behavior. Every deliberate edit must therefore make intent,
authority, source ownership, validation, provenance, diff, and audit evidence
machine-visible before any source write.

## Edit intents

| Intent | Meaning | Write behavior |
| --- | --- | --- |
| `propose` | Produce a candidate config change, rationale, and diff without selecting a write target. | No source write. |
| `patch` | Change specific fields in one selected authored config source. | Deferred until an approved surface implements source selection, validation, authority, diff, and audit. |
| `migrate` | Translate stale schema metadata through a registered migration. | Current runtime supports dry-run preview and eligible source apply through `migrate config preview` and `migrate config apply`. |
| `revise` | Re-open selected equipment namespaces for onboarding or re-onboarding while preserving unselected sections. | Current runtime reports a revision plan through `onboard config`; source writing is deferred. |
| `apply` | Write a previously reviewed plan to an eligible source after explicit authority and final precondition checks. | Current runtime applies only registered migrations to eligible TOML sources. |

An edit surface may also inspect, explain, trace, compare, or validate Config,
but those read-only operations do not authorize source mutation.

## Source ownership

| Source category or context | Edit stance | Write owner |
| --- | --- | --- |
| `committed durable config` | Writable only through a deliberate Config write surface with authority, diff, validation, audit, and rollback evidence. | Project or repository policy owner. |
| `local-only operator config` | Writable only through a deliberate local write surface with operator authority, diff, validation, audit, and local artifact classification. | Local operator. |
| `checkout-local state` | Read-only to Config edit surfaces. A proposal may identify stale state, but the owning checkout or tool regenerates or changes it. | Owning checkout or tool. |
| `generated cache or state` | Read-only to Config edit surfaces. A proposal may ask the generator to refresh it. | Generator. |
| `secret reference source` | Read-only metadata. Config may propose or patch secret-reference pointers in eligible authored config, but it must not write secret values or mutate the secret provider. | Secret provider or harness. |
| `session override` | Session-scoped and read-only for durable source writes. A session may accept a new plain handoff or override value, but Config must not persist it as project truth without a separate eligible target. | Current session or handoff owner. |
| External owner context, not a v0 `agent_equipment_config.layer.category` value | Read-only unless the owner exposes a Config-aware write surface with its own authority and audit contract. | External owner. |

The source category is not enough by itself. A write also needs trusted
provenance, an eligible source path, applicable Policy Authority, and a clean
effective-config result for the requested behavior.

## Required mutation controls

Every Config source-write surface must:

- default to dry-run or proposal output;
- require an explicit edit intent and selected source target before writing;
- emit a reviewable diff or change set before writing;
- preserve source category, path, layer name, trust, and authority provenance;
- validate schema, semantic rules, Policy Authority, and Config Safety Status;
- refuse writes that cross source ownership, secret, authority, validation, or
  harness-support boundaries;
- verify that the source still matches the reviewed precondition before writing;
- write atomically when the local filesystem is the target;
- emit audit records that classify artifact durability, project-truth status,
  authority, decision, result, rollback stance, and any refusal reason;
- avoid external system mutation unless the consuming equipment owns and audits
  that external write separately.

## Edit decision states

| State | Required meaning |
| --- | --- |
| `dry-run` | The output describes a candidate write and audit preview; no source changed. |
| `authorized` | The requested write passed intent, authority, source, and validation gates and is ready for the final precondition check. |
| `applied` | The write completed and mutation audit evidence exists. |
| `refused` | A candidate write violated a gate; no write for that candidate is authorized. |
| `blocked` | The apply request contained at least one refusal or unsafe condition, so staged writes did not run. |
| `write-failed` | A final precondition or filesystem write failed after authorization. |
| `deferred` | The intent is valid for the Config contract but has no implemented write surface yet. |

## Refusal states

Config edit surfaces must use stable refusal reasons that future tools can
route without parsing prose. The current contract includes:

- `unsupported_intent`: the requested edit intent has no implemented surface;
- `source_category_ineligible`: the selected source category is read-only for
  this write;
- `source_untrusted`: the source is visible for diagnostics but cannot
  authorize mutation;
- `missing_authority`: no applicable operator or configured Policy Authority is
  usable for the selected write;
- `safety_status_blocking`: effective Config is incomplete, unsafe, stale,
  untrusted, conflicted, or otherwise not usable for the write;
- `validation_failed`: schema or semantic validation rejects the proposed
  source shape;
- `secret_boundary_violation`: the edit would write a secret value, weaken
  secret handling, or mutate a secret provider;
- `ownership_boundary_violation`: the selected surface does not own the target
  source;
- `source_changed`: the source changed after the reviewed plan was produced;
- `partial_write_blocked`: at least one candidate in an apply request refused,
  so no partial apply may proceed.

The non-migration authoring plan/apply model adds narrower plan-artifact
refusals for `unsupported_plan_kind`, `non_deterministic_plan`, and
`unsupported_mcp_authoring`. Those codes preserve the same refusal contract:
tools route stable codes, while humans receive readable detail.

Existing runtime output may render these as human-readable `reason` strings.
New edit surfaces should expose the stable reason code alongside the readable
detail.

## Current runtime reconciliation

`migrate config apply` is the only current source mutation surface. It supports:

- `migrate config preview` as dry-run output with exact changes and audit records;
- `apply` for registered migrations on `committed durable config` and
  `local-only operator config`;
- operator authority through `--apply-authority operator`;
- trusted configured authority through `config_migration_apply = "usable"`;
- refusals for untrusted, ineligible, unsafe, incomplete, stale-without-
  migration, missing-authority, and changed-source cases;
- blocked partial apply when any candidate refuses.

`onboard config --revise-section` implements revision planning. It selects the
sections to revisit and marks unselected sections for preservation. It does not
write source config.

`propose` and `patch` are contract intents for the deferred Config Authoring
Surfaces bucket. The authoring plan/apply model specifies `config propose`,
`config patch`, `create-layer`, reviewed plan artifacts, precondition
fingerprint checks, virtual post-change effective Config validation,
all-or-nothing apply, durability classification, and rollback stance. Until a
child implementation issue implements that model, Config-aware equipment may
emit proposals or diffs but must not perform general source patches.

Issue [#78](https://github.com/nisavid/agent-armory/issues/78) owns published
integration guidance for the settled MVP operation surface. General source
authoring guidance follows the deferred Config Authoring Surfaces bucket.

## Examples

Allowed current write path:

1. A trusted `committed durable config` layer has stale schema metadata for a
   namespace with a registered migration.
2. `migrate config preview` reports exact field renames, fragment-version
   updates, source category, write target, and audit records.
3. The operator runs `migrate config apply --apply-authority operator`.
4. The source still matches the reviewed precondition.
5. The runtime writes the TOML atomically and emits `applied` mutation audit
   evidence.

Refused current write path:

1. A `generated cache or state`, `checkout-local state`, `session override`, or
   `secret reference source` layer has stale schema metadata.
2. The operator requests `migrate config apply`.
3. The runtime refuses the candidate because the source category is not eligible
   for migration apply.
4. No source write occurs, and the refusal audit record names the source,
   category, namespace, authority evidence, and reason.
