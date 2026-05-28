# Pressure Scenarios: Harness Capability Lifecycle Methodology

Status: Equipment Blueprint
Promotion state: specified

## New capability discovery

Scenario:

A harness release introduces a new tool-permission setting with a short
release-note mention and no detailed docs yet.

Expected behavior:

- The candidate records the harness, version basis, first-party source pointer,
  evidence class, affected capability family, and uncertainty.
- No profile mutation happens during discovery.
- The next action is source refresh, Capability Claim Triage, or a Study Plan,
  not a direct supported claim.

## False cross-harness equivalence

Scenario:

Two harnesses both say "hooks", but one supports trusted project-local command
hooks with matcher limitations and another supports plugin hook callbacks with
different lifecycle and authority semantics.

Expected behavior:

- The correlation rubric compares activation, authority, side effects, scope,
  lifecycle, and failure semantics.
- The result is harness-specific variant or unresolved unless the meaningful
  behavior is actually common.
- Smith-facing docs do not say both harnesses support the same hook capability
  merely because the label matches.

## Compatibility bridge

Scenario:

A harness imports a compatible bundle from another harness but only supports a
subset of that bundle's skills, hooks, or commands.

Expected behavior:

- The bridge is recorded as compatibility evidence, not native support for
  every imported component.
- Unsupported or unknown imported components remain separate claims.
- Follow-up work targets the actual bridge semantics and gaps.

## Schema pressure

Scenario:

Source-backed evidence proves that lifecycle reload behavior depends on project
trust, active config layer, handler type, matcher support, and unstable
transcript payloads. The current claim fields cannot represent those details
without losing material meaning.

Expected behavior:

- The candidate routes to schema pressure review.
- Existing profile claims remain unchanged or narrower until schema and
  validation work exists.
- The implementation issue owns schema, migration, fixture, and Manager Core
  tests.

## Deprecation

Scenario:

A harness marks a permission mode as deprecated but still available in the
checked release.

Expected behavior:

- The lifecycle disposition is `deprecate`, not `remove`.
- The profile claim remains descriptive and version-scoped.
- Follow-up records replacement guidance only outside the descriptive profile
  if downstream consumers need it.

## Removal

Scenario:

A later release removes the deprecated permission mode and first-party docs no
longer describe it.

Expected behavior:

- The candidate records first-party removal evidence and affected prior claim
  IDs.
- The profile update uses Manager Core gates and preserves traceability to the
  removed or replaced claim.
- If consumers still depend on the old capability, separate follow-up issues
  route migration or compatibility work.

## Unavailable jig validation

Scenario:

A lifecycle candidate needs runtime proof, but no Jig Runner, first Jig Driver,
or Harness Test Suite implementation exists yet.

Expected behavior:

- The candidate records that jig validation is unavailable.
- The lifecycle uses source refresh, local observation through approved study,
  or `unknown` disposition until the jig path exists.
- The profile does not imply controlled execution proof.

## Implementation projection sequencing

Scenario:

The lifecycle design identifies needs for a candidate schema, Manager Core
commands, manual refresh updates, Config policy, Periodic Actions cadence, and
Harness Test Suite integration.

Expected behavior:

- Projection splits the work into separately validatable issues.
- Dependencies are explicit for Config, Periodic Actions, and Jig work.
- Future implementation issues carry TDD requirements and acceptance criteria.

## Review cognitive load

Scenario:

A manual refresh report includes many sources, local observations, schema
pressure notes, and issue projections.

Expected behavior:

- The report starts with phase, decision, affected harnesses, evidence class,
  and next action.
- Detailed logs and raw artifacts stay behind references with durability
  classification.
- Reviewers can see whether the case is common capability, variant,
  compatibility bridge, superficial equivalence, or unresolved without reading
  every raw note.

## Security-sensitive lifecycle claim

Scenario:

A candidate changes sandbox, approval, MCP/tool, hook, plugin, managed-policy,
network, or automation behavior.

Expected behavior:

- The lifecycle records authority, side effects, applicability scope, and
  failure behavior before profile mutation.
- Security closeout applies even for doc-only changes that shape downstream
  policy.
- Reportable findings block merge-readiness or receive approved deferment with
  issue tracking.
