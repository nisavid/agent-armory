# MCP Tools: Agent Equipment Config

Status: Equipment Blueprint
Promotion state: planned

Agent Equipment Config exposes MCP parity for the safe read, onboarding,
migration-preview, and migration-apply CLI/runtime slice through typed tool
definitions and structured tool-call results. The CLI also exposes read-only
authoring proposal and plan-generation surfaces through `config propose`,
`config patch`, and `create-layer`; MCP authoring parity for those surfaces is
deferred. The importable runtime source is
`tools.agent_equipment_config.mcp_tool_definitions()` for tool metadata and
`tools.agent_equipment_config.call_mcp_tool()` for direct tool dispatch. A
harness-specific MCP server can wrap those functions without redefining Config
behavior.

This spec describes desired behavior and the current runtime boundary. It does not implement Agent Equipment.

## Tool definition contract

Each Config MCP tool definition includes:

- `name`, `title`, `description`, `inputSchema`, and `outputSchema`;
- MCP `annotations` for read-only, destructive, idempotent, and open-world
  hints;
- `x-agent-armory` metadata for CLI parity, read/write classification, auth
  source, side effects, approval requirements, mutation gate, and failure
  modes.

Tool-call results return an MCP-style object with text `content` and
`structuredContent`. The structured content contains the MCP operation name,
paired CLI operation, read/write classification, and the redacted runtime
result.
The direct dispatcher rejects arguments outside the published input schema and
requires every schema-required argument before invoking runtime behavior.

## Operation map

| CLI operation | MCP tool | Read/write classification |
| --- | --- | --- |
| `config resolve` | `config.resolve` | read-only |
| `config validate` | `config.validate` | read-only |
| `config diff` | `config.diff` | read-only |
| `onboard config` | `onboard.config` | read-only |
| `migrate config preview` | `migrate.config_preview` | read-only |
| `migrate config apply` | `migrate.config_apply` | local write |

All tools are closed-world local Config operations. They do not call networks,
resolve secret values, mutate external systems, or discover config paths. MCP
structured results use the same CLI redaction boundary for secret-reference
names and direct secret values.

`config propose`, `config patch`, and `create-layer` are current read-only CLI
surfaces, but they do not have MCP tool definitions in this slice.
`config apply` is a current CLI/runtime write surface for reviewed plan
artifacts. MCP authoring parity remains follow-up work.

Deferred MCP authoring parity must use these tool names when it is implemented:

| CLI operation | Deferred MCP tool | Read/write classification |
| --- | --- | --- |
| `config propose` | `config.propose` | read-only |
| `config patch` | `config.patch` | read-only policy decision |
| `create-layer` | `config.create_layer` | read-only policy decision |
| `config apply` | `config.apply` | local write |

## Shared inputs

Read operations that load Config accept:

- `layer_paths`: explicit authored TOML layer paths;
- `plain_handoff_paths`: explicit plain handoff TOML paths promoted as session
  overrides;
- `fragments`: schema fragments to register before validation;
- `requested_behavior`: `advisory` or `mutation`.

The current fragment registry exposes `issue_tracker_ops`. Arbitrary fragment
registration belongs to a later integration surface.

`config.diff` accepts typed `before` and `after` JSON objects rather than file
paths. The CLI fallback remains `config diff --before <file> --after <file>`
for command-line evidence comparison.

## Tool specs

### `config.resolve`

Purpose: resolve effective Config with values, provenance, diagnostics, safety
status, migration previews, plain-handoff promotion evidence, and enforcement
projection.

Classification: read-only. Auth source: none. Side effects: none. Approval
requirements: none.

Failure modes: input validation failure, config parse failure, schema conflict,
policy diagnostic, secret boundary violation.

### `config.validate`

Purpose: return lower-noise readiness evidence without full effective Config by
default. The report includes pass/fail status, Config Safety Status, authority
readiness, fragment readiness, diagnostics, and enforcement projection.

