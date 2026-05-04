# Use Standard-Library Python for Seed Validation

Seed Validation will be implemented as `tools/validate_forge_seed.py` using Python 3.14 or newer and only the Python standard library, with `unittest` tests under `tests/test_validate_forge_seed.py`. The tool will default to a concise human report and expose `--json` for machine-readable results.

## Considered Options

- Use standard-library Python.
- Use shell scripts.
- Introduce a package-managed validation stack.

## Consequences

- TOML parsing can use `tomllib` without adding dependencies because Python 3.14 or newer is required.
- The Forge Seed gets a real TDD surface while staying independent of Node, Python package managers, or harness-specific runtimes.
- The tool should validate repository/framework integrity only, not harness behavior.
- Tests should run with `python -m unittest`, not a third-party test runner.
