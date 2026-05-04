# Portable Agentic Engineering Workflow Equipment

Status: Follow-Up Capture

## Purpose

Design a generic, reusable ingestion and promotion flow for portable Agent
Equipment. The first motivating import source is the operator's current
user-global equipment, but the flow must work for any repo, harness, or
equipment kind.

## Captured Requirements

- Ingest the [Engineering Workflow Generalization Addendum](../closeout/forge-seed-engineering-workflow-generalization.md)
  alongside the original workflow lessons.
- Start with a grill-with-docs session that resolves ingestion ambiguities and
  records ADRs before bulk import.
- Treat source materials as directional evidence of intended capability, not as
  authoritative final equipment design.
- Inspect the full source set plus existing equipment before item-level import.
  Catalog overlap, containment, conflict, integration opportunities, plugin
  bundles, and group-level import candidates before planning each item.
- Support skills, plugins, Agent Profiles, MCP/tool definitions, scripts,
  workflows, policy frameworks, and other equipment types.
- Classify each candidate as example, candidate, internal repo workflow,
  publishable equipment, bundle member, wrapper/extension, rejected source, or
  deferred design input.
- Preserve source, provenance, and licensing context.
- Identify global-installation assumptions and remove accidental dependency on
  the operator's user-global state.
- Provide an interactive or configurable UX so the operator can choose import
  policy at source, group, function, or facet granularity.
- Account for externally maintained sources by supporting ingest-as-is, drop,
  wrapper, extension, adaptation layer, local policy overlay, and upstream-update
  preservation strategies.

## GitHub Issue Projection

Projected follow-up issues:

- [#5](https://github.com/nisavid/agent-armory/issues/5): Design equipment
  ingestion and promotion pipeline.
- [#8](https://github.com/nisavid/agent-armory/issues/8): Engineer portable
  agentic workflow equipment.

This capture remains local source material until
[#10](https://github.com/nisavid/agent-armory/issues/10) decides whether to
retain, consolidate, or retire the Seed-era bookkeeping now that active
tracking lives in GitHub Issues.