Classification: read-only. Auth source: none. Side effects: none. Approval
requirements: none.

Failure modes: input validation failure, config parse failure, blocking
validation, policy diagnostic, secret boundary violation.

### `config.diff`

Purpose: compare two effective Config objects and report value,
secret-reference identity, diagnostic, and safety-status changes.

Classification: read-only. Auth source: none. Side effects: none. Approval
requirements: none.

Failure modes: input validation failure, malformed effective Config input.

### `onboard.config`

Purpose: produce first-run, resume, restart, or revise planning output for
Config onboarding.

Classification: read-only. Auth source: none. Side effects: none. Approval
requirements: none.

Failure modes: input validation failure, config parse failure, unknown revise
section, policy diagnostic.

### `migrate.config_preview`

Purpose: preview registered migrations, refusals, projected effective Config,
and audit records without rewriting sources.

Classification: read-only. Auth source: none. Side effects: none. Approval
requirements: none.

Failure modes: input validation failure, config parse failure, migration
refusal, policy diagnostic.

### `migrate.config_apply`

Purpose: apply registered migrations to eligible local TOML sources and return
applications, refusals, write failures, projected effective Config, and audit
records.

Classification: local write. Auth source: per-call `apply_authority`. Side
effects: eligible local TOML source rewrite. Approval requirements: per-call
`apply_authority = "operator"`.

Mutation gate: eligible source category, trusted provenance, usable projected
Config, per-call apply authority, and final source precondition check.

Failure modes: input validation failure, config parse failure, missing
migration apply authority, ineligible source refusal, source precondition
failure, partial local write failure.

Rollback: restore the source file from version control or the recorded diff.

## Deferred authoring parity contract

MCP authoring parity is designed here but remains unimplemented. Runtime tool
definitions must not expose `config.propose`, `config.patch`,
`config.create_layer`, or `config.apply` until the implementation issue adds
the corresponding dispatcher behavior and validation coverage, and until
CLI/runtime authoring behavior is stable enough to treat as the source
contract. Until then, callers use the fluent CLI authoring workflow and MCP
wrappers return no authoring tool definition.

The deferred authoring tools mirror the current CLI/runtime authoring contract:

- plan-generation tools never write sources;
- every output is structured, redacted, and stable enough for machine routing;
- `config.patch` and `config.create_layer` emit reviewed plan artifacts with
  schema `agent-armory.config.authoring-plan.v1`;
- `config.apply` accepts only a reviewed plan artifact, not ad hoc source
  changes;
- apply rechecks precondition fingerprints, authority, source eligibility,
  trust, ownership, schema, semantic safety, secret boundaries, and the virtual
  post-change effective Config before writing;
- apply is all-or-nothing for every supported local filesystem target;
- mutation audit output classifies artifact durability, project-truth status,
  result, refusal reasons, and rollback stance;
- secret values, provider credential material, provider mutation, separate
  secret-reference source writes, generated/cache writes, checkout-local state
  writes, session override writes, untrusted layers, and unsupported source
  categories refuse before any source change.

All deferred authoring tools keep the current closed-world local boundary. They
do not call networks, discover config paths, resolve secrets, read provider
credential stores, mutate providers, or mutate external systems.

### Shared authoring input shapes

The MCP input schemas use typed JSON values instead of CLI `--set` strings.
Every authoring tool that accepts changes uses this shape:

```json
{
  "type": "object",
  "required": ["path", "value"],
  "properties": {
    "path": {
      "type": "string",
      "description": "Namespace-qualified Config field path such as issue_tracker_ops.mode."
    },
    "value": {
      "description": "JSON-compatible value to place at the Config field path."
    }
  },
  "additionalProperties": false
}
```

When a tool definition embeds the schemas below, this shape appears as
`$defs.authoringChange`.

`value` is schema-validated by the registered fragment. Null values, direct
secret values, secret-reference objects with embedded value payloads, and
nested provider-metadata edits refuse through stable refusal codes instead of
being normalized into a write.

