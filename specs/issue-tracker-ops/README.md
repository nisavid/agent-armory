# Issue Tracker Ops

Status: Equipment Candidate
Promotion state: implemented for bootstrap MVP; full delivery remains open

This Equipment Design Bundle records the bootstrap design and planned
full-delivery contracts for Issue Tracker Ops, also called Issue Ops, tracked by
GitHub issue #11.

## Bundle contents

- [Capability card](capability-card.md)
- [Interface decision record](interface-decision-record.md)
- [Security and control classification](security-control-classification.md)
- [Pressure scenarios](pressure-scenarios.md)
- [Validation plan](validation-plan.md)
- [Closeout evidence plan](closeout-evidence-plan.md)
- [Config profile and onboarding](config-profile-and-onboarding.md)

## Bootstrap surface

The bootstrap MVP is the tracker-neutral core at `tools/issue_tracker_core.py`
and the GitHub Issues adapter at `tools/issue_tracker_ops.py`. The core defines
operation ids, operation classes, side-effect classes, capability dispositions,
audit requirements, adapter capability entries, and operation-plan output. The
adapter exposes that contract through read-only JSON commands before callers
use tracker-specific commands.

The bootstrap scope covers direct issue create, issue update, issue comment,
label-axis audit, issue dependency operations, fallback-record reconciliation,
neutral core inspection, adapter capability inspection, and neutral operation
planning for GitHub Issues without Projects. Full Issue Ops delivery remains
tracked in issue #11 and child issues.

Inspection commands:

- `describe-core`
- `describe-adapter --adapter github-issues-baseline`
- `plan-operation --adapter github-issues-baseline --operation <operation-id>`

Runtime adapter commands use the local `gh` CLI as the authenticated transport
and default write modes to dry-run output unless `--execute` is provided. Live
mutation requires either usable Config authorization or
`--mutation-policy-ref <ref>`. Mutation commands perform live preflight reads
under `--execute` to block duplicate issue creation and comments, skip exact
no-op issue updates, and skip already-applied or already-absent dependency
changes.

The adapter consumes explicit Agent Equipment Config sources when callers pass
`--config-layer` or `--config-plain-handoff`. Config-aware dry-runs include the
effective Config evidence, consumer action decision, and adapter enforcement
projection. Config-aware live mutation requires `--execute`, an Issue Ops
consumer decision that supports execute mode, and
`consumer_enforcement_projection.adapter_action = "allow"`; blocking,
unsupported, malformed, or missing projection evidence fails closed before the
adapter invokes `gh`.

Fallback records use `issue_tracker_ops.fallback_record.v1alpha1`. The adapter
writes a fallback record only when `--fallback-record-file <path>` is provided
and a live mutation cannot be completed. `reconcile-fallback` checks the
intended tracker target before retry or retirement, and `--retire-record`
updates the local fallback record only after projection is verified.

Durable layered configuration belongs to Agent Equipment Config. Issue Ops owns
the Issue Ops namespace, plain handoff shape, and behavior-specific semantics
for the adapter. The progressive config profile and onboarding contract is
defined in [Config profile and onboarding](config-profile-and-onboarding.md). Full
runtime delivery remains tracked by issue #11 child work.

Issue Ops also provides the issue-tracked path for Reflection Findings until
generic Reflection and cognition equipment can automate more of that capture,
routing, and follow-up loop.
