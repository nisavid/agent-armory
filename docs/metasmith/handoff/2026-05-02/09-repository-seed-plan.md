# Repository Seed Plan

## Goal

Transform `nisavid/agent-armory` from a blank slate into a durable Agent Equipment Framework.

## Proposed initial structure

```text
README.md
docs/
  ubiquitous-language.md
  equipment-framework.md
  smith-runbook.md
  metasmith-runbook.md
  interface-decision-guide.md
  harness-components.md
  harness-capabilities.md
  harness-capabilities.toml
  evidence-taxonomy.md
  security-and-control.md
templates/
  capability-card.md
  interface-decision-record.md
  skill/
    README.md
    SKILL.md
  hook/
    README.md
    hook.ts
  agent-profile/
    README.md
    profile.toml
  plugin/
    README.md
    manifest.toml
  script/
    README.md
    example-script
  mcp/
    README.md
    tool-spec.md
  config/
    README.md
    example.toml
examples/
  pr-review/
  docs-research/
  observability-investigation/
specs/
  agent-ops.md
  periodic-actions.md
  harness-capability-refresh.md
issues/
  pending/
    high/
```

## README requirements

The repo README should explain:

- what the Agent Armory is,
- what Agent Equipment is,
- what the Agent Equipment Framework is,
- who Smiths and Metasmiths are,
- how to read the repo,
- how to add new equipment,
- where to find templates,
- how to refresh harness capabilities,
- what is intentionally not yet implemented.

## Docs requirements

Docs should be layered:

- conceptual docs for definitions,
- method docs for decisions,
- harness docs for projections,
- templates for creation,
- examples for demonstration,
- specs for future work.

## Template requirements

Templates should be ready for Smiths to copy.

Each template should include:

- purpose,
- required fields,
- optional fields,
- common mistakes,
- validation expectations.

## Example requirements

Examples should demonstrate the method without pretending to be production-ready.

Each example should include:

- capability card,
- interface decision record,
- skill,
- docs,
- script placeholder,
- hook placeholder,
- Agent Profile placeholder,
- config placeholder.

## Harness capability catalog requirements

The catalog must include:

- checked-at date,
- version,
- source URLs,
- evidence level,
- skills support,
- MCP support,
- hooks support,
- Agent Profile support,
- plugin support,
- scheduling support,
- limitations,
- refresh instructions.

## Acceptance criteria

The seed is acceptable when:

1. A new Smith can understand the Framework without reading prior conversations.
2. The Ubiquitous Language is present and clear.
3. The decision method is actionable.
4. Templates cover every major Harness Component.
5. Examples demonstrate the method.
6. Harness facts are versioned and source-backed.
7. Agent Ops and Periodic Actions specs are present.
8. A harness refresh policy exists.
9. The repo avoids fake production-ready code.
10. The README provides a complete reading path.
