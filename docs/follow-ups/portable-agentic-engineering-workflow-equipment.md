# Portable Agentic Engineering Workflow Equipment

Status: Follow-Up Capture

## Purpose

Design a generic, reusable ingestion and promotion flow for portable Agent
Equipment. The first motivating import source is the operator's current
user-global equipment, but the flow must work for any repo, harness, or
equipment kind.

## Captured Requirements

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

## Pending Projection

GitHub Issue Projection is pending because the Forge Seed pauses after branch
push and before PR creation. This file governs the follow-up until that issue is
created or updated.
