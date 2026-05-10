# Vanilla Harness Capability Profile v1alpha1

Status: Forge Canon

This schema reference describes the Vanilla Harness Capability Profile shape
validated by `tools/harness_capability_profiles.py`. The schema preserves the
first migrated claim IDs and adds the accepted issue #45 enrichment fields. It
is still not the final Harness Capability Profile schema.

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
host. Source kinds are `first_party` or `third_party_fallback`. The Manager
Core derives the evidence ID from the source URL and claim scope.

## Version observations

Each `[[version_observation]]` record has `id`, `observed_version`,
`checked_at`, `source_url`, `source_kind`, `canonical_profile_change`, and
`evidence_class`.

Version observations let a profile record current release or changelog state
without changing stable claim IDs. `canonical_profile_change` is true when the
observation is part of the current canonical profile refresh.

## Harness extensions

Each `[[harness_extension]]` record has `id`, `name`, `scope`,
`description`, `evidence_ids`, `evidence_class`, and `schema_pressure_ids`.

Harness extensions describe harness-specific integration surfaces such as
compatible bundles, plugin sharing metadata, active memory controls, or
runner-locus distinctions. They do not prescribe downstream Forge behavior or
recommended Equipment choices.

## Claim records

Each `[[claim]]` record has a stable per-profile `id`, `family`, `status`,
`statement`, `evidence_ids`, `applicability_scope`, `capability_origin`,
`migration_status`, `evidence_basis`, `limitations`, and `uncertainty`.
Refreshed claims also have `claim_triage`, `triage_rationale`,
`install_activation`, `configuration_surface`, and
`reload_update_behavior`.

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

Optional nested claim tables record accepted issue #45 enrichment fields:

- `[[claim.detail]]` records `component`, `load_attachment_point`,
  `activation`, `mutability`, `scope`, `evidence_ids`, and
  `evidence_class`.
- `[[claim.memory_like_surface]]` records `persistence_scope`,
  `retrieval_trigger`, `mutability`, `freshness`, `privacy_boundary`,
  `write_authority`, `api_stability`, `evidence_ids`, and
  `evidence_class`.
- `[[claim.automation_surface]]` records `trigger_class`, `runner_locus`,
  `recurrence_shape`, `permission_sandbox_context`,
  `missed_run_behavior`, `output_delivery`, `evidence_ids`, and
  `evidence_class`.
- `[[claim.compatibility_bridge]]` records `imported_from`,
  `imported_convention`, `surviving_components`, `activation`,
  `disable_behavior`, `precedence`, `fidelity_limits`, `evidence_ids`, and
  `evidence_class`.

## Migration status

Migrated-only claims use `migration_status = "migrated_from_aggregate"` and
`evidence_basis = "aggregate_catalog_migration"`. Refreshed claims keep their
stable claim IDs and use a controlled migration status such as
`refreshed_from_migrated_claim` with an evidence basis such as
`current_first_party_source` or `explicit_unknown`.

## Research outputs

Issue #44 adds adjacent research artifacts under
`specs/vanilla-harness-capability-profiles/`:

- one research note per supported harness under `research-notes/`;
- `schema-pressure-report.md`.

These artifacts are validated by the Manager Core for structure, source
traceability, required surface-family coverage, and schema-pressure finding
shape. Issue #45 applies the accepted enrichment findings to the canonical
profiles while keeping unresolved schema pressure explicit.