Authoring inputs that load Config accept explicit `layer_paths` and
`fragments`. The current fragment registry exposes `issue_tracker_ops`; later
registries may add fragment names without changing the authoring control
contract. Plain handoffs remain session overrides and are not eligible write
targets.

### Shared authoring output shapes

Every deferred authoring tool-call result follows the existing MCP wrapper
shape:

```json
{
  "content": [
    {
      "type": "text",
      "text": "redacted human-readable summary"
    }
  ],
  "structuredContent": {
    "tool": "config.patch",
    "operation": "config.patch",
    "cli_operation": "config patch",
    "read_write_classification": "read-only policy decision",
    "result": {}
  }
}
```

`structuredContent.result` is the redacted runtime object that the paired CLI
would emit. Human-readable text is never the contract that apply consumes.

When a tool definition embeds the schemas below, the reviewed authoring plan
artifact appears as `$defs.authoringPlanArtifact`:

```json
{
  "type": "object",
  "required": [
    "schema",
    "operation",
    "plan_surface",
    "plan_kind",
    "source_target",
    "source_category",
    "source_identity",
    "precondition_fingerprint",
    "change_payload",
    "authority_evidence",
    "validation_result",
    "virtual_post_change_effective_config",
    "audit_preview",
    "refusal_codes",
    "durability_classification"
  ],
  "properties": {
    "schema": {"const": "agent-armory.config.authoring-plan.v1"},
    "operation": {"enum": ["config patch", "create-layer"]},
    "plan_surface": {"const": "reviewed-plan"},
    "plan_kind": {"enum": ["patch-layer", "create-layer"]},
    "source_target": {"type": "string"},
    "source_category": {"type": "string"},
    "source_identity": {"type": ["object", "null"]},
    "precondition_fingerprint": {"type": ["string", "null"]},
    "change_payload": {"type": "object"},
    "authority_evidence": {"type": "object"},
    "validation_result": {"type": "object"},
    "virtual_post_change_effective_config": {"type": "object"},
    "audit_preview": {"type": "object"},
    "refusal_codes": {"type": "array", "items": {"type": "string"}},
    "durability_classification": {"type": "string"},
    "rationale": {"type": "string"}
  },
  "additionalProperties": true
}
```

### `config.propose`

Purpose: produce target-agnostic candidate Config changes, rationale, affected
namespaces and fields, possible target categories, validation errors, and
refusal codes. It does not select a source target and does not authorize a
write.

Input schema:

```json
{
  "type": "object",
  "required": ["fragments", "changes"],
  "properties": {
    "fragments": {
      "type": "array",
      "items": {"type": "string"},
      "minItems": 1,
      "uniqueItems": true
    },
    "changes": {
      "type": "array",
      "items": {"$ref": "#/$defs/authoringChange"},
      "minItems": 1
    },
    "rationale": {"type": "string"}
  },
  "additionalProperties": false
}
```

Output schema:

```json
{
  "type": "object",
  "required": [
    "operation",
    "plan_surface",
    "source_target",
    "affected_namespaces",
    "affected_fields",
    "possible_target_categories",
    "candidates",
    "path_errors",
    "value_errors",
    "refusal_codes"
  ],
  "properties": {
    "operation": {"const": "config propose"},
    "plan_surface": {"const": "proposal"},
    "source_target": {"type": "null"},
    "affected_namespaces": {"type": "array", "items": {"type": "string"}},
    "affected_fields": {"type": "array", "items": {"type": "string"}},
    "possible_target_categories": {
      "type": "array",
      "items": {"enum": ["committed durable config", "local-only operator config"]}
    },
    "candidates": {"type": "array", "items": {"type": "object"}},
    "path_errors": {"type": "array", "items": {"type": "object"}},
    "value_errors": {"type": "array", "items": {"type": "object"}},
    "refusal_codes": {"type": "array", "items": {"type": "string"}}
  }
}
```

