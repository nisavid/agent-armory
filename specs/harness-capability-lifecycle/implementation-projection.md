# Implementation Projection: Harness Capability Lifecycle Methodology

Status: Equipment Blueprint
Promotion state: specified

## Projection principles

Implementation work should be narrow, test-first, and aligned with current
ownership boundaries:

- Manager Core owns deterministic lifecycle artifacts, validation, JSON output,
  diffing, apply gates, and audit formatting.
- Agent-guided workflows own source interpretation, cross-harness correlation,
  schema pressure judgment, and selected-rigor decisions.
- GitHub Issues own durable follow-up projection.
- Agent Equipment Config owns configurable policy after issue #23 work lands.
- Periodic Actions owns cadence and recurring execution after issue #3 work
  lands.
- Agent Test Jigs and Harness Test Suites own controlled local validation only
  after issue #61 follow-up work lands.

No implementation issue should combine all of those responsibilities.

## Projected issue set

The implementation projection created these follow-up issues:

1. [#173 Implement Harness Capability lifecycle candidate records in Manager Core](https://github.com/nisavid/agent-armory/issues/173):
   unblocked first deterministic slice for candidate artifacts and JSON output.
2. [#174 Implement Harness Capability lifecycle disposition and schema-pressure gates](https://github.com/nisavid/agent-armory/issues/174):
   blocked by #173 unless narrowed to an equivalent first slice.
3. [#175 Update manual Harness Capability refresh workflow for lifecycle candidates](https://github.com/nisavid/agent-armory/issues/175):
   blocked by #173 and #174 unless narrowed to a docs-only bridge.
4. [#176 Route Harness Capability lifecycle findings through Issue Tracker Ops and Reflection Findings](https://github.com/nisavid/agent-armory/issues/176):
   blocked by #173 and #174; Reflection-specific routing may also depend on
   #25.
5. [#177 Integrate Harness Test Suite results with Harness Capability lifecycle evidence](https://github.com/nisavid/agent-armory/issues/177):
   blocked by #164, #167, and any prerequisite Jig Test Plan, first Jig
   Driver, Assertion Provider, or adequacy-report work.
6. [#178 Integrate Harness Capability lifecycle with Config and Periodic Actions](https://github.com/nisavid/agent-armory/issues/178):
   blocked by #23 and #3.

The blocked dependency labels are intentional. Native issue dependencies remain
authoritative when they are present.

## Acceptance criteria for implementation issues

Every implementation issue should include:

- current source-of-truth spec links;
- precise owned outputs;
- non-owned boundaries;
- security/control requirements;
- TDD requirement for executable code or schema validation;
- validation commands;
- issue projection or docs-closeout expectations.

## Out of scope for this PR

- CLI/API/schema implementation.
- Profile schema migration.
- Manager Core candidate artifact commands.
- Manual refresh checklist rewrites beyond discoverability links.
- Hook, MCP/tool, plugin, Config, or Periodic Actions implementation.
- Jig Runner, Jig Driver, Harness Test Suite, or Learned Oracle work.
- ADR 0023, because this design does not make a hard-to-reverse tradeoff.

## Update contract

When a projected issue lands, update the lifecycle bundle or related workflow
docs only if the implemented behavior changes the methodology, not merely
because an issue changed state.
