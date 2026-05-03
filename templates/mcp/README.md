# MCP Tool Template

## Purpose

Use this template to specify an MCP tool or server operation before implementation
or publication.

## Required fields

- Tool name and purpose.
- Read/write classification.
- Input schema.
- Output schema.
- Auth source.
- Side effects.
- Approval requirements.
- Rate limits.
- Pagination.
- Rollback and cleanup.
- Failure modes.

## Optional fields

- Idempotency key.
- Example calls.
- Audit logging.

## Common mistakes

- Hiding writes behind read-looking names.
- Omitting auth source or credential storage.
- Returning unstructured errors that agents cannot act on.
- Treating external disclosure as read-only.

## Validation expectations

- Schemas are explicit enough for generated callers.
- Side effects and approvals match the strongest operation.
- Failure modes distinguish user error, tool error, auth error, and policy block.
- Security review covers credentials, disclosure, and mutation paths.
