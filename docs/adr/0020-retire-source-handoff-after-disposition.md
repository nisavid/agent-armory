# ADR 0020: Retire Source Handoff After Disposition

Status: Accepted

Supersedes: ADR 0001, ADR 0015

## Context

ADR 0001 preserved the imported source handoff as provenance. ADR 0015 added a
Source Projection Register to make accepted requirements auditable. During Forge
Seed closeout, the source handoff became less useful as a live repository
surface: it preserved formative material, but also carried stale terminology,
source-only prompts, and pre-Seed uncertainty.

## Decision

Retire raw source handoff files after a source-bearing checkpoint records a
self-contained Source Disposition Ledger. The ledger must preserve enough
source identity evidence, normalized summaries, synthetic source payloads,
manifest and disposition digests, operator decisions, and source-retirement
stamp evidence for future Forgewrights to audit the Seed without relying on raw
source files, chat history, host-local scratch artifacts, or Git object
reachability.

## Consequences

- `docs/metasmith/**` is not part of the final live Forge Seed tree.
- Source history remains auditable through the Source Disposition Ledger and the
  committed source-bearing checkpoint.
- Deferred work moves to governed follow-up captures rather than raw source
  archives.
- ADR 0001 and ADR 0015 remain useful historical context but no longer define
  the current source-retirement policy.
