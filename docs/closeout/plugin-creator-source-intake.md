# Plugin-Creator Source Intake

Status: Source Disposition Ledger

## Scope Boundary

This ledger captures reusable plugin-creation source knowledge from the Codex
`plugin-creator` source family for issue #85. It is source-disposition evidence
for downstream Armory work. It does not create, install, publish, or validate an
Armory plugin, and it does not decide a final Armory plugin manifest,
marketplace, inventory, delivery, ingestion, or evaluation architecture.

Accepted claims in this ledger are design input for plugin-dependent work.
Codex-specific manifest fields, marketplace behavior, cache refresh steps, UI
metadata, and validation rules remain harness-specific evidence until a
downstream issue accepts them through its own interface decision, validation,
security, and delivery gates.

## Portable Source Inventory

| source_id | source identity | source family | retained use |
| --- | --- | --- | --- |
| PC001 | `plugin-creator/SKILL.md` | scaffold workflow | Plugin creation sequence, personal versus repo marketplace boundary, required behavior, validation command, update flow routing, deeplink handoff, and operator-approval boundary. |
| PC002 | `plugin-creator/scripts/create_basic_plugin.py` | scaffold workflow | Name normalization, manifest scaffolding, optional component surface selection, marketplace projection, deterministic JSON output, force behavior, and policy/auth semantics. |
| PC003 | `plugin-creator/scripts/validate_plugin.py` | schema validation | Manifest schema validation, companion file checks, skill metadata validation, app and MCP checks, asset path validation, URL and semver validation, unsupported-field rejection, and placeholder debt rejection. |
| PC004 | `plugin-creator/scripts/update_plugin_cachebuster.py` | update workflow | Cachebuster reinstall flow that preserves the version prefix and rewrites a single Codex metadata suffix for local plugin iteration. |
| PC005 | `plugin-creator/scripts/read_marketplace_name.py` | update workflow | Marketplace-name discovery from a marketplace file without requiring manual marketplace JSON edits during reinstall. |
| PC006 | `plugin-creator/references/plugin-json-spec.md` | manifest and marketplace reference | Field-level plugin manifest, interface metadata, default prompt, asset metadata, marketplace entry, install policy, authentication policy, product-gating, and validation conventions. |
| PC007 | `plugin-creator/references/installing-and-updating.md` | update workflow | Local update flow, personal marketplace discovery, non-default marketplace checks, reinstall command shape, and new-thread pickup boundary after reinstall. |
| PC008 | `plugin-creator/agents/openai.yaml` | UX metadata | Display name, short description, default prompt, and icon references used to present the skill-like plugin creation flow. |
| PC009 | `plugin-creator/assets/plugin-creator.png` and `plugin-creator/assets/plugin-creator-small.svg` | UX assets | Source evidence that plugin-shaped equipment can include presentation assets, with asset existence and relative-path checks as part of publish readiness. |

## Reusable Techniques

