# ADR 0019: Adopt Forge Nomenclature

Status: Accepted

## Context

The Seed established enough durable shape to give the Agent Equipment work a
more precise project vocabulary. The old Framework and Metasmith terms were
useful during formation, but the operator selected a Forge-centered vocabulary
that better matches the Armory theme and leaves `framework` available for
ordinary software and process frameworks.

## Decision

Use Agent Equipment Forge as the full name and Forge as the normal short name.
Use Forgewright for agents that build or refine the Forge, and keep Smith for
agents that use the Forge to craft Agent Equipment.

Record this rename map for posterity:

| Prior term | Current term |
| --- | --- |
| Agent Equipment Framework | Agent Equipment Forge |
| Framework Seed | Forge Seed |
| Canonical Framework Docs | Forge Canon |
| Framework Path / Preloaded Framework Path | Forge Conveyor |
| Human Framework Entry | Forge Tour |
| Framework Example | Forge Example |
| Metasmith | Forgewright |
| Framework Requirement | Tooling Gap |
| Framework Requirement Escalation | Tooling Request |
| Smith-to-Metasmith Handoff | Smith-to-Forgewright Handoff |
| Metasmith Hand-Back | Forgewright Hand-Back |
| Downstream Smith Spec | Equipment Blueprint |

The mapping is historical and migratory. Durable current docs should state the
desired current shape directly rather than preserving old-name exclusions.

## Consequences

- Current live routes, validation, README guidance, agent routing, and closeout
  evidence use Forge names.
- ADRs and other historical passages may retain old terms when the history
  itself is the subject.
- Ordinary lowercase `framework` remains available for generic software and
  process frameworks.
