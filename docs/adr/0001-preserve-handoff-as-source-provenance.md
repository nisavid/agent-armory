# Preserve Handoff as Source Provenance

Status: Superseded by ADR 0020

The handoff bundle is accepted as source material for the first Agent Equipment Forge, but it will not be the live framework surface. Preserve the bundle under `docs/metasmith/handoff/2026-05-02/`, then project its decisions into canonical docs, templates, examples, specs, and future equipment surfaces so future Smiths get usable guidance without losing provenance.

## Considered Options

- Preserve the bundle in the repo and distill it into canonical framework files.
- Distill only, leaving provenance outside the repo.
- Treat the handoff bundle itself as the live framework documentation.

## Consequences

- Future agents can audit why the Framework began with these choices.
- The live reading path can stay concise and task-shaped.
- Changes to canonical docs must not silently mutate the source handoff; refinements should be re-projected downstream instead.
