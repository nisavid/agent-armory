# The Agent Armory documentation

This map helps human readers choose what to read and what to give to their
agents. The Agent Armory is under construction: the Forge has just come online,
and Agent Equipment Config has its first published runtime slice.

## Choose a path

- **Wielding a loadout**: start with the [Armory Vision](vision.md), then the
  [Forge Tour](forge-tour.md). For shared equipment configuration, use
  [Agent Equipment Config](equipment/agent-equipment-config.md) and the
  [Config integration guide](equipment/agent-equipment-config-integration.md).
  Check the [stocked-equipment inventory](equipment/inventory.md) before
  treating any surface as current Armory stock.
- **Outfitting a harness**: ask an outfitter to compare
  [harness capabilities](harness-capabilities.md),
  [harness components](harness-components.md), and
  [security and control](security-and-control.md) against the
  [Armory Vision](vision.md) before selecting a future loadout.
- **Evaluating the Armory**: start with the [Armory Vision](vision.md) and the
  [Forge Tour](forge-tour.md), then use the
  [Forge Canon](agent-equipment-forge.md) and current [roadmap](#roadmap) to see
  what exists now, how equipment is made, and what is planned.
- **Procuring equipment**: check the current
  [stocked-equipment inventory](equipment/inventory.md), then review
  [equipment promotion](equipment-promotion.md) and
  [Published Equipment Delivery](equipment-delivery.md) to see what must be
  true before equipment is ready to use.
- **Commissioning new equipment**: have a smith start with the
  [Armory Vision](vision.md), [smith runbook](smith-runbook.md),
  [interface decision guide](interface-decision-guide.md), and
  [templates](../templates/).
- **Keeping equipment current**: ask the responsible agent to compare the
  [Armory Vision](vision.md),
  [harness capabilities](harness-capabilities.md),
  [security and control](security-and-control.md), and
  [equipment promotion](equipment-promotion.md).

## Start here

- [Armory Vision](vision.md): Efficient Coherence and the intended agent and
  operator experience behind the Armory, the Forge, and Agent Equipment.
- [Forge Tour](forge-tour.md): human-facing orientation to the Armory, the Forge,
  agent roles, and current construction state.
- [Forge Canon](agent-equipment-forge.md): core method for the Forge and component
  model.
- [Project context and language](../CONTEXT.md): glossary, relationships,
  precision rules, example dialogue, and ambiguity resolutions.

## Tutorials and guided examples

- [PR review example](../examples/pr-review/projected-components.md): how a PR
  review capability projects into equipment surfaces.
- [Documentation research example](../examples/docs-research/projected-components.md):
  how a documentation research capability handles evidence-backed claims.
- [Observability investigation example](../examples/observability-investigation/projected-components.md):
  how an investigation capability combines judgment, tools, docs, and checks.

These examples are teaching artifacts. They are not installable or published
agent equipment.

## Guides to hand to agents

- [Smith runbook](smith-runbook.md): give this to a smith when you want new or
  revised agent equipment.
- [Interface decision guide](interface-decision-guide.md): choose the right
  place for each equipment responsibility.
- [Equipment promotion](equipment-promotion.md): see how close an example,
  blueprint, or candidate is to being ready for inventory.
- [Published Equipment Delivery](equipment-delivery.md): use when a stockable
  release needs a shop card, stock record, component manifest, and delivery
  compliance status.
- [Work closeout](story-closeout.md): use when an agent needs to finish work
  cleanly, with checks, safeguards, docs, and review aligned.
- [External tool evaluation](external-tool-evaluation.md): use when an outside
  tool, framework, harness, service, dataset, or adjacent project may influence
  Armory architecture, issue projection, documentation, security posture, or
  adoption decisions.

## Reference

- [Harness components](harness-components.md): where skills, MCP/tools, hooks,
  agent profiles, plugins, scripts, docs, and config fit.
- [Harness capabilities](harness-capabilities.md): evidence-backed Vanilla
  Harness Capability Profiles for supported agent harnesses.
- [Evidence taxonomy](evidence-taxonomy.md): how the Forge labels claims and
  decides what can be trusted.
- [Security and control](security-and-control.md): what equipment may do, what
  needs approval, and where secrets and side effects are controlled.
- [External tool evaluation](external-tool-evaluation.md): reusable operating
  contract for source review, evidence classification, security disclosure,
  projection, and final disposition of outside tools.
- [Security Best Practices Baseline](security/security-best-practices.md):
  current secure defaults for executable repository surfaces.
- [Templates](../templates/): starting points an agent can copy while making
  future equipment.
- [Agent Equipment Config](equipment/agent-equipment-config.md): published
  runtime slice with fluent CLI operations and MCP parity tools for shared
  Config.
- [Config integration guide](equipment/agent-equipment-config-integration.md):
  how Smiths, Wielders, and Outfitters connect equipment to shared Config.
- [Stocked equipment inventory](equipment/inventory.md): human-facing view of
  current stock, backed by `inventory/equipment.toml`.
- [Published Equipment Delivery](equipment-delivery.md): stock inventory and
  shop-card standard for delivery-compliant equipment claims.

## Explanation

- [Armory Vision](vision.md): Efficient Coherence and the experience,
  architecture, strategy, design, validation, and maintenance north star for the
  Armory.
- [Forge Canon](agent-equipment-forge.md): the deeper explanation of how the
  Forge turns ideas into trustworthy equipment.
- [Forgewright runbook](forgewright-runbook.md): give this to an agent when the
  Forge itself needs improvement.
- [Repository threat model](security/threat-model.md): risks, boundaries, and
  control assumptions for people evaluating trust.
- [Security Best Practices Baseline](security/security-best-practices.md):
  durable conclusions from the current executable-surface security refresh.
- [Agent Equipment Config PRD](prd/agent-equipment-config.md): product
  requirements for shared Config, including CLI and MCP operation surfaces.
- [Published Equipment Delivery System PRD](prd/published-equipment-delivery.md):
  draft delivery standard for shop cards, inventory, storefronts, Equipment
  ITP, closeout gates, and the Config delivery retrofit.
- [Design decisions](adr/): the decision records behind durable choices in the
  Forge.
- [Agentic Engineering Operating Model Review](reviews/agentic-engineering-operating-model.md):
  current review of cross-Armory operating contracts, validation boundaries,
  and manual Harness Capability Profile refresh certification.

## Roadmap

The current roadmap points to equipment lines that still have future slices:

- [Agent Equipment Config](../specs/agent-equipment-config/): shared,
  layerable, enforceable configuration across equipment; the
  [runtime slice](equipment/agent-equipment-config.md) is published, and the
  [integration guide](equipment/agent-equipment-config-integration.md) and
  [PRD](prd/agent-equipment-config.md) record the current user path and
  required CLI and MCP operation surfaces.
- [Issue Tracker Ops](../specs/issue-tracker-ops/): direct GitHub
  Issues baseline operations and future issue lifecycle equipment. Issue Ops
  is the accepted shorthand.
- [Existing Equipment Onboarding](prd/existing-equipment-onboarding.md): draft
  generic contract for discovering prior equipment, deciding compatibility and
  disposition, and reporting activation limits before an equipment line claims
  coverage.
- [Repo Ops](../specs/repo-ops.md): repository framework for agentic
  operations. Repo Ops is complete for repositories that are not forks.
- [Fork Ops](https://github.com/nisavid/agent-armory/issues/87): planned
  Repo Ops add-on for fork-specific operations after Fork Ops source material
  and Repo Ops prerequisites are ready for intake.
- [Periodic Actions](../specs/periodic-actions.md): recurring agent actions
  across harnesses.
- [Vanilla Harness Capability Profiles](../specs/vanilla-harness-capability-profiles/):
  source-backed descriptions of supported harness integration surfaces, with
  manual profile validation and refresh tooling. The recurring refresh path
  remains future work.
- [Capability Profiling Protocol](../specs/capability-profiling-protocol/):
  reusable study-plan, study-report, and jig-adequacy structure for Capability
  Surface studies.
- [Agent Test Jigs and Harness Testing System](../specs/agent-test-jigs/):
  design package for controlled harness, equipment, Loadout, interaction, and
  Harness Capability validation. Implementation remains projected to follow-up
  issues.
- [Head Gear / Reflection and cognition equipment](https://github.com/nisavid/agent-armory/issues/25):
  future generic cognition enhancement equipment that turns underspecified
  intent and recent agent experience into durable insight, routed follow-up, and
  harness improvements.
- [Portable workflow equipment](https://github.com/nisavid/agent-armory/issues/8):
  future support for portable agent equipment.
- [Side-thread hand-back](https://github.com/nisavid/agent-armory/issues/7):
  future support for side conversations around active work.
- [Ephemeral workflow opportunity capture](https://github.com/nisavid/agent-armory/issues/9):
  future support for capturing useful workflow ideas during active sessions.

The GitHub issue tracker carries active story structure. The projected Forge
Seed follow-up captures are retired in
[Forge Seed Follow-Up Projection](closeout/forge-seed-follow-up-projection.md).
