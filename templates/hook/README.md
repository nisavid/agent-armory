# Hook Template

## Purpose

Use this template to specify a harness hook that observes or gates an agent event
with a clear side-effect and approval contract.

## Required fields

- Hook name and event source.
- Side-effect classification.
- Approval behavior.
- Failure handling.
- Exported hook function or equivalent harness contract.

## Optional fields

- Redaction policy.
- Idempotency key.
- Retry policy.
- Structured audit record.
- Test fixture examples.

## Common mistakes

- Running mutations from a hook without an approval boundary.
- Treating failures as harmless without deciding fail-open or fail-closed.
- Depending on ambient credentials without documenting their source.
- Logging secrets or private prompt material.

## Validation expectations

- The hook contract is exported and type-checkable for the target harness.
- Side effects are classified before implementation.
- External disclosure, local write, network write, process execution,
  privileged operation, and irreversible mutation require explicit approval.
- Unsafe mutations fail closed.
- Tests cover allowed, blocked, malformed, and error paths.
