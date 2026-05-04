# Script Template

## Purpose

Use this template for deterministic helper scripts that make agent workflows
repeatable, reviewable, and easier to validate than prose-only instructions.

## Required fields

- CLI entry point.
- `--help` output.
- Deterministic exit-code contract.
- Machine-readable output when practical.
- Safe defaults and explicit destructive flags.

## Optional fields

- JSON schema.
- Dry-run mode.
- Fixture directory.
- Golden output examples.
- Environment variable contract.

## Common mistakes

- Returning success for skipped or partially checked work.
- Requiring ambient state that the script does not report.
- Mixing validation and mutation without a clear flag.
- Printing verbose logs where an agent needs structured output.

## Validation expectations

- The script compiles or parses.
- Exit `0` means success, exit `1` means validation failure, and exit `2` means
  usage or environment error unless the script documents a different contract.
- Tests cover pass, fail, and malformed input cases.
- Destructive operations are opt-in.
