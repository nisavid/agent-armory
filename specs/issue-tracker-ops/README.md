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

The bootstrap MVP is the GitHub Issues adapter at
`tools/issue_tracker_ops.py`. It uses the local `gh` CLI as the authenticated
transport and defaults write modes to dry-run output unless `--execute` is
provided.

The bootstrap scope covers direct issue create, issue update, issue comment,
label-axis audit, and issue dependency operations for GitHub Issues without
Projects. Full Issue Ops delivery remains tracked in issue #11 and child
issues.

The adapter consumes explicit Agent Equipment Config sources when callers pass
`--config-layer` or `--config-plain-handoff`. Config-aware dry-runs include the
effective Config evidence, consumer action decision, and adapter enforcement
projection. Config-aware live mutation requires `--execute`, an Issue Ops
consumer decision that supports execute mode, and
`consumer_enforcement_projection.adapter_action = "allow"`; blocking,
unsupported, malformed, or missing projection evidence fails closed before the
adapter invokes `gh`.

Durable layered configuration belongs to Agent Equipment Config. Issue Ops owns
the Issue Ops namespace, plain handoff shape, and behavior-specific semantics
for the adapter. The progressive config profile and onboarding contract is
defined in [Config profile and onboarding](config-profile-and-onboarding.md). Full
runtime delivery remains tracked by issue #11 child work.

Issue Ops also provides the issue-tracked path for Reflection Findings until
generic Reflection and cognition equipment can automate more of that capture,
routing, and follow-up loop.