Classification: read-only. MCP annotations: `readOnlyHint = true`,
`openWorldHint = false`. Destructive and idempotent hints are unnecessary for
this read-only tool.
Auth source: none. Side effects: none. Approval requirements: none. Failure
modes: MCP input validation failure, unknown fragment, malformed change path,
unknown schema namespace or field, invalid value, non-deterministic duplicate
paths, direct secret value, provider credential material, or provider mutation
attempt.

### `config.patch`

Purpose: select one eligible existing authored source and turn reviewed changes
into a `patch-layer` plan artifact. It reads the selected source, records a
precondition fingerprint, validates the planned source shape, builds the
virtual post-change effective Config, and emits an audit preview. It writes no
source.

Input schema:

```json
{
  "type": "object",
  "required": ["layer_paths", "fragments", "source_target", "changes"],
  "properties": {
    "layer_paths": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    "fragments": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    "source_target": {"type": "string"},
    "changes": {
      "type": "array",
      "items": {"$ref": "#/$defs/authoringChange"},
      "minItems": 1
    },
    "plan_authority": {"enum": ["operator"]},
    "requested_behavior": {"enum": ["advisory", "mutation"], "default": "mutation"},
    "rationale": {"type": "string"}
  },
  "additionalProperties": false
}
```

Output schema:

```json
{
  "allOf": [
    {"$ref": "#/$defs/authoringPlanArtifact"},
    {
      "type": "object",
      "properties": {
        "operation": {"const": "config patch"},
        "plan_kind": {"const": "patch-layer"}
      }
    }
  ]
}
```

Classification: read-only policy decision. MCP annotations:
`readOnlyHint = true`, `openWorldHint = false`. Destructive and idempotent
hints are unnecessary for this read-only tool. Auth source: optional per-call
`plan_authority` or configured `config_authoring_plan` Policy Authority
evidence in the supplied layers. Side effects: local source reads only.
Approval requirements: no write approval; human or harness review is required
before the emitted plan is passed to `config.apply`. Failure modes: MCP input
validation failure, config parse failure, unknown fragment, target not present
in explicit `layer_paths`, ineligible source category, untrusted source,
missing plan authority, safety status blocking, planned-source validation
failure, secret-boundary violation, ownership-boundary violation,
non-deterministic duplicate paths, and unsupported source categories.

### `config.create_layer`

Purpose: create a reviewed `create-layer` plan artifact for a new eligible
authored Config layer. It verifies that the destination is an absent local
source target, builds the proposed layer payload, validates the planned source
shape, builds the virtual post-change effective Config, and emits an audit
preview. It writes no source.

Input schema:

```json
{
  "type": "object",
  "required": ["destination", "layer_name", "source_category", "fragments", "changes"],
  "properties": {
    "destination": {"type": "string"},
    "layer_name": {"type": "string"},
    "source_category": {"enum": ["committed durable config", "local-only operator config"]},
    "fragments": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    "changes": {
      "type": "array",
      "items": {"$ref": "#/$defs/authoringChange"},
      "minItems": 1
    },
    "layer_paths": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Existing explicit layers used only to build the virtual effective Config."
    },
    "plan_authority": {"enum": ["operator"]},
    "requested_behavior": {"enum": ["advisory", "mutation"], "default": "mutation"},
    "rationale": {"type": "string"}
  },
  "additionalProperties": false
}
```

Output schema:

```json
{
  "allOf": [
    {"$ref": "#/$defs/authoringPlanArtifact"},
    {
      "type": "object",
      "properties": {
        "operation": {"const": "create-layer"},
        "plan_kind": {"const": "create-layer"}
      }
    }
  ]
}
```

