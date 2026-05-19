# Security Best Practices Baseline

Status: Security Best Practices
Last refreshed: 2026-05-19

This baseline records the current secure shape of Agent Armory's executable
repository surfaces. It applies to the Python CLI tools, executable templates,
and local evidence workflows that exist now.

Agent Armory does not currently define a deployed web service, browser
frontend, authentication session runtime, or database query layer. Web, Django,
FastAPI, Flask, JavaScript web-server, frontend, SQL, and ORM-specific guidance
does not apply to the current runtime surface.

## Current Security Posture

The 2026-05-19 Codex Security refresh completed a repository-wide scan of the
current executable surface and found no reportable findings. The raw scan
bundle is instance-scoped scratch evidence; this document and the repository
threat model carry the durable conclusions.

## Python CLI Tools

Use Python CLI tools for deterministic repository validation and bounded local
operations. Keep them standard-library-first unless a real dependency removes
more risk than it adds.

- Parse structured input with `json`, `tomllib`, `argparse`, or typed helper
  functions rather than ad hoc string splitting.
- Treat caller-supplied file paths as untrusted until they are made
  repo-relative, checked for absolute paths and `..`, checked for symlinks, and
  resolved under the repository root.
- Keep mutation commands dry-run by default when they can affect external
  systems or durable repository state.
- Require explicit operator authority or approval for local writes, profile
  mutation, external disclosure, network writes, process execution, privileged
  operations, and irreversible mutations.
- Use hash or source-text preconditions before applying a planned write.
- Prefer argument-list subprocess calls with structured stdin. Do not build
  shell command strings from user input.
- Catch parse and I/O failures at CLI boundaries and return deterministic exit
  codes.

## Config and Secrets

Agent Equipment Config records unresolved secret references. It does not own
secret-provider value resolution.

- Store provider-owned references, not secret values.
- Treat direct secret-like values as policy violations.
- Redact secret-like fields and secret-reference names in CLI, MCP, log, audit,
  and review output.
- Keep Config mutation-capable behavior blocked unless the effective Config is
  usable, the source is eligible, authority is present, and the write target is
  owned by the chosen surface.

## GitHub Reads and External Mutation

Issue Tracker Ops is the current external API read and mutation surface.

- Default issue operations to dry-run.
- Require `--execute` for live GitHub reads or writes.
- Serialize request bodies as JSON and pass them to `gh api` through stdin.
- Preserve Config preflight as an additional refusal path for mutation-capable
  operations.
- Summarize API output so routine command output does not accidentally publish
  broader response payloads.

## Templates and Future Equipment

Templates are teaching and scaffold surfaces. They must remain safe before a
Smith copies them into future equipment.

- Hooks default to fail-closed decisions and declare side-effect
  classification, approval behavior, and failure handling.
- Script templates remain deterministic, non-mutating, and standard-library
  only unless a specific equipment spec authorizes more capability.
- MCP/tool specs record read/write classification, input and output schemas,
  auth source, side effects, approval requirements, rate limits, pagination,
  rollback or cleanup, and failure modes.
- Agent Profile, plugin, and config templates keep approval coverage aligned
  with the canonical side-effect vocabulary.

## Evidence and Closeout

- Classify evidence before committing or projecting it.
- Commit durable project evidence and portable review summaries.
- Keep raw scan bundles, local paths, screenshots, generated scratch reports,
  and host-specific logs out of durable project docs unless explicitly promoted
  with a portability rationale.
- Record security findings, suppressions, deferrals, and no-finding outcomes in
  PR bodies, issue comments, closeout docs, or neutral security docs.

## Refresh Triggers

Refresh this baseline when Agent Armory adds or materially changes:

- executable code, hooks, MCP/tool definitions, plugin manifests, scripts, or
  permissions;
- Config secret resolution, adapter enforcement, or mutation authority;
- GitHub, network, filesystem, process, or scheduler side effects;
- package metadata, distribution channels, signed artifacts, or update flows;
- web services, auth/session handling, databases, frontend surfaces, or cloud
  SDK integrations.
