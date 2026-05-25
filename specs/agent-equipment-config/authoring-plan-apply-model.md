# Authoring Plan/Apply Model: Agent Equipment Config

Status: Equipment Blueprint
Promotion state: planned

This Equipment Design Bundle document describes desired behavior for
non-migration Config authoring. It does not implement Agent Equipment, publish
assets, expose a general source patcher, resolve secrets, mutate external
systems, or implement harness controls. Current source mutation remains limited
to `migrate config apply` for registered migrations on eligible local TOML
sources.

## Purpose

Agent Equipment Config authoring changes policy that other Agent Equipment may
use before advisory behavior, mutation, publication, external calls, hook
execution, or workflow changes. The authoring model therefore makes proposed
changes, source targeting, authority, validation, refusal, and audit evidence
machine-visible before any non-migration Config write surface exists.

This model defines the shared contract for proposal, plan creation, and apply.
Command-specific implementation issues may later build CLI, runtime, docs, or
MCP surfaces against this contract.

## Operation roles

| Surface | Role | Write behavior |
| --- | --- | --- |
| `config propose` | Emits candidate changes, rationale, affected namespaces and fields, and possible target categories. | No source target is selected, and no source write is authorized. |
| `config patch` | Selects one eligible authored source and turns a candidate into a concrete `patch-layer` plan. | No source write occurs. The output is a reviewed plan artifact. |
| `create-layer` | Creates a plan for a new committed durable or local-only authored Config layer. | No source write occurs. The output is a reviewed plan artifact. |
| `config apply` | Applies a reviewed machine-readable plan artifact after final gates pass. | Writes only eligible authored sources, and only after precondition, authority, validation, and audit gates pass. |

Ad hoc flags such as `--set` may exist only as sugar that emits the same plan
artifact shape and stops before writing. The first model does not support
free-form mutation flags that bypass plan review.

## Plan artifacts

Authoring plan surfaces emit deterministic JSON by default. The caller owns
persistence unless a later command-specific implementation issue defines an
explicit storage surface. Plan artifacts are review records and apply inputs,
not durable project truth until an eligible apply action succeeds and its
evidence is classified.

Every authoring plan artifact includes:

| Field | Meaning |
| --- | --- |
| `schema` | Stable artifact schema identifier. |
| `plan_kind` | `patch-layer` or `create-layer`. |
| `source_target` | Source path or new-source destination selected by the plan surface. |
| `source_category` | Config source category for the target. |
| `source_identity` | Layer name, trusted provenance, and authority-relevant source metadata. |
| `precondition_fingerprint` | Fingerprint proving the reviewed source state that apply must recheck. |
| `change_payload` | Diff for `patch-layer`, or create payload for `create-layer`. |
| `authority_evidence` | Operator or configured Policy Authority evidence used by the plan. |
| `validation_result` | Schema and semantic validation outcome for the planned source shape. |
| `virtual_post_change_effective_config` | Effective Config status, diagnostics, and relevant provenance after applying the planned change in memory. |
| `audit_preview` | Durability, project-truth status, result expectation, refusal reasons, and rollback stance that apply will emit or refine. |
| `refusal_codes` | Stable refusal codes when the plan is not applyable. |
| `durability_classification` | Whether the artifact is project truth, local-only operator evidence, instance-scoped scratch, or review-only output. |

Plan artifacts are stable enough for tests and tools to parse without reading
human prose. Human-readable summaries may accompany the artifact, but they are
not the contract apply consumes.

## Source and authority boundary

The first authoring model writes only:

- `committed durable config`;
- `local-only operator config`.

The model may emit proposals or diagnostics for read-only categories, but it
does not write `checkout-local state`, `generated cache or state`,
`secret reference source`, `session override`, untrusted layers, or
external-owner contexts.

Writes require:

- trusted source provenance;
- an eligible source path or create destination;
- applicable Policy Authority or operator authority;
- schema and semantic validation success;
- usable virtual post-change effective Config for the requested behavior;
- a matching precondition fingerprint at apply time;
- an audit record that classifies durability, project-truth status, result,
  refusal reasons, and rollback stance.