| technique | retained method | evidence class | limits and side effects |
| --- | --- | --- | --- |
| manifest scaffolding | Create a required plugin manifest first, populate the full accepted schema shape with safe defaults, and add component references only when companion files exist. | Source-supported technique from PC001, PC002, PC003, and PC006. | Codex uses `.codex-plugin/plugin.json`; Armory Harness Plugin templates currently use TOML. The reusable lesson is schema-first scaffolding, not Codex JSON as the universal manifest. |
| name normalization | Normalize plugin identifiers to lower-case hyphen-case, collapse duplicate separators, reject empty identifiers, enforce a length limit, and keep folder and manifest names aligned. | Source-supported technique from PC001 and PC002. | The exact 64-character limit is Codex source evidence, not an accepted Armory-wide identifier limit. |
| component surface selection | Create optional `skills`, `hooks`, `scripts`, `assets`, MCP, and app surfaces only when requested, and keep manifest references synchronized with created companions. | Source-supported technique from PC001, PC002, PC003, and PC006. | The Codex component list overlaps with Armory Harness Components but does not cover every future component type or package shape. |
| marketplace projection | Treat marketplace visibility as separate from plugin creation. Preserve marketplace display metadata, append entries by default, require force for replacement, and keep source paths relative to the marketplace root. | Source-supported technique from PC001, PC002, PC006, and PC007. | Codex personal marketplace discovery and marketplace JSON shape are harness-specific. Generic Armory inventory and shop-card surfaces belong to delivery-system work. |
| policy/auth semantics | Always represent install and authentication timing policy on marketplace entries; treat product gating as an explicit override instead of a silent default. | Source-supported technique from PC001, PC002, and PC006. | The allowed values `AVAILABLE`, `INSTALLED_BY_DEFAULT`, `NOT_AVAILABLE`, `ON_INSTALL`, and `ON_USE` are Codex-specific source material until accepted by delivery or inventory policy. |
| schema validation | Validate manifests, companion files, skill metadata, semver, URLs, assets, accepted fields, and component path conventions before treating the scaffold as hand-back ready. | Source-supported technique from PC001, PC003, and PC006. | The source validator depends on Codex's current ingestion contract and `yaml` library availability; Armory validators should use repo-accepted dependencies and schemas. |
| placeholder debt | Reject unresolved placeholder markers in plugin manifests and keep unknown publisher, legal, UX, policy, or asset decisions as explicit completion debt rather than pretending the scaffold has final publish metadata. | Source-supported technique from PC001, PC003, and PC006. | Placeholder policy needs downstream delivery-system alignment before it becomes a generic publication gate. |
| cachebuster reinstall flow | Preserve the semantic version prefix and rewrite one Codex cachebuster suffix for local iteration, then reinstall from the selected marketplace and start a new thread for pickup. | Source-supported technique from PC004 and PC007. | This is local Codex iteration behavior. It should not become a generic versioning model for published equipment. |
| source-specific helper routing | Use helper scripts for deterministic marketplace name reads and cachebuster edits instead of manual JSON edits during local update flows. | Source-supported technique from PC004, PC005, and PC007. | The helper commands perform local reads or writes and need side-effect classification before use in repo-owned equipment. |

## UX And Marketplace Metadata

Impeccable review result: the durable UX lesson is metadata discipline, not a
frontend implementation. Plugin-shaped equipment should carry enough
presentation metadata for a Wielder or Outfitter to choose it without reading
implementation files, while keeping publishing claims tied to current validated
surfaces.

Retained UX and marketplace lessons:

- `displayName`, short and long descriptions, developer name, category,
  capabilities, starter prompts, brand color, composer icon, logo, and
  screenshots are presentation data, not proof of implementation readiness.
- Starter prompts should be short, few, and task-shaped so they reduce choice
  friction without replacing real documentation or validation.
- Marketplace ordering is a presentation decision. Automated intake should not
  reorder entries unless an accepted policy or explicit request owns that
  change.
- Asset metadata must resolve to real bundled files before publish readiness is
  claimed. Asset paths should stay relative to the package boundary.
- Install/auth policy and product gating are UX-affecting control surfaces.
  They need delivery and security review when projected into Armory inventory,
  shop cards, plugins, or gear-up paths.

## Downstream Routing

| route | accepted input from this ledger | not owned here |
| --- | --- | --- |
| #5 | Equipment ingestion and promotion should consume the distinction between source intake, plugin creation, marketplace projection, schema validation, placeholder debt, source provenance, and update-channel handling. | The full ingestion and promotion pipeline design, operator choice points, licensing policy, update-channel strategy, and bulk migration workflow. |
| #154 | The Agent Equipment Config Codex plugin should consume the Codex-specific scaffold, manifest, marketplace, component-reference, validation, UX metadata, policy/auth, and cachebuster lessons before repo-owned plugin implementation. | The Config plugin source tree, manifest, build/install instructions, repo-local package checks, local install dogfood, MCP exposure, and Config-specific security closeout. |
| #157 | Delivery-system alignment should consume this ledger only for plugin-dependent delivery slices, especially the boundary between plugin source intake, shop cards, inventory, ITP, delivery compliance, and marketplace-like presentation. | The Published Equipment Delivery alignment decision, follow-up issue projection, or dependency cleanup beyond the source-intake evidence from #85. |
| #16 | Conditional consumer only if issue lifecycle work reaches skill, Agent Profile, or future plugin projection and needs plugin-shaped pressure cases. | Issue Tracker Ops enrichment/orchestration implementation. |
| #61 | Conditional consumer only if Agent Test Jigs designs plugin installability, component exposure, asset resolution, policy/auth behavior, or publish-readiness scenarios. | Jig runner, driver, assertion-provider, and result-schema architecture. |
| later Forge work | Later Forge work can decide whether plugin-creator lessons become templates, examples, specs, validators, delivery gates, or equipment-specific closeout checks. | A final Armory plugin manifest abstraction, remote marketplace model, or package manager. |

