# Vanilla Harness Capability Profile v1alpha1

Status: Forge Canon

This schema reference describes the first-slice Vanilla Harness Capability
Profile shape validated by `tools/harness_capability_profiles.py`. It is a
migration substrate, not the final Harness Capability Profile schema.

## Profile metadata

Each profile is a TOML file at
`docs/harness-capabilities/vanilla/<harness-id>.toml` with:

- `schema_version = "vanilla-harness-capability-profile.v1alpha1"`
- `profile_kind = "vanilla_harness_capability_profile"`
- `harness_id`
- `display_name`
- `checked_at`
- `checked_version`
- `version_basis`
- `evidence_category`
- `summary_scheduling`
- `scheduling`
- `limitations`
- `uncertainty`
- `refresh_notes`
- `components`
- `local_observations`

`[scope]` records `surface = "vanilla_harness_capability_surface"` and the
default installation and onboarding applicability statement.

## Evidence records

Each `[[evidence]]` record has a stable `id`, `category`, `source_kind`,
`url`, and `claim_scope`. Source URLs must be `http` or `https` URLs with a
host. Source kinds are `first_party` or `third_party_fallback`.

## Claim records

Each `[[claim]]` record has a stable per-profile `id`, `family`, `status`,
`statement`, `evidence_ids`, `applicability_scope`, `capability_origin`,
`migration_status`, `evidence_basis`, `limitations`, and `uncertainty`.

Supported claim statuses are `supported`, `unsupported`, `unknown`, and
`not-applicable`. Supported claims require evidence references. Every claim
needs limitations or uncertainty.

Every profile covers the standard surface-family rubric:

- `instructions_context`
- `skills`
- `mcp_tools`
- `hooks_events`
- `plugins_bundles`
- `agent_profiles_subagents`
- `memory_context_retrieval`
- `config_settings`
- `permissions_approvals_sandboxing`
- `scheduling_automation`
- `commands_shortcuts`
- `providers_connectors`
- `runtime_modes`
- `cross_harness_import_compatibility`
- `lifecycle_reload_update`

## Migration status

Migrated claims use `migration_status = "migrated_from_aggregate"` and
`evidence_basis = "aggregate_catalog_migration"` so later research and schema
pressure work can triage them without changing stable claim IDs.
