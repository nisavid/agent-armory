#!/usr/bin/env python3.14
from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    detail: str
    path: str


MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
FENCE_START_RE = re.compile(r"(`{3,}|~{3,})")


def strip_fenced_code_blocks(markdown: str) -> str:
    visible_lines: list[str] = []
    fence_char: str | None = None
    fence_length = 0
    for line in markdown.splitlines(keepends=True):
        stripped = line.lstrip(" ")
        indent = len(line) - len(stripped)
        if indent <= 3:
            if fence_char is not None:
                closing_fence = re.match(rf"{re.escape(fence_char)}{{{fence_length},}}\s*$", stripped)
                if closing_fence:
                    fence_char = None
                    fence_length = 0
                continue
            opening_fence = FENCE_START_RE.match(stripped)
            if opening_fence:
                marker = opening_fence.group(1)
                fence_char = marker[0]
                fence_length = len(marker)
                continue
        if fence_char is None:
            visible_lines.append(line)
    return "".join(visible_lines)


def validate_required_paths(root: Path, paths: Iterable[str]) -> list[CheckResult]:
    results: list[CheckResult] = []
    for path in paths:
        exists = (root / path).exists()
        results.append(
            CheckResult(
                name=f"required_path:{path}",
                ok=exists,
                detail="exists" if exists else "missing",
                path=path,
            )
        )
    return results


def find_markdown_links(markdown: str) -> list[str]:
    searchable_markdown = strip_fenced_code_blocks(markdown)
    links: list[str] = []
    for match in MARKDOWN_LINK_RE.finditer(searchable_markdown):
        target = match.group(1).split("#", 1)[0]
        if not target:
            continue
        if "://" in target or target.startswith(("mailto:", "#")):
            continue
        links.append(target)
    return links


def load_toml(path: Path) -> dict:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def render_human(results: list[CheckResult]) -> str:
    lines: list[str] = []
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        lines.append(f"{status} {result.name} {result.path} - {result.detail}")
    failed = sum(1 for result in results if not result.ok)
    passed = len(results) - failed
    lines.append(f"{failed} failed, {passed} passed")
    return "\n".join(lines)


def render_json(results: list[CheckResult]) -> str:
    return json.dumps([asdict(result) for result in results], indent=2, sort_keys=True)


def run(root: Path) -> list[CheckResult]:
    required_paths = [
        "README.md",
        "AGENTS.md",
        "CONTEXT.md",
        "docs/prd/framework-seed.md",
        "docs/metasmith/source-projection.md",
        "docs/harness-capabilities.toml",
    ]
    return validate_required_paths(root, required_paths)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the Agent Armory Framework Seed.")
    parser.add_argument("--root", default=".", help="Repository root to validate.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args(argv)

    results = run(Path(args.root).resolve())
    output = render_json(results) if args.json else render_human(results)
    print(output)
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    sys.exit(main())
