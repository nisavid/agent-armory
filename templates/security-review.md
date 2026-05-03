# Security Review

Status: Template

## Scope

Name the change set, files, generated artifacts, tools, and out-of-scope areas.

## Assets

List secrets, credentials, prompts, local files, repositories, issue trackers,
deployment targets, user data, and external systems that need protection.

## Trust boundaries

Identify boundaries between agent, human operator, local host, sandbox, MCP
server, external API, generated code, and published artifact.

## Side effects

Classify side effects as read-only, external disclosure, local write, network
write, process execution, privileged operation, or irreversible mutation.

## Threats

Record plausible prompt injection, data exfiltration, confused deputy,
overbroad permission, unsafe hook, unsafe tool, supply-chain, and stale-doc
threats.

## Controls

List deterministic validators, approvals, least-privilege settings, redaction,
audit records, and fail-closed behavior.

## Findings

Track each finding with severity, evidence, decision, fix, and verification.

## Residual risk

State what remains accepted, deferred, blocked, or awaiting broader review.
