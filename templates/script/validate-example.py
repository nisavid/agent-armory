#!/usr/bin/env python3.14
"""Example validator with a deterministic exit-code contract."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    detail: str


def run(subject: str) -> list[CheckResult]:
    return [
        CheckResult(
            name="subject",
            ok=bool(subject.strip()),
            detail="present" if subject.strip() else "missing",
        )
    ]


def main() -> int:
    """CLI entry point. Exit 0 for pass, 1 for validation failure, 2 for usage errors."""
    parser = argparse.ArgumentParser(description="Validate an example subject.")
    parser.add_argument("subject", help="Subject string to validate.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    args = parser.parse_args()

    results = run(args.subject)
    if args.json:
        print(json.dumps([asdict(result) for result in results], indent=2, sort_keys=True))
    else:
        for result in results:
            status = "PASS" if result.ok else "FAIL"
            print(f"{status} {result.name} - {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