## Deferments And Nonportable Claims

- Codex's `.codex-plugin/plugin.json` path is retained as source evidence, not
  as the generic Armory plugin manifest path.
- Codex marketplace JSON, personal marketplace discovery, deeplinks, reinstall
  commands, cachebuster suffixes, and new-thread pickup behavior are retained as
  Codex-specific local iteration behavior.
- The source validator's accepted and rejected manifest fields are retained as
  current source evidence. They do not prove future Codex compatibility and do
  not override Armory Harness Plugin templates.
- The exact scaffold defaults for category, author, prompt text, install
  policy, authentication policy, and version are examples from the source
  workflow, not Armory publication defaults.
- Raw local source paths, generated plugin scaffolds, marketplace files,
  command output, local install state, and screenshots are instance-scoped
  scratch unless a downstream issue promotes sanitized evidence.
- No local plugin creation, Codex installation, marketplace mutation, or
  package smoke is accepted by this issue.

## Security, Privacy, And Durability

The source material describes local filesystem writes, marketplace JSON writes,
local plugin reinstall commands, MCP/app component references, skill metadata,
asset loading, external URLs, policy/auth metadata, and deeplinks. Downstream
executable or package work must model those as file, process, disclosure,
network, install, and user-visible state boundaries before using them as
automation.

Durable project evidence for #85 consists of this ledger, the PR diff,
deterministic validation output, security closeout, documentation closeout, and
issue projection. Portable review summaries may name the source identities
above and the conclusions retained here. Instance-scoped scratch includes raw
home-directory paths, local marketplace files, generated plugin trees, copied
asset files, command stdout/stderr, local app install state, deeplink execution,
and local validation work directories.

Privacy boundaries:

- Do not preserve user workstation paths, personal marketplace contents,
  installed plugin state, auth state, local app state, or local command
  environment in durable project docs.
- Do not publish generated plugin manifests or marketplace entries as project
  truth unless a downstream story accepts a sanitized fixture or repo-owned
  plugin source tree.
- Do not treat presentation metadata as publishable until the linked equipment,
  component paths, assets, policy, and support claims pass the relevant
  delivery checks.

## Closeout Evidence

Grill-with-docs result: existing Armory vocabulary is sufficient. The correct
durable surface is this Source Disposition Ledger under `docs/closeout/`.
No new glossary term or ADR is needed for #85.

Impeccable review-method pass: accepted UX lessons are marketplace and
interface metadata discipline, short task-shaped starter prompts, relative
asset paths, presentation ordering as an explicit decision, and no custom UI
implementation in this issue.

TDD result: Armory Integrity Validation owns a structural guard for this
ledger: status, required sections, required technique coverage, downstream
issue routes, and host-local path rejection.

Security closeout: the change set adds a read-only validator check and a
portable ledger. The validator reads one repository-relative Markdown path
through existing path-status checks, performs text and exact-route validation,
and rejects host-local paths. It introduces no writes, subprocess execution,
network calls, secret handling, or untrusted path inputs.

Documentation closeout: this ledger is the committed documentation change for
issue #85. The repository documentation map remains reader-oriented and does
not list issue-specific closeout ledgers; downstream issue routing is captured
in the ledger and issue projection rather than duplicated into the docs map.

Ralph review closeout: documentation closeout, Cross-Boundary Coherence, and
Story Quality review cycles are clean after the routing precision and
host-local path checks.
