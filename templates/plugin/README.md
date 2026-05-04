# Plugin Template

## Purpose

Use this template to describe a harness plugin that packages multiple equipment
components behind one installable or loadable boundary.

## Required fields

- Plugin name.
- Version.
- Description.
- Components.
- Permissions.
- Ownership and source notes.

## Optional fields

- Config defaults.
- Compatibility matrix.
- Install hooks.
- Upgrade or migration notes.
- Local validation commands.

## Common mistakes

- Bundling unrelated capabilities into one plugin.
- Omitting permissions because each component documents its own needs.
- Publishing example components as validated equipment.
- Leaving version or compatibility promises unverified.

## Validation expectations

- The manifest TOML parses.
- Components point to real files or packages.
- Permissions summarize the strongest capability in the plugin.
- Security review covers the plugin boundary, not only individual components.
