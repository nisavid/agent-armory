# Pressure Scenarios: Vanilla Harness Capability Profiles

Status: Equipment Blueprint
Promotion state: specified

## Aggregate migration without split truth

The repository stores authored structured harness facts as six per-harness
Vanilla Harness Capability Profiles. The manager must preserve aggregate-
imported facts inside stable per-harness profile claims, mark migrated claims
for schema pressure, keep the human-facing summary aligned with validated
profiles, and reject any retained aggregate catalog as split authored truth.

Expected behavior: the repository has one authored structured profile source,
the per-harness vanilla profiles.

## New harness version with selective re-analysis

A supported harness releases a new version. The manager and agent-guided
workflow must identify version and source deltas, run Capability Claim Triage,
reuse still-applicable grounded claims, and focus analysis on changed or stale
claims.

Expected behavior: the refresh does not exhaustively re-prove every claim, but
does not silently reuse stale evidence.

## Cross-harness compatibility bridge

OpenClaw or another harness accepts another harness's bundle or component
convention. The profile must model the cross-harness import and compatibility
surface as first-class: imported convention, surviving components, activation,
disable behavior, precedence, fidelity limits, and evidence.

Expected behavior: the profile does not flatten compatibility into native
support.

## Memory-like surface without a stable standard

A harness exposes monolithic memory, structured memory, RAG, context provider
plugins, session summaries, persistent goals, or custom instructions. The
workflow must profile memory-like behavior without pretending there is one
standard memory API.

Expected behavior: the profile records load timing, retrieval, mutability,
freshness, privacy, write authority, evidence, and unknowns appropriate to the
observed memory-like surface.

## Active local probing contamination risk

A live-study idea would modify the same Codex harness instance used by the
investigator. The workflow must recognize the contamination risk and either
use passive observation only, move the active test to a separate controlled
instance, or record a selected-rigor deviation.

Expected behavior: the investigator or orchestrator harness is not silently
mutated by the test.

## Alternative analysis angles

A capability claim can be modeled through more than one Capability State Graph.
One graph is easy to run but weakly observes the claim; another is more
controlled but costly. The workflow must compare Capability Analysis Angles,
record advised and selected rigor, and state claim confidence separately from
test sufficiency.

Expected behavior: the first plausible test design is not treated as the only
valid analysis.

## Jig limitation affects selected rigor

A Per-Harness Clean-Room Jig cannot control provider seeds or fully isolate
plugins. The study plan must record the ideal Standard Clean-Room Profiling
Jig expectation, the harness-specific limitation, selected rigor, and how the
limitation affects test sufficiency.

Expected behavior: jig limits are profileable evidence, not prose-only caveats.

## Manual refresh leaves unknowns

Manual refresh completes with some material surfaces still unknown. The
workflow must make those unknown claims explicit and either project follow-up
issues or record why the unknowns are accepted as non-blocking for returning to
Agent Equipment Config.

Expected behavior: unknowns are visible, scoped, and dispositioned.