## Secret-reference boundary

Authoring may create or patch secret-reference pointers when the target remains
an eligible authored Config layer. That allowance does not authorize writes to
a separate `secret reference source`. Authoring must refuse:

- secret values;
- secret-reference tables with embedded value payloads;
- provider credential material;
- provider configuration mutation;
- secret provider lookup, authentication, creation, rotation, or deletion.

Provider-specific secret behavior remains owned by the harness, tool, adapter,
or secret provider surface.

## Apply behavior

`config apply` accepts a plan artifact from a file or stdin. It does not accept
ad hoc source edits as its write contract.

Apply runs these gates in order:

1. Parse and validate the plan artifact schema.
2. Confirm the plan kind is implemented by the apply surface.
3. Re-read the selected source or create destination.
4. Verify the precondition fingerprint.
5. Recheck source category, trust, ownership, and authority.
6. Rebuild the virtual post-change effective Config.
7. Re-run schema, semantic, safety, and secret-boundary validation.
8. Refuse if any planned change fails.
9. Write atomically for local filesystem targets.
10. Emit mutation audit evidence with durability classification, project-truth
    status, result, and rollback stance.

Apply is all-or-nothing. If any source precondition, authority gate, schema
check, semantic validation, safety status, ownership boundary, or
secret-boundary check fails, no writes occur.

The first model does not define multi-source partial success. A later
implementation issue may define multi-source plans only if it preserves
all-or-nothing semantics or defines an explicit safe-continuation contract.

## Refusal codes

Authoring surfaces use stable refusal codes alongside readable detail:

- `unsupported_plan_kind`;
- `source_category_ineligible`;
- `source_untrusted`;
- `missing_authority`;
- `safety_status_blocking`;
- `validation_failed`;
- `secret_boundary_violation`;
- `ownership_boundary_violation`;
- `source_changed`;
- `partial_write_blocked`;
- `non_deterministic_plan`;
- `unsupported_mcp_authoring`.

The existing edit-boundary refusal states remain the shared vocabulary. New
command-specific issues may add narrower codes only when tests and docs explain
how tools route them.

## Issue Tracker Ops pressure scenario

Issue Tracker Ops is the first pressure consumer for this authoring model.

Scenario:

An Agent wants to move Issue Tracker Ops from advisory or dry-run behavior to
authorized live GitHub mutation. `config propose` suggests the policy fields
that would enable live mutation and names possible target categories. The
operator chooses an eligible committed or local-only authored Config layer.
`config patch` emits a `patch-layer` plan with the selected source, diff,
authority evidence, virtual post-change effective Config status, audit preview,
and refusal codes. `config apply` writes only if the source still matches the
reviewed precondition and the virtual post-change Config authorizes the live
mutation behavior.

Expected behavior:

- proposal output is target-agnostic;
- patch planning selects one eligible authored source;
- virtual post-change validation proves the consumer boundary before apply;
- missing authority, stale sources, unsafe Config, secret values, and ineligible
  source categories refuse before any write;
- apply emits audit evidence that distinguishes committed durable project
  truth from local-only operator state;
- Issue Tracker Ops still fails closed for live mutation when effective Config
  is blocking, unsupported, incomplete, unsafe, conflicted, stale, untrusted,
  or missing authority.

## MCP boundary

MCP authoring tools are later follow-up work. This issue defines the CLI and
runtime plan/apply contract and only records the likely MCP parity shape:

- `config.propose`;
- `config.patch`;
- `config.create_layer`;
- `config.apply`.

Those tools stay deferred until plan artifact schemas, side-effect classes,
auth source, approval requirements, failure modes, and mutation gates are
stable in the CLI/runtime contract.

## Follow-up slices

After this model lands, child issues should split implementation and validation
work by surface:

- proposal and plan-generation runtime behavior;
- apply runtime behavior for reviewed plan artifacts;
- CLI documentation and integration guidance;
- Issue Tracker Ops pressure validation;
- later MCP authoring parity after CLI/runtime behavior is stable.

Existing issues should be reused or updated when they already own one of these
slices.
