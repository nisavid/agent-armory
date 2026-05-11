# Harness Capability Refresh Spec

Status: Equipment Blueprint
Promotion state: specified

This spec is retained as the deferred recurring-refresh blueprint. The active
pre-Config work is the
[Vanilla Harness Capability Profiles](vanilla-harness-capability-profiles/)
Equipment Design Bundle; recurring refresh integration remains deferred until
Agent Equipment Config and Periodic Actions exist.

Manual profile refresh now belongs to the Harness Capability Profile Manager
Core and its agent-guided workflow. This recurring-refresh blueprint should
invoke that staged scout, analyze, plan, diff, apply, and audit surface later;
it should not introduce a separate profile mutation path.

This spec describes desired behavior for future Agent Equipment. It does not implement Agent Equipment, create a live scheduler, or keep current harness facts refreshed by itself. Until this recurring equipment exists, current profile state is maintained through the Harness Capability Profile Manager Core and manual refresh workflow.

## Purpose

Harness Capability Refresh keeps the Armory's harness knowledge current enough for Forge decisions. It periodically checks supported harnesses, records source-backed capability facts, and opens a high-priority issue or issue candidate when depended-on behavior changes.

## User stories

### Maintainer receives drift signal

As a maintainer, I receive a clear signal when a harness changes a capability that the Forge depends on.

### Smith receives source-backed facts

As a Smith, I can inspect the latest refresh record for a supported harness and see the source URLs, checked-at timestamp, version evidence, affordances, limitations, and Forge impact.

### Agent falls back without issue access

As an agent without GitHub issue write access, I can still record a high-priority issue candidate in the repo for later triage.

## Acceptance criteria

Harness Capability Refresh covers these harnesses:

- Codex,
- OpenClaw,
- Hermes Agent,
- Claude Code,
- Cursor,
- OpenCode.

For each harness, the refresh records these tracked fields:

- current version,
- checked-at timestamp,
- source URLs,
- supported Harness Component types,
- key affordances,
- known limitations,
- scheduling mechanisms,
- hook/event names,
- skill discovery paths,
- plugin interfaces,
- MCP behavior.

When depended-on capabilities change, the refresh creates a high-priority issue with this title shape:

```text
[high] Refresh Forge for <harness> <capability> change
```

The issue body includes:

- current version,
- previous version,
- capability affected,
- source evidence,
- expected Forge impact,
- suggested Smith task.

If GitHub issue creation is unavailable, the refresh writes a markdown issue candidate under `issues/pending/high/`:

```text
issues/pending/high/
```

The refresh uses a weekly starting cadence.

The prioritization order is:

1. security-relevant behavior,
2. hook blocking semantics,
3. permissions and sandboxing,
4. scheduling,
5. skill discovery and context behavior,
6. plugin packaging,
7. MCP tool exposure and context bloat.

## Harness projections

Harness Capability Refresh must define projections for:

- Codex,
- OpenClaw,
- Hermes Agent,
- Claude Code,
- Cursor,
- OpenCode.

Each projection must state:

- which first-party or authoritative sources are checked,
- whether current version discovery is automated or manual,
- how scheduling mechanisms are refreshed,
- how hooks and blocking semantics are verified,
- how skill discovery paths and plugin interfaces are validated,
- how MCP behavior is checked,
- where refresh state is stored,
- how the high-priority issue or issue candidate is created.

## Non-goals

- Harness Capability Refresh does not replace Vanilla Harness Capability
  Profiles, the Harness Capability Catalog front door, or the Harness
  Capability Profile Manager Core.
- Harness Capability Refresh does not accept unsourced claims as refreshed facts.
- Harness Capability Refresh does not require GitHub write access when the issue-candidate fallback can preserve the signal.
- Harness Capability Refresh does not guarantee that every harness publishes machine-readable version or capability metadata.

## Open questions

- Should refresh output update per-harness profiles directly after explicit apply, or stage a candidate for review?
- Which source classes are authoritative for each harness when first-party docs and observed behavior disagree?
- Should security-relevant changes trigger an additional security scan before issue projection?
