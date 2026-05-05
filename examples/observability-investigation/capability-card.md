# Capability Card: Observability Investigation

Status: Forge Example
Promotion state: example

This Forge Example is not Published Agent Equipment and is not installable.
Trace: capability card -> [interface decision record](interface-decision-record.md) -> projected components.

## Purpose

Investigate service latency, error, or regression signals by correlating bounded metrics, traces, logs, and deploy history.

## Vision alignment

This example shows how an investigation Assembly lets the Agent synthesize a
timeline and confidence model while typed observability tools, query bounds,
redaction gates, config, scripts, and local docs protect reliability and
authority boundaries.

## Users

- Human operator: wants a clear incident timeline and evidence-backed suspected cause.
- Root agent: coordinates investigation without exceeding autonomy or data-access policy.
- Specialist agent: inspects observability data with scoped tools and redaction controls.
- External system: observability backend, deploy tracker, incident tracker, or service catalog.

## Target harnesses

- Codex: illustrative target for local docs, scoped tools, config, and specialist profile design.
- Other harnesses: deferred until observability tool integration, credential handling, and lifecycle controls are mapped.

## Risks

- Security: logs and traces may contain secrets, tokens, customer data, or internal hostnames.
- Privacy: observability queries can expose user data or production incident details.
- Reliability: broad or unbounded queries can mislead, overload systems, or miss the relevant time window.
- Context budget: raw logs and traces can consume the agent's useful context quickly.
- Human workflow: mitigation suggestions may imply operational authority the agent does not have.

## External systems

- Metrics backend.
- Trace backend.
- Log backend.
- Deploy history and incident tracker.
- Service catalog or ownership registry.

## Side effects

Default side effect classification: read-only for bounded queries.

Potential side effects requiring gates:

- external disclosure when incident data leaves the approved tool boundary;
- network write if the agent annotates incidents or deploy records;
- privileged operation if production credentials or break-glass access are involved.

## Needed Harness Components

- Skills: investigation sequence and evidence synthesis.
- MCP/tools: metrics, traces, logs, deploy history, and service catalog readers.
- Hooks: query bounds, redaction, and audit logging.
- Agent Profiles: incident investigator with scoped read-only observability tools.
- Plugins: deferred bundle for the observability capability set.
- Scripts: trace summarizer, deploy mapper, and log redaction checker.
- Config: allowed environments, service allowlist, default lookback, query limits.
- Docs: incident runbooks, service ownership, data-handling policy.

## Hard rules

- Start with bounded service, environment, and time window.
- Redact secrets and sensitive user data before copying evidence into durable docs or chat.
- Do not run mitigations, rollbacks, or production writes from the investigation path unless explicitly authorized elsewhere.
- State confidence and separate evidence from hypotheses.

## Deterministic checks

- Query window validation.
- Service and environment allowlist validation.
- Secret and sensitive-data redaction scan.
- Timeline consistency check against deploy records.

## Output contract

An investigation report with:

- incident scope and time window;
- timeline;
- evidence from metrics, traces, logs, and deploys;
- suspected cause with confidence;
- mitigation options that respect current authority;
- unknowns and next checks.

## Failure modes

- Missing service or environment: ask for the missing scope before querying.
- Query exceeds configured bounds: fail closed and request a narrower window or approval.
- Potential secret in evidence: redact before reporting or stop if redaction is uncertain.
- Tool unavailable: record the gap and continue only with clearly labeled partial evidence.

## Evidence

Evidence category: implementation inference for this example shape. Real investigations need source-supported evidence from the relevant observability systems.

## Open questions

- Which observability tools should be canonical for each harness and deployment environment?
- Which incident actions are purely investigative, and which require separate operational approval?
