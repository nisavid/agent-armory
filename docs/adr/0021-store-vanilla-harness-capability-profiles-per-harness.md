# Store Vanilla Harness Capability Profiles Per Harness

Status: Accepted

Vanilla Harness Capability Profiles live as one structured file per supported
Agent Harness, with the Harness Capability Catalog as the catalog front door
and summary surface. Per-harness files keep refresh diffs reviewable, allow
harness-specific extensions without rewriting unrelated profiles, and give the
profile manager a stable unit for validation, diffing, scouting, and migration.

## Considered Options

- Keep one aggregate structured catalog file.
- Store one structured Vanilla Harness Capability Profile per supported Agent
  Harness.

## Consequences

- `docs/harness-capabilities.md` remains the human-facing catalog front door.
- `docs/harness-capabilities/vanilla/<harness-id>.toml` stores each Vanilla
  Harness Capability Profile.
- Profile schema and migrations live under `docs/harness-capabilities/schema/`.
- The aggregate `docs/harness-capabilities.toml` is migrated completely into
  per-harness profiles and removed as authored truth to avoid drift and
  split-brain profile state.
- Profile management tooling validates, summarizes, diffs, scouts, and migrates
  per-harness profiles.
