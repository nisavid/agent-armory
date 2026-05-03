# MCP/tool definition notes: <tool-name>

## Purpose

State the user-visible operation and the reason it belongs behind an MCP/tool
boundary.

## Read/write classification

Classify the operation as read-only, local write, network write, external
disclosure, process execution, privileged operation, or irreversible mutation.

## Input schema

Define required fields, optional fields, validation rules, defaults, and examples.

## Output schema

Define success output, partial output, error output, and any stable machine fields
agents may depend on.

## Auth source

State where credentials come from, how scope is limited, and whether the tool can
run without credentials.

## Side effects

Describe filesystem, process, network, issue-tracker, repo, deployment, or other
state changes.

## Approval requirements

State which calls require stakeholder approval, sandbox escalation, or a human
operator action.

## Rate limits

State relevant upstream limits, local throttles, retry budgets, and what the tool
returns when a limit is reached.

## Pagination

State whether responses paginate, how callers request the next page, and how the
tool reports partial results.

## Rollback and cleanup

State whether mutations can be rolled back, what cleanup is automatic, and what
manual recovery step remains after partial failure.

## Failure modes

Separate validation failure, auth failure, policy denial, transient remote
failure, and partial mutation.