Classification: read-only policy decision. MCP annotations:
`readOnlyHint = true`, `openWorldHint = false`. Destructive and idempotent
hints are unnecessary for this read-only tool. Auth source: optional per-call
`plan_authority` or configured `config_authoring_plan` Policy Authority
evidence from supplied context layers. Side effects: local destination
existence check and optional explicit layer reads only. Approval requirements:
no write approval; human or harness review is required before the emitted plan
is passed to `config.apply`. Failure modes: MCP input validation failure,
destination already exists, unsupported destination category, unknown fragment,
malformed change path, missing plan authority, safety status blocking,
planned-source validation failure, secret-boundary violation, provider mutation
attempt, non-deterministic duplicate paths, and unsupported source categories.

### `config.apply`

Purpose: apply one reviewed `patch-layer` or `create-layer` authoring plan
artifact after all final gates pass. It is the only deferred MCP authoring tool
that writes Config sources.

Input schema:

```json
{
  "type": "object",
  "required": ["plan", "apply_authority"],
  "properties": {
    "plan": {
      "$ref": "#/$defs/authoringPlanArtifact",
      "description": "A reviewed agent-armory.config.authoring-plan.v1 artifact."
    },
    "apply_authority": {"enum": ["operator"]}
  },
  "additionalProperties": false
}
```

Output schema:

```json
{
  "type": "object",
  "required": [
    "operation",
    "plan_schema",
    "plan_kind",
    "source_target",
    "applied",
    "result",
    "refusal_codes",
    "audit_records"
  ],
  "properties": {
    "operation": {"const": "config apply"},
    "plan_schema": {"const": "agent-armory.config.authoring-plan.v1"},
    "plan_kind": {"enum": ["patch-layer", "create-layer"]},
    "source_target": {"type": "string"},
    "applied": {
      "type": "boolean",
      "description": "Must equal true when result is applied and false for every other result."
    },
    "result": {"enum": ["applied", "refused", "blocked", "write-failed"]},
    "refusal_codes": {"type": "array", "items": {"type": "string"}},
    "validation_result": {"type": "object"},
    "audit_records": {"type": "array", "items": {"type": "object"}}
  },
  "allOf": [
    {
      "if": {"properties": {"result": {"const": "applied"}}},
      "then": {"properties": {"applied": {"const": true}}}
    },
    {
      "if": {"properties": {"result": {"not": {"const": "applied"}}}},
      "then": {"properties": {"applied": {"const": false}}}
    }
  ]
}
```

Classification: local write. MCP annotations: `readOnlyHint = false`,
`destructiveHint = true`, `idempotentHint = false`, `openWorldHint = false`.
Auth source: per-call `apply_authority = "operator"`. Side effects: atomic
rewrite or creation of one eligible local TOML source when all gates pass.
Approval requirements: the MCP tool metadata must require explicit
operator/harness approval before the call because the call is mutation-capable.
Mutation gate: reviewed plan artifact schema, implemented plan kind, eligible
source category, trusted provenance, source ownership, per-call apply authority,
matching precondition fingerprint, valid planned source shape, usable virtual
post-change effective Config for the requested behavior, secret-boundary
validation, all-or-nothing refusal handling, atomic local write, and mutation
audit emission.

Failure modes: MCP input validation failure, malformed plan artifact,
`unsupported_plan_kind`, missing apply authority, source category ineligible,
source untrusted, ownership boundary violation, `source_changed`, safety status
blocking, validation failure, secret-boundary violation, provider mutation
attempt, `partial_write_blocked`, and local filesystem write failure. The
`unsupported_mcp_authoring` refusal code is a defensive transitional guard only
for a host or wrapper that reaches authoring dispatch before the authoring
feature flag is enabled. It does not authorize publishing these tool
definitions without dispatcher behavior and validation coverage.

Rollback: for committed durable config, revert the committed config change or
restore the recorded diff from version control. For local-only operator config,
restore the local operator file from the recorded diff or local backup. Refused
and blocked results require no rollback because no source write occurred.

## Fallback path

Agents should prefer MCP when a harness exposes these tools because the input
and output contracts are typed. Agents should fall back to the paired fluent CLI
operation when MCP is unavailable, when a human needs copyable commands, or
when command-line evidence comparison is clearer for review.
