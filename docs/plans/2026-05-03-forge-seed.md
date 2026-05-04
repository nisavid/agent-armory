# Forge Seed Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Forge Seed defined in `docs/prd/forge-seed.md`.

**Architecture:** The seed is documentation- and validation-first. Canonical docs, templates, examples, Equipment Blueprints, and refreshed harness facts are created as Seed Surfaces, while `tools/validate_forge_seed.py` and `tests/test_validate_forge_seed.py` enforce the repository shape, link paths, source disposition, promotion-state labels, and catalog metadata.

**Source-retirement note:** Task 2 records the original source-bearing implementation path. ADR 0020 superseded that path for the final tree: `docs/metasmith/**` and the Source Projection Register were retired after the source-bearing checkpoint, and `docs/closeout/forge-seed-source-disposition.md` is now the durable source-disposition surface. Do not recreate `docs/metasmith/**` during closeout unless a later accepted decision explicitly reopens source-bearing work.

**Tech Stack:** Markdown, TOML, Python 3.14 standard library, `unittest`, Git, Firecrawl or equivalent first-party web source retrieval, GitHub issue tooling for post-review Issue Projection.

---

## File Structure

Create or modify these files:

- Modify: `README.md` for the Forge Tour.
- Modify: `AGENTS.md` for the Forge Conveyor, durable file-placement policy, and change-set security closeout policy.
- Modify: `CONTEXT.md` for any new durable term exposed by implementation or closeout policy.
- Modify: `docs/prd/forge-seed.md` if security closeout or seed-surface requirements are refined during implementation.
- Create: ADRs for new durable policy decisions.
- Create: `docs/closeout/forge-seed-source-disposition.md` for source-handoff disposition and final source-retirement evidence.
- Create: `docs/security/threat-model.md` for the persistent Repository Threat Model.
- Create: `docs/security/forge-seed-closeout.md` for Forge Seed security closeout evidence.
- Create: `docs/closeout/forge-seed-documentation.md` for Forge Seed documentation closeout evidence.
- Create: `docs/ubiquitous-language.md`.
- Create: `docs/agent-equipment-forge.md`.
- Create: `docs/smith-runbook.md`.
- Create: `docs/forgewright-runbook.md`.
- Create: `docs/interface-decision-guide.md`.
- Create: `docs/harness-components.md`.
- Create: `docs/harness-capabilities.md`.
- Create: `docs/harness-capabilities.toml`.
- Create: `docs/evidence-taxonomy.md`.
- Create: `docs/security-and-control.md`.
- Create: `docs/equipment-promotion.md`.
- Create: `templates/capability-card.md`.
- Create: `templates/interface-decision-record.md`.
- Create: `templates/skill/README.md`.
- Create: `templates/skill/SKILL.md`.
- Create: `templates/hook/README.md`.
- Create: `templates/hook/hook.ts`.
- Create: `templates/agents/README.md`.
- Create: `templates/agents/profile.toml`.
- Create: `templates/plugin/README.md`.
- Create: `templates/plugin/manifest.toml`.
- Create: `templates/script/README.md`.
- Create: `templates/script/validate-example.py`.
- Create: `templates/mcp/README.md`.
- Create: `templates/mcp/tool-spec.md`.
- Create: `templates/config/README.md`.
- Create: `templates/config/example.toml`.
- Create: `templates/security-review.md`.
- Create: `templates/context-budget-review.md`.
- Create: `examples/pr-review/capability-card.md`.
- Create: `examples/pr-review/interface-decision-record.md`.
- Create: `examples/pr-review/projected-components.md`.
- Create: `examples/docs-research/capability-card.md`.
- Create: `examples/docs-research/interface-decision-record.md`.
- Create: `examples/docs-research/projected-components.md`.
- Create: `examples/observability-investigation/capability-card.md`.
- Create: `examples/observability-investigation/interface-decision-record.md`.
- Create: `examples/observability-investigation/projected-components.md`.
- Create: `specs/agent-ops.md`.
- Create: `specs/periodic-actions.md`.
- Create: `specs/harness-capability-refresh.md`.
- Create: `tools/validate_forge_seed.py`.
- Create: `tests/__init__.py`.
- Create: `tests/test_validate_forge_seed.py`.

## Task 1: Seed Validation Tool Core

**Files:**
- Create: `tools/validate_forge_seed.py`
- Create: `tests/__init__.py`
- Create: `tests/test_validate_forge_seed.py`

- [x] **Step 1: Write failing tests for validator primitives**

Add `tests/test_validate_forge_seed.py` with these tests:

```python
import json
import tempfile
import textwrap
import unittest
from pathlib import Path

from tools.validate_forge_seed import (
    CheckResult,
    find_markdown_links,
    load_toml,
    render_human,
    validate_required_paths,
)


class ValidatorPrimitiveTests(unittest.TestCase):
    def test_validate_required_paths_reports_missing_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "README.md").write_text("# Demo\n", encoding="utf-8")

            results = validate_required_paths(root, ["README.md", "docs/missing.md"])

        self.assertEqual(
            results,
            [
                CheckResult(
                    name="required_path:README.md",
                    ok=True,
                    detail="exists",
                    path="README.md",
                ),
                CheckResult(
                    name="required_path:docs/missing.md",
                    ok=False,
                    detail="missing",
                    path="docs/missing.md",
                ),
            ],
        )

    def test_find_markdown_links_ignores_external_and_anchor_links(self):
        markdown = textwrap.dedent(
            """
            [local](docs/start.md)
            [anchor](#section)
            [external](https://example.com)
            [mail](mailto:agent@example.test)
            """
        )

        self.assertEqual(find_markdown_links(markdown), ["docs/start.md"])

    def test_find_markdown_links_ignores_fenced_code_blocks(self):
        fence = "`" * 3
        markdown = textwrap.dedent(
            f"""
            [real](docs/real.md)

            {fence}markdown
            [fixture](docs/missing-fixture.md)
            {fence}

               {fence}python
               [indented](docs/missing-indented.md)
               {fence}

            ~~~~
            [tilde](docs/missing-tilde.md)
            ~~~~
            """
        )

        self.assertEqual(find_markdown_links(markdown), ["docs/real.md"])

    def test_load_toml_returns_data(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "catalog.toml"
            path.write_text('[harness.codex]\nversion = "0.128.0"\n', encoding="utf-8")

            self.assertEqual(load_toml(path), {"harness": {"codex": {"version": "0.128.0"}}})

    def test_render_human_summarizes_pass_and_fail(self):
        output = render_human(
            [
                CheckResult("alpha", True, "ok", "README.md"),
                CheckResult("beta", False, "missing", "docs/beta.md"),
            ]
        )

        self.assertIn("PASS alpha README.md - ok", output)
        self.assertIn("FAIL beta docs/beta.md - missing", output)
        self.assertIn("1 failed, 1 passed", output)


if __name__ == "__main__":
    unittest.main()
```

- [x] **Step 2: Run tests to verify they fail**

Run:

```bash
python3.14 -m unittest tests/test_validate_forge_seed.py
```

Expected: FAIL or ERROR because `tools.validate_forge_seed` does not exist.

- [x] **Step 3: Implement validator primitives**

Create `tools/validate_forge_seed.py`:

```python
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
        "docs/prd/forge-seed.md",
        "docs/metasmith/source-projection.md",
        "docs/harness-capabilities.toml",
    ]
    return validate_required_paths(root, required_paths)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the Agent Armory Forge Seed.")
    parser.add_argument("--root", default=".", help="Repository root to validate.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args(argv)

    results = run(Path(args.root).resolve())
    output = render_json(results) if args.json else render_human(results)
    print(output)
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    sys.exit(main())
```

- [x] **Step 4: Run tests to verify they pass**

Run:

```bash
python3.14 -m unittest tests/test_validate_forge_seed.py
```

Expected: PASS.

- [x] **Step 5: Commit**

Run:

```bash
git add tools/validate_forge_seed.py tests/__init__.py tests/test_validate_forge_seed.py
git commit -m "test(forge): add seed validator primitives" -m "Co-authored-by: Codex <noreply@openai.com>"
```

## Task 2: Source Projection Register and Handoff Provenance

This task is superseded as final-tree guidance by the Source Disposition Ledger. The historical steps remain here to preserve the reviewed TDD path through the source-bearing checkpoint.

**Files:**
- Modify: `tools/validate_forge_seed.py`
- Modify: `tests/test_validate_forge_seed.py`
- Modify: `CONTEXT.md`
- Modify: `docs/prd/forge-seed.md`
- Modify: `docs/adr/0015-require-source-projection-register.md`
- Create: `docs/metasmith/source-projection.md`
- Validate existing archived handoff files under `docs/metasmith/handoff/2026-05-02/`.

- [x] **Step 1: Write failing tests for source projection validation**

Append to `tests/test_validate_forge_seed.py`:

```python
from tools.validate_forge_seed import (
    ACCEPTED_SOURCE_REQUIREMENTS,
    validate_source_handoff_provenance,
    validate_source_projection,
)


class SourceProjectionTests(unittest.TestCase):
    def write_register(self, root: Path, rows: list[str]) -> None:
        register = root / "docs/metasmith/source-projection.md"
        register.parent.mkdir(parents=True, exist_ok=True)
        register.write_text(
            textwrap.dedent(
                f"""
                # Source Projection Register

                | requirement_id | source_file | source_anchor | summary | disposition | target_path | deferment_reason | validation_status |
                | --- | --- | --- | --- | --- | --- | --- | --- |
                {chr(10).join(rows)}
                """
            ),
            encoding="utf-8",
        )

    def write_source_handoff_fixture(self, root: Path, omit: set[str] | None = None) -> None:
        omitted = omit or set()
        handoff = root / "docs/metasmith/handoff/2026-05-02"
        handoff.mkdir(parents=True, exist_ok=True)
        anchors_by_file: dict[str, list[str]] = {}
        for metadata in ACCEPTED_SOURCE_REQUIREMENTS.values():
            anchors_by_file.setdefault(metadata["source_file"], []).append(metadata["source_anchor"])
        for source_file, anchors in anchors_by_file.items():
            if source_file in omitted:
                continue
            (handoff / source_file).parent.mkdir(parents=True, exist_ok=True)
            (handoff / source_file).write_text(
                "\n".join(f"# {anchor}" for anchor in anchors) + "\n",
                encoding="utf-8",
            )

    def test_validate_source_projection_accepts_complete_inventory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            self.write_source_handoff_fixture(root)
            (root / "docs/ubiquitous-language.md").write_text("# Fixture\n", encoding="utf-8")
            rows = [
                f"| {requirement_id} | {metadata['source_file']} | {metadata['source_anchor']} | Summary | projected | docs/ubiquitous-language.md |  | planned |"
                for requirement_id, metadata in ACCEPTED_SOURCE_REQUIREMENTS.items()
            ]
            self.write_register(root, rows)

            results = validate_source_projection(root)

        self.assertTrue(all(result.ok for result in results), results)

    def test_validate_source_projection_rejects_symlinked_register(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            register = root / "docs/metasmith/source-projection.md"
            register.parent.mkdir(parents=True)
            outside = root / "outside-register.md"
            outside.write_text("# Source Projection Register\n", encoding="utf-8")
            register.symlink_to(outside)

            results = validate_source_projection(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    name="source_projection:register",
                    ok=False,
                    detail="register path contains symlink",
                    path="docs/metasmith/source-projection.md",
                )
            ],
        )

    def test_validate_source_projection_rejects_wrong_source_reference(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            self.write_source_handoff_fixture(root)
            (root / "docs/ubiquitous-language.md").write_text("# Fixture\n", encoding="utf-8")
            rows = [
                f"| {requirement_id} | {metadata['source_file']} | {metadata['source_anchor']} | Summary | projected | docs/ubiquitous-language.md |  | planned |"
                for requirement_id, metadata in ACCEPTED_SOURCE_REQUIREMENTS.items()
            ]
            rows[0] = rows[0].replace("00-metasmith-handoff-prompt.md", "wrong-source.md")
            self.write_register(root, rows)

            results = validate_source_projection(root)

        self.assertIn(
            CheckResult(
                name="source_projection:H001",
                ok=False,
                detail="source_file must be 00-metasmith-handoff-prompt.md",
                path="docs/metasmith/source-projection.md",
            ),
            results,
        )

    def test_validate_source_projection_rejects_missing_source_anchor(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            self.write_source_handoff_fixture(root)
            (root / "docs/metasmith/handoff/2026-05-02/00-metasmith-handoff-prompt.md").write_text(
                "# Different anchor\n",
                encoding="utf-8",
            )
            (root / "docs/ubiquitous-language.md").write_text("# Fixture\n", encoding="utf-8")
            rows = [
                f"| {requirement_id} | {metadata['source_file']} | {metadata['source_anchor']} | Summary | projected | docs/ubiquitous-language.md |  | planned |"
                for requirement_id, metadata in ACCEPTED_SOURCE_REQUIREMENTS.items()
            ]
            self.write_register(root, rows)

            results = validate_source_projection(root)

        self.assertIn(
            CheckResult(
                name="source_projection:H001",
                ok=False,
                detail="source_anchor not found in 00-metasmith-handoff-prompt.md",
                path="docs/metasmith/source-projection.md",
            ),
            results,
        )

    def test_validate_source_projection_rejects_missing_source_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            self.write_source_handoff_fixture(root, omit={"00-metasmith-handoff-prompt.md"})
            (root / "docs/ubiquitous-language.md").write_text("# Fixture\n", encoding="utf-8")
            rows = [
                f"| {requirement_id} | {metadata['source_file']} | {metadata['source_anchor']} | Summary | projected | docs/ubiquitous-language.md |  | planned |"
                for requirement_id, metadata in ACCEPTED_SOURCE_REQUIREMENTS.items()
            ]
            self.write_register(root, rows)

            results = validate_source_projection(root)

        self.assertIn(
            CheckResult(
                name="source_projection:H001",
                ok=False,
                detail="source_file missing: 00-metasmith-handoff-prompt.md",
                path="docs/metasmith/source-projection.md",
            ),
            results,
        )

    def test_validate_source_projection_rejects_symlinked_source_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_source_handoff_fixture(root)
            source = root / "docs/metasmith/handoff/2026-05-02/00-metasmith-handoff-prompt.md"
            source.unlink()
            outside = root / "outside-handoff.md"
            outside.write_text("# Your objective\n", encoding="utf-8")
            source.symlink_to(outside)
            (root / "docs/target.md").write_text("# Target\n", encoding="utf-8")
            self.write_register(
                root,
                [
                    "| H001 | 00-metasmith-handoff-prompt.md | Your objective | Summary | projected | docs/target.md |  | planned |"
                ],
            )

            results = validate_source_projection(root)

        self.assertIn(
            CheckResult(
                name="source_projection:H001",
                ok=False,
                detail="source_file invalid: 00-metasmith-handoff-prompt.md (manifest-listed file is a symlink)",
                path="docs/metasmith/source-projection.md",
            ),
            results,
        )

    def test_validate_source_projection_rejects_symlinked_handoff_root(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            handoff_parent = root / "docs/metasmith/handoff"
            handoff_parent.mkdir(parents=True)
            outside = root / "outside-handoff"
            outside.mkdir()
            (outside / "00-metasmith-handoff-prompt.md").write_text("# Your objective\n", encoding="utf-8")
            (handoff_parent / "2026-05-02").symlink_to(outside, target_is_directory=True)
            (root / "docs/target.md").write_text("# Target\n", encoding="utf-8")
            self.write_register(
                root,
                [
                    "| H001 | 00-metasmith-handoff-prompt.md | Your objective | Summary | projected | docs/target.md |  | planned |"
                ],
            )

            results = validate_source_projection(root)

        self.assertIn(
            CheckResult(
                name="source_projection:H001",
                ok=False,
                detail="source_file invalid: 00-metasmith-handoff-prompt.md (handoff directory path contains symlink)",
                path="docs/metasmith/source-projection.md",
            ),
            results,
        )

    def test_validate_source_projection_rejects_symlinked_projected_target(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_source_handoff_fixture(root)
            target = root / "docs/target.md"
            target.parent.mkdir(parents=True, exist_ok=True)
            outside = root / "outside-target.md"
            outside.write_text("# Target\n", encoding="utf-8")
            target.symlink_to(outside)
            rows = [
                f"| {requirement_id} | {metadata['source_file']} | {metadata['source_anchor']} | Summary | projected | docs/target.md |  | planned |"
                for requirement_id, metadata in ACCEPTED_SOURCE_REQUIREMENTS.items()
            ]
            self.write_register(root, rows)

            results = validate_source_projection(root)

        self.assertIn(
            CheckResult(
                name="source_projection:H001:target:docs/target.md",
                ok=False,
                detail="projected target invalid",
                path="docs/metasmith/source-projection.md",
            ),
            results,
        )

    def test_validate_source_projection_rejects_missing_projected_target(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_source_handoff_fixture(root)
            rows = [
                f"| {requirement_id} | {metadata['source_file']} | {metadata['source_anchor']} | Summary | projected | docs/missing.md |  | planned |"
                for requirement_id, metadata in ACCEPTED_SOURCE_REQUIREMENTS.items()
            ]
            self.write_register(root, rows)

            results = validate_source_projection(root)

        self.assertIn(
            CheckResult(
                name="source_projection:H001:target:docs/missing.md",
                ok=False,
                detail="projected target missing",
                path="docs/metasmith/source-projection.md",
            ),
            results,
        )

    def test_validate_source_projection_accepts_deferred_future_target_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            self.write_source_handoff_fixture(root)
            (root / "docs/ubiquitous-language.md").write_text("# Fixture\n", encoding="utf-8")
            rows = [
                f"| {requirement_id} | {metadata['source_file']} | {metadata['source_anchor']} | Summary | projected | docs/ubiquitous-language.md |  | planned |"
                for requirement_id, metadata in ACCEPTED_SOURCE_REQUIREMENTS.items()
            ]
            rows[0] = "| H001 | 00-metasmith-handoff-prompt.md | Your objective | Defer seed objective | deferred | specs/future-work.md | Deferred until follow-up. | planned |"
            self.write_register(root, rows)

            results = validate_source_projection(root)

        self.assertTrue(all(result.ok for result in results), results)

    def test_validate_source_projection_rejects_deferred_url_target(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_source_handoff_fixture(root)
            self.write_register(
                root,
                [
                    "| H001 | 00-metasmith-handoff-prompt.md | Your objective | Defer seed objective | deferred | file:///tmp/future.md | Deferred until follow-up. | planned |"
                ],
            )

            results = validate_source_projection(root)

        self.assertIn(
            CheckResult(
                name="source_projection:H001:target:file:///tmp/future.md",
                ok=False,
                detail="deferred target invalid",
                path="docs/metasmith/source-projection.md",
            ),
            results,
        )

    def test_validate_source_projection_rejects_deferred_parent_traversal_target(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_source_handoff_fixture(root)
            self.write_register(
                root,
                [
                    "| H001 | 00-metasmith-handoff-prompt.md | Your objective | Defer seed objective | deferred | ../future.md | Deferred until follow-up. | planned |"
                ],
            )

            results = validate_source_projection(root)

        self.assertIn(
            CheckResult(
                name="source_projection:H001:target:../future.md",
                ok=False,
                detail="deferred target invalid",
                path="docs/metasmith/source-projection.md",
            ),
            results,
        )

    def test_validate_source_projection_rejects_missing_accepted_requirement(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            self.write_source_handoff_fixture(root)
            (root / "docs/ubiquitous-language.md").write_text("# Fixture\n", encoding="utf-8")
            self.write_register(
                root,
                [
                    "| H001 | 00-metasmith-handoff-prompt.md | Required content | Ubiquitous language docs | projected | docs/ubiquitous-language.md |  | planned |"
                ],
            )

            results = validate_source_projection(root)

        self.assertTrue(
            any(
                result.name == "source_projection:coverage"
                and not result.ok
                and result.detail.startswith("missing accepted requirements: H002")
                for result in results
            ),
            results,
        )

    def test_validate_source_projection_rejects_unknown_requirement(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_register(
                root,
                [
                    "| H999 | 08-initial-smith-task-specs.md | Agent Ops | Unknown task | deferred | specs/future-work.md | Deferred until follow-up. | planned |"
                ],
            )

            results = validate_source_projection(root)

        self.assertIn(
            CheckResult(
                name="source_projection:coverage",
                ok=False,
                detail="unknown requirement ids: H999",
                path="docs/metasmith/source-projection.md",
            ),
            results,
        )

    def test_validate_source_projection_rejects_duplicate_requirement(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            self.write_source_handoff_fixture(root)
            (root / "docs/ubiquitous-language.md").write_text("# Fixture\n", encoding="utf-8")
            rows = [
                f"| {requirement_id} | {metadata['source_file']} | {metadata['source_anchor']} | Summary | projected | docs/ubiquitous-language.md |  | planned |"
                for requirement_id, metadata in ACCEPTED_SOURCE_REQUIREMENTS.items()
            ]
            rows.append(rows[0])
            self.write_register(root, rows)

            results = validate_source_projection(root)

        self.assertIn(
            CheckResult(
                name="source_projection:coverage",
                ok=False,
                detail="duplicate requirement ids: H001",
                path="docs/metasmith/source-projection.md",
            ),
            results,
        )

    def test_validate_source_projection_rejects_deferred_without_reason(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            register = root / "docs/metasmith/source-projection.md"
            register.parent.mkdir(parents=True)
            register.write_text(
                textwrap.dedent(
                    """
                    # Source Projection Register

                    | requirement_id | source_file | source_anchor | summary | disposition | target_path | deferment_reason | validation_status |
                    | --- | --- | --- | --- | --- | --- | --- | --- |
                    | H999 | 08-initial-smith-task-specs.md | Agent Ops | Implement Agent Ops | deferred |  |  | planned |
                    """
                ),
                encoding="utf-8",
            )

            results = validate_source_projection(root)

        self.assertIn(
            CheckResult(
                name="source_projection:H999",
                ok=False,
                detail="deferred requirement missing deferment_reason",
                path="docs/metasmith/source-projection.md",
            ),
            results,
        )

    def test_validate_source_projection_rejects_deferred_without_target(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_source_handoff_fixture(root)
            self.write_register(
                root,
                [
                    "| H001 | 00-metasmith-handoff-prompt.md | Your objective | Defer seed objective | deferred |  | Deferred until follow-up. | planned |"
                ],
            )

            results = validate_source_projection(root)

        self.assertIn(
            CheckResult(
                name="source_projection:H001",
                ok=False,
                detail="deferred requirement missing downstream target_path",
                path="docs/metasmith/source-projection.md",
            ),
            results,
        )

    def test_validate_source_handoff_provenance_checks_manifest_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            handoff = root / "docs/metasmith/handoff/2026-05-02"
            handoff.mkdir(parents=True)
            (handoff / "AGENTS.md").write_text(
                "# Handoff Provenance\n\nTreat the manifest-listed source files in this directory as provenance, not current operating instructions.\n",
                encoding="utf-8",
            )
            (handoff / "manifest.json").write_text(
                json.dumps({"files": ["README.md", "00-metasmith-handoff-prompt.md"]}),
                encoding="utf-8",
            )
            (handoff / "README.md").write_text("# Bundle\n", encoding="utf-8")

            results = validate_source_handoff_provenance(root)

        self.assertIn(
            CheckResult(
                name="source_handoff:file:00-metasmith-handoff-prompt.md",
                ok=False,
                detail="manifest-listed file missing",
                path="docs/metasmith/handoff/2026-05-02/00-metasmith-handoff-prompt.md",
            ),
            results,
        )

    def test_validate_source_handoff_provenance_rejects_invalid_manifest_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            handoff = root / "docs/metasmith/handoff/2026-05-02"
            handoff.mkdir(parents=True)
            (handoff / "AGENTS.md").write_text(
                "# Handoff Provenance\n\nTreat the manifest-listed source files in this directory as provenance, not current operating instructions.\n",
                encoding="utf-8",
            )
            (handoff / "manifest.json").write_text("not json", encoding="utf-8")

            results = validate_source_handoff_provenance(root)

        self.assertIn(
            CheckResult(
                name="source_handoff:manifest_json",
                ok=False,
                detail="manifest JSON invalid: Expecting value",
                path="docs/metasmith/handoff/2026-05-02/manifest.json",
            ),
            results,
        )

    def test_validate_source_handoff_provenance_rejects_non_object_manifest_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            handoff = root / "docs/metasmith/handoff/2026-05-02"
            handoff.mkdir(parents=True)
            (handoff / "AGENTS.md").write_text(
                "# Handoff Provenance\n\nTreat the manifest-listed source files in this directory as provenance, not current operating instructions.\n",
                encoding="utf-8",
            )
            (handoff / "manifest.json").write_text("[]", encoding="utf-8")

            results = validate_source_handoff_provenance(root)

        self.assertIn(
            CheckResult(
                name="source_handoff:manifest_json",
                ok=False,
                detail="manifest JSON must be an object",
                path="docs/metasmith/handoff/2026-05-02/manifest.json",
            ),
            results,
        )

    def test_validate_source_handoff_provenance_rejects_manifest_without_files_key(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            handoff = root / "docs/metasmith/handoff/2026-05-02"
            handoff.mkdir(parents=True)
            (handoff / "AGENTS.md").write_text(
                "# Handoff Provenance\n\nTreat the manifest-listed source files in this directory as provenance, not current operating instructions.\n",
                encoding="utf-8",
            )
            (handoff / "manifest.json").write_text(json.dumps({}), encoding="utf-8")

            results = validate_source_handoff_provenance(root)

        self.assertIn(
            CheckResult(
                name="source_handoff:manifest_files",
                ok=False,
                detail="manifest files must be a non-empty list",
                path="docs/metasmith/handoff/2026-05-02/manifest.json",
            ),
            results,
        )

    def test_validate_source_handoff_provenance_rejects_empty_manifest_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            handoff = root / "docs/metasmith/handoff/2026-05-02"
            handoff.mkdir(parents=True)
            (handoff / "AGENTS.md").write_text(
                "# Handoff Provenance\n\nTreat the manifest-listed source files in this directory as provenance, not current operating instructions.\n",
                encoding="utf-8",
            )
            (handoff / "manifest.json").write_text(json.dumps({"files": []}), encoding="utf-8")

            results = validate_source_handoff_provenance(root)

        self.assertIn(
            CheckResult(
                name="source_handoff:manifest_files",
                ok=False,
                detail="manifest files must be a non-empty list",
                path="docs/metasmith/handoff/2026-05-02/manifest.json",
            ),
            results,
        )

    def test_validate_source_handoff_provenance_rejects_null_manifest_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            handoff = root / "docs/metasmith/handoff/2026-05-02"
            handoff.mkdir(parents=True)
            (handoff / "AGENTS.md").write_text(
                "# Handoff Provenance\n\nTreat the manifest-listed source files in this directory as provenance, not current operating instructions.\n",
                encoding="utf-8",
            )
            (handoff / "manifest.json").write_text(json.dumps({"files": None}), encoding="utf-8")

            results = validate_source_handoff_provenance(root)

        self.assertIn(
            CheckResult(
                name="source_handoff:manifest_files",
                ok=False,
                detail="manifest files must be a non-empty list",
                path="docs/metasmith/handoff/2026-05-02/manifest.json",
            ),
            results,
        )

    def test_validate_source_handoff_provenance_rejects_string_manifest_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            handoff = root / "docs/metasmith/handoff/2026-05-02"
            handoff.mkdir(parents=True)
            (handoff / "AGENTS.md").write_text(
                "# Handoff Provenance\n\nTreat the manifest-listed source files in this directory as provenance, not current operating instructions.\n",
                encoding="utf-8",
            )
            (handoff / "manifest.json").write_text(json.dumps({"files": "README.md"}), encoding="utf-8")

            results = validate_source_handoff_provenance(root)

        self.assertIn(
            CheckResult(
                name="source_handoff:manifest_files",
                ok=False,
                detail="manifest files must be a non-empty list",
                path="docs/metasmith/handoff/2026-05-02/manifest.json",
            ),
            results,
        )

    def test_validate_source_handoff_provenance_rejects_manifest_missing_accepted_source(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_source_handoff_fixture(root)
            handoff = root / "docs/metasmith/handoff/2026-05-02"
            (handoff / "AGENTS.md").write_text(
                "# Handoff Provenance\n\nTreat the manifest-listed source files in this directory as provenance, not current operating instructions.\n",
                encoding="utf-8",
            )
            source_files = sorted({metadata["source_file"] for metadata in ACCEPTED_SOURCE_REQUIREMENTS.values()})
            source_files.remove("00-metasmith-handoff-prompt.md")
            (handoff / "manifest.json").write_text(json.dumps({"files": source_files}), encoding="utf-8")

            results = validate_source_handoff_provenance(root)

        self.assertIn(
            CheckResult(
                name="source_handoff:manifest_coverage",
                ok=False,
                detail="accepted source files missing from manifest: 00-metasmith-handoff-prompt.md",
                path="docs/metasmith/handoff/2026-05-02/manifest.json",
            ),
            results,
        )

    def test_validate_source_handoff_provenance_rejects_symlink_handoff_root(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            handoff_parent = root / "docs/metasmith/handoff"
            handoff_parent.mkdir(parents=True)
            outside = root / "outside-handoff"
            outside.mkdir()
            (outside / "AGENTS.md").write_text(
                "# Handoff Provenance\n\nTreat the manifest-listed source files in this directory as provenance, not current operating instructions.\n",
                encoding="utf-8",
            )
            (outside / "manifest.json").write_text(
                json.dumps({"files": ["00-metasmith-handoff-prompt.md"]}),
                encoding="utf-8",
            )
            (outside / "00-metasmith-handoff-prompt.md").write_text("# Your objective\n", encoding="utf-8")
            (handoff_parent / "2026-05-02").symlink_to(outside, target_is_directory=True)

            results = validate_source_handoff_provenance(root)

        self.assertIn(
            CheckResult(
                name="source_handoff:root",
                ok=False,
                detail="handoff directory path contains symlink",
                path="docs/metasmith/handoff/2026-05-02",
            ),
            results,
        )

    def test_validate_source_handoff_provenance_rejects_symlink_manifest(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            handoff = root / "docs/metasmith/handoff/2026-05-02"
            handoff.mkdir(parents=True)
            (handoff / "AGENTS.md").write_text(
                "# Handoff Provenance\n\nTreat the manifest-listed source files in this directory as provenance, not current operating instructions.\n",
                encoding="utf-8",
            )
            outside_manifest = root / "outside-manifest.json"
            outside_manifest.write_text(json.dumps({"files": []}), encoding="utf-8")
            (handoff / "manifest.json").symlink_to(outside_manifest)

            results = validate_source_handoff_provenance(root)

        self.assertIn(
            CheckResult(
                name="source_handoff:manifest_path",
                ok=False,
                detail="manifest path contains symlink",
                path="docs/metasmith/handoff/2026-05-02/manifest.json",
            ),
            results,
        )

    def test_validate_source_handoff_provenance_rejects_symlink_provenance_notice(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_source_handoff_fixture(root)
            handoff = root / "docs/metasmith/handoff/2026-05-02"
            source_files = sorted({metadata["source_file"] for metadata in ACCEPTED_SOURCE_REQUIREMENTS.values()})
            (handoff / "manifest.json").write_text(json.dumps({"files": source_files}), encoding="utf-8")
            outside_notice = root / "outside-AGENTS.md"
            outside_notice.write_text(
                "# Outside Instructions\n\nTreat this as current operating instructions.\n",
                encoding="utf-8",
            )
            (handoff / "AGENTS.md").symlink_to(outside_notice)

            results = validate_source_handoff_provenance(root)

        self.assertIn(
            CheckResult(
                name="source_handoff:provenance_notice_path",
                ok=False,
                detail="provenance notice path contains symlink",
                path="docs/metasmith/handoff/2026-05-02/AGENTS.md",
            ),
            results,
        )

    def test_validate_source_handoff_provenance_rejects_symlink_manifest_entry(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            handoff = root / "docs/metasmith/handoff/2026-05-02"
            handoff.mkdir(parents=True)
            (handoff / "AGENTS.md").write_text(
                "# Handoff Provenance\n\nTreat the manifest-listed source files in this directory as provenance, not current operating instructions.\n",
                encoding="utf-8",
            )
            outside = root / "outside-handoff.md"
            outside.write_text("# Outside bundle\n", encoding="utf-8")
            (handoff / "00-metasmith-handoff-prompt.md").symlink_to(outside)
            (handoff / "manifest.json").write_text(
                json.dumps({"files": ["00-metasmith-handoff-prompt.md"]}),
                encoding="utf-8",
            )

            results = validate_source_handoff_provenance(root)

        self.assertIn(
            CheckResult(
                name="source_handoff:file:00-metasmith-handoff-prompt.md",
                ok=False,
                detail="manifest-listed file is a symlink",
                path="docs/metasmith/handoff/2026-05-02/00-metasmith-handoff-prompt.md",
            ),
            results,
        )

    def test_validate_source_handoff_provenance_rejects_blank_manifest_entry(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            handoff = root / "docs/metasmith/handoff/2026-05-02"
            handoff.mkdir(parents=True)
            (handoff / "AGENTS.md").write_text(
                "# Handoff Provenance\n\nTreat the manifest-listed source files in this directory as provenance, not current operating instructions.\n",
                encoding="utf-8",
            )
            (handoff / "manifest.json").write_text(
                json.dumps({"files": [""]}),
                encoding="utf-8",
            )

            results = validate_source_handoff_provenance(root)

        self.assertIn(
            CheckResult(
                name="source_handoff:file:",
                ok=False,
                detail="manifest file path invalid",
                path="docs/metasmith/handoff/2026-05-02/manifest.json",
            ),
            results,
        )

    def test_validate_source_handoff_provenance_rejects_directory_manifest_entry(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            handoff = root / "docs/metasmith/handoff/2026-05-02"
            handoff.mkdir(parents=True)
            (handoff / "AGENTS.md").write_text(
                "# Handoff Provenance\n\nTreat the manifest-listed source files in this directory as provenance, not current operating instructions.\n",
                encoding="utf-8",
            )
            (handoff / "manifest.json").write_text(
                json.dumps({"files": ["."]}),
                encoding="utf-8",
            )

            results = validate_source_handoff_provenance(root)

        self.assertIn(
            CheckResult(
                name="source_handoff:file:.",
                ok=False,
                detail="manifest-listed file missing",
                path="docs/metasmith/handoff/2026-05-02/.",
            ),
            results,
        )

    def test_validate_source_handoff_provenance_rejects_manifest_traversal(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "README.md").write_text("# Outside bundle\n", encoding="utf-8")
            handoff = root / "docs/metasmith/handoff/2026-05-02"
            handoff.mkdir(parents=True)
            (handoff / "AGENTS.md").write_text(
                "# Handoff Provenance\n\nTreat the manifest-listed source files in this directory as provenance, not current operating instructions.\n",
                encoding="utf-8",
            )
            (handoff / "manifest.json").write_text(
                json.dumps({"files": ["../../../../README.md"]}),
                encoding="utf-8",
            )

            results = validate_source_handoff_provenance(root)

        self.assertIn(
            CheckResult(
                name="source_handoff:file:../../../../README.md",
                ok=False,
                detail="manifest file path invalid",
                path="docs/metasmith/handoff/2026-05-02/manifest.json",
            ),
            results,
        )

    def test_validate_source_handoff_provenance_rejects_manifest_url(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            handoff = root / "docs/metasmith/handoff/2026-05-02"
            handoff.mkdir(parents=True)
            (handoff / "AGENTS.md").write_text(
                "# Handoff Provenance\n\nTreat the manifest-listed source files in this directory as provenance, not current operating instructions.\n",
                encoding="utf-8",
            )
            (handoff / "manifest.json").write_text(
                json.dumps({"files": ["file:///tmp/handoff.md"]}),
                encoding="utf-8",
            )

            results = validate_source_handoff_provenance(root)

        self.assertIn(
            CheckResult(
                name="source_handoff:file:file:///tmp/handoff.md",
                ok=False,
                detail="manifest file path invalid",
                path="docs/metasmith/handoff/2026-05-02/manifest.json",
            ),
            results,
        )
```

- [x] **Step 2: Run tests to verify they fail**

Run:

```bash
python3.14 -m unittest tests/test_validate_forge_seed.py
```

Expected: ERROR because `validate_source_projection` and `validate_source_handoff_provenance` are missing.

- [x] **Step 3: Implement source projection validation**

Add to `tools/validate_forge_seed.py`:

```python
SOURCE_PROJECTION_PATH = "docs/metasmith/source-projection.md"
SOURCE_PROJECTION_FIELDS = [
    "requirement_id",
    "source_file",
    "source_anchor",
    "summary",
    "disposition",
    "target_path",
    "deferment_reason",
    "validation_status",
]

ACCEPTED_SOURCE_REQUIREMENTS = {
    "H001": {"source_file": "00-metasmith-handoff-prompt.md", "source_anchor": "Your objective"},
    "H002": {"source_file": "00-metasmith-handoff-prompt.md", "source_anchor": "Terms you must use"},
    "H003": {"source_file": "00-metasmith-handoff-prompt.md", "source_anchor": "Core principle"},
    "H004": {"source_file": "00-metasmith-handoff-prompt.md", "source_anchor": "Required repository shape"},
    "H005": {"source_file": "00-metasmith-handoff-prompt.md", "source_anchor": "1. Ubiquitous Language"},
    "H006": {"source_file": "00-metasmith-handoff-prompt.md", "source_anchor": "2. Evidence discipline"},
    "H007": {"source_file": "00-metasmith-handoff-prompt.md", "source_anchor": "3. Forge architecture"},
    "H008": {"source_file": "00-metasmith-handoff-prompt.md", "source_anchor": "4. Decision method"},
    "H009": {"source_file": "00-metasmith-handoff-prompt.md", "source_anchor": "5. Harness capability catalog"},
    "H010": {"source_file": "00-metasmith-handoff-prompt.md", "source_anchor": "6. Templates and examples"},
    "H011": {"source_file": "00-metasmith-handoff-prompt.md", "source_anchor": "7. Initial Smith task specs"},
    "H012": {"source_file": "00-metasmith-handoff-prompt.md", "source_anchor": "Acceptance criteria"},
    "H052": {"source_file": "00-metasmith-handoff-prompt.md", "source_anchor": "Constraints"},
    "H053": {"source_file": "00-metasmith-handoff-prompt.md", "source_anchor": "Final report"},
    "H013": {"source_file": "01-executive-brief.md", "source_anchor": "What the Forge must solve"},
    "H014": {"source_file": "01-executive-brief.md", "source_anchor": "Core decomposition"},
    "H015": {"source_file": "01-executive-brief.md", "source_anchor": "What the Metasmith should produce"},
    "H016": {"source_file": "02-ubiquitous-language.md", "source_anchor": "Agent Armory"},
    "H017": {"source_file": "02-ubiquitous-language.md", "source_anchor": "Relationship model"},
    "H018": {"source_file": "03-evidence-and-source-map.md", "source_anchor": "Evidence categories"},
    "H019": {"source_file": "03-evidence-and-source-map.md", "source_anchor": "Source hygiene rules"},
    "H020": {"source_file": "04-framework-architecture.md", "source_anchor": "Component responsibilities"},
    "H021": {"source_file": "04-framework-architecture.md", "source_anchor": "Context management architecture"},
    "H022": {"source_file": "04-framework-architecture.md", "source_anchor": "Security architecture"},
    "H023": {"source_file": "04-framework-architecture.md", "source_anchor": "Maintenance architecture"},
    "H024": {"source_file": "05-decision-method-and-runbook.md", "source_anchor": "Principle: least cognitive privilege"},
    "H025": {"source_file": "05-decision-method-and-runbook.md", "source_anchor": "Placement guide"},
    "H026": {"source_file": "05-decision-method-and-runbook.md", "source_anchor": "Decision tree"},
    "H027": {"source_file": "05-decision-method-and-runbook.md", "source_anchor": "Capability creation runbook"},
    "H028": {"source_file": "05-decision-method-and-runbook.md", "source_anchor": "Anti-patterns"},
    "H029": {"source_file": "06-harness-capability-catalog.md", "source_anchor": "Summary matrix"},
    "H030": {"source_file": "06-harness-capability-catalog.md", "source_anchor": "Periodic Actions projection order"},
    "H031": {"source_file": "06-harness-capability-catalog.md", "source_anchor": "Refresh requirement"},
    "H032": {"source_file": "07-equipment-templates-and-examples.md", "source_anchor": "Template: capability card"},
    "H033": {"source_file": "07-equipment-templates-and-examples.md", "source_anchor": "Template: interface decision record"},
    "H034": {"source_file": "07-equipment-templates-and-examples.md", "source_anchor": "Template: skill reference"},
    "H035": {"source_file": "07-equipment-templates-and-examples.md", "source_anchor": "Template: skill body"},
    "H036": {"source_file": "07-equipment-templates-and-examples.md", "source_anchor": "Template: hook"},
    "H037": {"source_file": "07-equipment-templates-and-examples.md", "source_anchor": "Template: Agent Profile"},
    "H038": {"source_file": "07-equipment-templates-and-examples.md", "source_anchor": "Template: Harness Plugin manifest"},
    "H039": {"source_file": "07-equipment-templates-and-examples.md", "source_anchor": "Template: deterministic script contract"},
    "H040": {"source_file": "07-equipment-templates-and-examples.md", "source_anchor": "Example: PR review"},
    "H041": {"source_file": "07-equipment-templates-and-examples.md", "source_anchor": "Template: MCP/tool definition notes"},
    "H042": {"source_file": "07-equipment-templates-and-examples.md", "source_anchor": "Template: config"},
    "H043": {"source_file": "07-equipment-templates-and-examples.md", "source_anchor": "Example: documentation search"},
    "H044": {"source_file": "07-equipment-templates-and-examples.md", "source_anchor": "Example: observability investigation"},
    "H045": {"source_file": "08-initial-smith-task-specs.md", "source_anchor": "Task 1: Agent Ops"},
    "H046": {"source_file": "08-initial-smith-task-specs.md", "source_anchor": "Task 2: Periodic Actions"},
    "H047": {"source_file": "08-initial-smith-task-specs.md", "source_anchor": "Task 3: Harness Capability Refresh"},
    "H048": {"source_file": "09-repository-seed-plan.md", "source_anchor": "Proposed initial structure"},
    "H049": {"source_file": "09-repository-seed-plan.md", "source_anchor": "README requirements"},
    "H050": {"source_file": "10-gap-resolution-and-design-notes.md", "source_anchor": "Key corrections"},
    "H051": {"source_file": "10-gap-resolution-and-design-notes.md", "source_anchor": "Remaining uncertainties"},
    "H054": {"source_file": "harness-capabilities.seed.toml", "source_anchor": "[harness.codex]"},
}

SOURCE_HANDOFF_DIR = "docs/metasmith/handoff/2026-05-02"
SOURCE_HANDOFF_MANIFEST = f"{SOURCE_HANDOFF_DIR}/manifest.json"
SOURCE_HANDOFF_PROVENANCE_NOTICE = f"{SOURCE_HANDOFF_DIR}/AGENTS.md"


def parse_markdown_table(markdown: str) -> list[dict[str, str]]:
    rows = [line.strip() for line in markdown.splitlines() if line.strip().startswith("|")]
    if len(rows) < 2:
        return []
    headers = [cell.strip() for cell in rows[0].strip("|").split("|")]
    data_rows = rows[2:]
    parsed: list[dict[str, str]] = []
    for row in data_rows:
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        parsed.append(dict(zip(headers, cells, strict=False)))
    return parsed


def invalid_repo_relative_target(target: str) -> bool:
    parsed = urlparse(target)
    return bool(parsed.scheme) or target.startswith("/") or ".." in Path(target).parts


def repo_relative_path_status(root: Path, relative_path: str, expected_kind: str) -> tuple[bool, str, Path]:
    if invalid_repo_relative_target(relative_path):
        return False, "path invalid", root / relative_path
    candidate = root / relative_path
    current = root
    for part in Path(relative_path).parts:
        current = current / part
        if current.is_symlink():
            return False, "path contains symlink", candidate
    try:
        root_resolved = root.resolve(strict=True)
        candidate_resolved = candidate.resolve(strict=True)
    except OSError:
        return False, "missing", candidate
    try:
        candidate_resolved.relative_to(root_resolved)
    except ValueError:
        return False, "path escapes repository root", candidate
    if expected_kind == "file" and not candidate.is_file():
        return False, "not a file", candidate
    if expected_kind == "directory" and not candidate.is_dir():
        return False, "not a directory", candidate
    return True, "exists", candidate


def repo_surface_status(root: Path, relative_path: str, label: str) -> tuple[bool, str, Path]:
    ok, detail, path = repo_relative_path_status(root, relative_path, "any")
    if ok:
        return ok, detail, path
    if detail == "path contains symlink":
        return False, f"{label} path contains symlink", path
    return False, f"{label} {detail}", path


def source_anchor_exists(path: Path, anchor: str) -> bool:
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("#") and stripped.lstrip("#").strip() == anchor:
            return True
        if stripped == anchor:
            return True
    return False


def handoff_root_status(root: Path) -> tuple[bool, str, Path]:
    ok, detail, path = repo_relative_path_status(root, SOURCE_HANDOFF_DIR, "directory")
    if ok:
        return ok, detail, path
    if detail == "path contains symlink":
        return False, "handoff directory path contains symlink", path
    if detail == "missing":
        return False, "handoff directory missing", path
    return False, f"handoff directory {detail}", path


def handoff_control_file_status(root: Path, relative_path: str, label: str) -> tuple[bool, str, Path]:
    ok, detail, path = repo_relative_path_status(root, relative_path, "file")
    if ok:
        return ok, detail, path
    if detail == "path contains symlink":
        return False, f"{label} path contains symlink", path
    if detail == "missing":
        return False, f"{label} missing", path
    return False, f"{label} {detail}", path


def handoff_file_status(root: Path, file_name: str) -> tuple[bool, str, Path]:
    root_ok, root_detail, handoff_root = handoff_root_status(root)
    candidate = handoff_root / file_name
    if not root_ok:
        return False, root_detail, candidate
    handoff_root_resolved = handoff_root.resolve(strict=True)
    current = handoff_root
    for part in Path(file_name).parts:
        current = current / part
        if current.is_symlink():
            return False, "manifest-listed file is a symlink", candidate
    try:
        candidate_resolved = candidate.resolve(strict=True)
    except OSError:
        return False, "manifest-listed file missing", candidate
    try:
        candidate_resolved.relative_to(handoff_root_resolved)
    except ValueError:
        return False, "manifest-listed file escapes handoff directory", candidate
    if not candidate.is_file():
        return False, "manifest-listed file missing", candidate
    return True, "exists", candidate


def validate_source_projection(root: Path) -> list[CheckResult]:
    register_ok, register_detail, path = repo_surface_status(root, SOURCE_PROJECTION_PATH, "register")
    if not register_ok:
        detail = "missing" if register_detail == "register missing" else register_detail
        return [CheckResult("source_projection:register", False, detail, SOURCE_PROJECTION_PATH)]
    rows = parse_markdown_table(path.read_text(encoding="utf-8"))
    results: list[CheckResult] = []
    if not rows:
        return [CheckResult("source_projection:rows", False, "no requirement rows", SOURCE_PROJECTION_PATH)]
    seen: dict[str, int] = {}
    for row in rows:
        requirement_id = row.get("requirement_id", "")
        seen[requirement_id] = seen.get(requirement_id, 0) + 1
        missing = [field for field in SOURCE_PROJECTION_FIELDS if field not in row]
        if missing:
            results.append(
                CheckResult(
                    name=f"source_projection:{requirement_id or 'unknown'}",
                    ok=False,
                    detail=f"missing fields: {', '.join(missing)}",
                    path=SOURCE_PROJECTION_PATH,
                )
            )
            continue
        expected = ACCEPTED_SOURCE_REQUIREMENTS.get(requirement_id)
        if expected:
            for field in ("source_file", "source_anchor"):
                if row[field] != expected[field]:
                    results.append(
                        CheckResult(
                            name=f"source_projection:{requirement_id}",
                            ok=False,
                            detail=f"{field} must be {expected[field]}",
                            path=SOURCE_PROJECTION_PATH,
                        )
                    )
            source_ok, source_detail, source_path = handoff_file_status(root, expected["source_file"])
            if not source_ok:
                detail = (
                    f"source_file missing: {expected['source_file']}"
                    if source_detail == "manifest-listed file missing"
                    else f"source_file invalid: {expected['source_file']} ({source_detail})"
                )
                results.append(
                    CheckResult(
                        name=f"source_projection:{requirement_id}",
                        ok=False,
                        detail=detail,
                        path=SOURCE_PROJECTION_PATH,
                    )
                )
            elif not source_anchor_exists(source_path, expected["source_anchor"]):
                results.append(
                    CheckResult(
                        name=f"source_projection:{requirement_id}",
                        ok=False,
                        detail=f"source_anchor not found in {expected['source_file']}",
                        path=SOURCE_PROJECTION_PATH,
                    )
                )
        disposition = row["disposition"]
        if disposition not in {"projected", "deferred"}:
            results.append(
                CheckResult(
                    name=f"source_projection:{requirement_id}",
                    ok=False,
                    detail="disposition must be projected or deferred",
                    path=SOURCE_PROJECTION_PATH,
                )
            )
        elif disposition == "projected":
            targets = [target.strip() for target in row["target_path"].split(",") if target.strip()]
            if not targets:
                results.append(
                    CheckResult(
                        name=f"source_projection:{requirement_id}",
                        ok=False,
                        detail="projected requirement missing target_path",
                        path=SOURCE_PROJECTION_PATH,
                    )
                )
            for target in targets:
                target_ok, target_detail, _ = repo_surface_status(root, target, "projected target")
                if not target_ok:
                    detail = (
                        "projected target missing"
                        if target_detail == "projected target missing"
                        else "projected target invalid"
                    )
                    results.append(
                        CheckResult(
                            name=f"source_projection:{requirement_id}:target:{target}",
                            ok=False,
                            detail=detail,
                            path=SOURCE_PROJECTION_PATH,
                        )
                    )
        elif disposition == "deferred":
            if not row["deferment_reason"]:
                results.append(
                    CheckResult(
                        name=f"source_projection:{requirement_id}",
                        ok=False,
                        detail="deferred requirement missing deferment_reason",
                        path=SOURCE_PROJECTION_PATH,
                    )
                )
            targets = [target.strip() for target in row["target_path"].split(",") if target.strip()]
            if not targets:
                results.append(
                    CheckResult(
                        name=f"source_projection:{requirement_id}",
                        ok=False,
                        detail="deferred requirement missing downstream target_path",
                        path=SOURCE_PROJECTION_PATH,
                    )
                )
            for target in targets:
                invalid = invalid_repo_relative_target(target)
                if invalid:
                    results.append(
                        CheckResult(
                            name=f"source_projection:{requirement_id}:target:{target}",
                            ok=False,
                            detail="deferred target invalid",
                            path=SOURCE_PROJECTION_PATH,
                        )
                    )
        if not any(result.name.startswith(f"source_projection:{requirement_id}") and not result.ok for result in results):
            results.append(
                CheckResult(
                    name=f"source_projection:{requirement_id}",
                    ok=True,
                    detail=disposition,
                    path=SOURCE_PROJECTION_PATH,
                )
            )
    expected_ids = set(ACCEPTED_SOURCE_REQUIREMENTS)
    seen_ids = {requirement_id for requirement_id in seen if requirement_id}
    missing_ids = sorted(expected_ids - seen_ids)
    extra_ids = sorted(seen_ids - expected_ids)
    duplicate_ids = sorted(requirement_id for requirement_id, count in seen.items() if count > 1)
    if missing_ids:
        results.append(
            CheckResult(
                name="source_projection:coverage",
                ok=False,
                detail=f"missing accepted requirements: {', '.join(missing_ids)}",
                path=SOURCE_PROJECTION_PATH,
            )
        )
    if extra_ids:
        results.append(
            CheckResult(
                name="source_projection:coverage",
                ok=False,
                detail=f"unknown requirement ids: {', '.join(extra_ids)}",
                path=SOURCE_PROJECTION_PATH,
            )
        )
    if duplicate_ids:
        results.append(
            CheckResult(
                name="source_projection:coverage",
                ok=False,
                detail=f"duplicate requirement ids: {', '.join(duplicate_ids)}",
                path=SOURCE_PROJECTION_PATH,
            )
        )
    return results


def validate_source_handoff_provenance(root: Path) -> list[CheckResult]:
    manifest_path = root / SOURCE_HANDOFF_MANIFEST
    notice_path = root / SOURCE_HANDOFF_PROVENANCE_NOTICE
    results = validate_required_paths(root, [SOURCE_HANDOFF_MANIFEST, SOURCE_HANDOFF_PROVENANCE_NOTICE])
    root_ok, root_detail, _ = handoff_root_status(root)
    if not root_ok:
        results.append(CheckResult("source_handoff:root", False, root_detail, SOURCE_HANDOFF_DIR))
        return results
    manifest_ok, manifest_detail, manifest_path = handoff_control_file_status(root, SOURCE_HANDOFF_MANIFEST, "manifest")
    if not manifest_ok:
        if manifest_detail != "manifest missing":
            results.append(CheckResult("source_handoff:manifest_path", False, manifest_detail, SOURCE_HANDOFF_MANIFEST))
        return results
    notice_ok, notice_detail, notice_path = handoff_control_file_status(
        root,
        SOURCE_HANDOFF_PROVENANCE_NOTICE,
        "provenance notice",
    )
    if not notice_ok and notice_detail != "provenance notice missing":
        results.append(
            CheckResult("source_handoff:provenance_notice_path", False, notice_detail, SOURCE_HANDOFF_PROVENANCE_NOTICE)
        )
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        results.append(
            CheckResult(
                name="source_handoff:manifest_json",
                ok=False,
                detail=f"manifest JSON invalid: {error.msg}",
                path=SOURCE_HANDOFF_MANIFEST,
            )
        )
        return results
    if not isinstance(manifest, dict):
        results.append(
            CheckResult(
                name="source_handoff:manifest_json",
                ok=False,
                detail="manifest JSON must be an object",
                path=SOURCE_HANDOFF_MANIFEST,
            )
        )
        return results
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        results.append(
            CheckResult(
                name="source_handoff:manifest_files",
                ok=False,
                detail="manifest files must be a non-empty list",
                path=SOURCE_HANDOFF_MANIFEST,
            )
        )
        return results
    manifest_files: set[str] = set()
    for file_name in files:
        if not isinstance(file_name, str) or not file_name.strip() or invalid_repo_relative_target(file_name):
            results.append(
                CheckResult(
                    name=f"source_handoff:file:{file_name}",
                    ok=False,
                    detail="manifest file path invalid",
                    path=SOURCE_HANDOFF_MANIFEST,
                )
            )
            continue
        manifest_files.add(file_name)
        path = f"{SOURCE_HANDOFF_DIR}/{file_name}"
        ok, detail, _ = handoff_file_status(root, file_name)
        results.append(
            CheckResult(
                name=f"source_handoff:file:{file_name}",
                ok=ok,
                detail=detail,
                path=path,
            )
        )
    expected_source_files = {metadata["source_file"] for metadata in ACCEPTED_SOURCE_REQUIREMENTS.values()}
    missing_source_files = sorted(expected_source_files - manifest_files)
    if missing_source_files:
        results.append(
            CheckResult(
                name="source_handoff:manifest_coverage",
                ok=False,
                detail=f"accepted source files missing from manifest: {', '.join(missing_source_files)}",
                path=SOURCE_HANDOFF_MANIFEST,
            )
        )
    if notice_ok:
        notice = notice_path.read_text(encoding="utf-8")
        expected_notice = "provenance, not current operating instructions."
        results.append(
            CheckResult(
                name="source_handoff:provenance_notice",
                ok=expected_notice in notice,
                detail="present" if expected_notice in notice else "missing archive instruction boundary",
                path=SOURCE_HANDOFF_PROVENANCE_NOTICE,
            )
        )
    return results
```

Update `run()` to include `validate_source_handoff_provenance(root)` and `validate_source_projection(root)`.

- [x] **Step 4: Create the Source Projection Register**

Create `docs/metasmith/source-projection.md` with this shape. The table must include exactly one row for every id in `ACCEPTED_SOURCE_REQUIREMENTS`; do not stop at the examples below.

```markdown
# Source Projection Register

This register maps accepted Source Handoff requirements to canonical Forge Seed surfaces or explicit deferments.

| requirement_id | source_file | source_anchor | summary | disposition | target_path | deferment_reason | validation_status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H001 | 00-metasmith-handoff-prompt.md | Your objective | Produce the Forge Seed as canonical docs, templates, examples, specs, and validation surfaces. | projected | docs/prd/forge-seed.md |  | planned |
| H002 | 00-metasmith-handoff-prompt.md | Terms you must use | Establish the core Forge vocabulary. | projected | docs/ubiquitous-language.md |  | planned |
| H003 | 00-metasmith-handoff-prompt.md | Core principle | Preserve least cognitive privilege as the Forge's central design rule. | projected | docs/agent-equipment-forge.md |  | planned |
| ... | ... | ... | ... | ... | ... | ... | ... |
```

Projection target guidance:

- `target_path` uses comma-separated repo-relative paths for projected requirements. Absolute paths, URLs, and parent traversal are invalid.
- Forge architecture, component model, context, security, and maintenance requirements project to canonical docs under `docs/`.
- Decision method and Smith runbook requirements project to `docs/smith-runbook.md` and `docs/interface-decision-guide.md`.
- Harness fact requirements project to `docs/harness-capabilities.md`, `docs/harness-capabilities.toml`, and `specs/harness-capability-refresh.md`.
- The archived structured seed `harness-capabilities.seed.toml` must have an explicit projection row into the refreshed TOML catalog.
- Templates and examples requirements project to `templates/` and `examples/`.
- Agent Ops, Periodic Actions, and Harness Capability Refresh implementation requirements project to `specs/`.
- Remaining uncertainties may be `deferred`, but every deferred row must have a concrete reason and downstream `target_path` for the follow-up surface or tracking note.

- [x] **Step 5: Run tests and validator**

Run:

```bash
python3.14 -m unittest tests/test_validate_forge_seed.py
python3.14 tools/validate_forge_seed.py
```

Expected: tests PASS. The full validator may still FAIL for seed surfaces and projected targets not yet created.

- [x] **Step 6: Commit**

Run:

```bash
git add CONTEXT.md docs/adr/0015-require-source-projection-register.md docs/prd/forge-seed.md docs/plans/2026-05-03-forge-seed.md tools/validate_forge_seed.py tests/test_validate_forge_seed.py docs/metasmith/source-projection.md
git commit -m "feat(forge): validate source projection register" -m "Co-authored-by: Codex <noreply@openai.com>"
```

## Task 3: Preloaded and Human Forge Conveyors

**Files:**
- Modify: `AGENTS.md`
- Modify: `README.md`
- Modify: `tools/validate_forge_seed.py`
- Modify: `tests/test_validate_forge_seed.py`

- [x] **Step 1: Write failing tests for routing links**

Add tests that create fixture `AGENTS.md` and `README.md` files, then assert validator failures when required links are absent:

```python
from tools.validate_forge_seed import validate_forge_routes, validate_markdown_links


class ForgeRouteTests(unittest.TestCase):
    def test_validate_forge_routes_requires_agent_and_human_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "AGENTS.md").write_text("# AGENTS\n", encoding="utf-8")
            (root / "README.md").write_text("# README\n", encoding="utf-8")

            results = validate_forge_routes(root)

        self.assertIn(
            CheckResult("forge_route:agent", False, "missing Forge Conveyor", "AGENTS.md"),
            results,
        )
        self.assertIn(
            CheckResult("forge_route:human", False, "missing Forge Tour", "README.md"),
            results,
        )

    def test_validate_forge_routes_requires_all_preloaded_links(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "AGENTS.md").write_text(
                textwrap.dedent(
                    """
                    # AGENTS

                    ## Forge Conveyor

                    - `docs/agent-equipment-forge.md`
                    - `docs/smith-runbook.md`
                    - `docs/harness-capabilities.md`
                    - `templates/`
                    - `examples/`
                    - `specs/`
                    """
                ),
                encoding="utf-8",
            )
            (root / "README.md").write_text(
                "## Forge\n\nStart with [Forge Tour](docs/forge-tour.md).\n",
                encoding="utf-8",
            )

            results = validate_forge_routes(root)

        self.assertIn(
            CheckResult(
                "forge_route:agent:docs/interface-decision-guide.md",
                False,
                "missing required preloaded route",
                "AGENTS.md",
            ),
            results,
        )

    def test_validate_forge_routes_rejects_unresolved_route_targets(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            (root / "templates").mkdir()
            (root / "examples").mkdir()
            (root / "specs").mkdir()
            for path in [
                "docs/agent-equipment-forge.md",
                "docs/smith-runbook.md",
                "docs/interface-decision-guide.md",
            ]:
                (root / path).write_text("# Fixture\n", encoding="utf-8")
            (root / "AGENTS.md").write_text(
                textwrap.dedent(
                    """
                    # AGENTS

                    ## Forge Conveyor

                    - `docs/agent-equipment-forge.md`
                    - `docs/smith-runbook.md`
                    - `docs/interface-decision-guide.md`
                    - `docs/harness-capabilities.md`
                    - `templates/`
                    - `examples/`
                    - `specs/`
                    """
                ),
                encoding="utf-8",
            )
            (root / "README.md").write_text(
                "## Forge\n\nStart with [Forge Tour](docs/forge-tour.md).\n",
                encoding="utf-8",
            )

            results = validate_forge_routes(root)

        self.assertIn(
            CheckResult(
                "forge_route:target:docs/harness-capabilities.md",
                False,
                "route target missing",
                "AGENTS.md",
            ),
            results,
        )


class MarkdownLinkTests(unittest.TestCase):
    def test_validate_markdown_links_rejects_broken_relative_link(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            (root / "docs/start.md").write_text("[missing](missing.md)\n", encoding="utf-8")

            results = validate_markdown_links(root)

        self.assertIn(
            CheckResult(
                "markdown_link:docs/start.md:missing.md",
                False,
                "target missing",
                "docs/start.md",
            ),
            results,
        )

    def test_validate_markdown_links_accepts_anchor_stripped_target(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            (root / "docs/start.md").write_text("[next](next.md#section)\n", encoding="utf-8")
            (root / "docs/next.md").write_text("# Next\n", encoding="utf-8")

            results = validate_markdown_links(root)

        self.assertTrue(all(result.ok for result in results), results)

    def test_validate_markdown_links_checks_nested_policy_docs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs/adr").mkdir(parents=True)
            (root / "docs/adr/0001-demo.md").write_text("[missing](../missing.md)\n", encoding="utf-8")

            results = validate_markdown_links(root)

        self.assertIn(
            CheckResult(
                "markdown_link:docs/adr/0001-demo.md:../missing.md",
                False,
                "target missing",
                "docs/adr/0001-demo.md",
            ),
            results,
        )
```

- [x] **Step 2: Run tests to verify they fail**

Run:

```bash
python3.14 -m unittest tests/test_validate_forge_seed.py
```

Expected: ERROR because `validate_forge_routes` and `validate_markdown_links` are missing.

- [x] **Step 3: Implement route validation**

Add `validate_forge_routes(root: Path)` that checks:

- `AGENTS.md` contains `## Forge Conveyor`.
- `AGENTS.md` links to `docs/agent-equipment-forge.md`, `docs/smith-runbook.md`, `docs/interface-decision-guide.md`, `docs/harness-capabilities.md`, `templates/`, `examples/`, and `specs/`.
- `README.md` contains `## Forge`.
- `README.md` links to `docs/agent-equipment-forge.md` with a real Markdown link in the Forge section.
- Every local Markdown or directory target named in the `AGENTS.md` Forge Conveyor and `README.md` Forge Tour resolves from the repository root. Backticked path strings count as route targets for agent-facing docs; Markdown links are also accepted.
- Route target checks must run after the route text checks, so early tasks can distinguish "route missing" from "target not created yet".

Add `validate_markdown_links(root: Path)` that checks all repository Markdown files for broken local Markdown links:

- Include root docs, canonical docs, nested docs under `docs/adr/`, `docs/prd/`, `docs/plans/`, `docs/agents/`, security docs, templates, examples, and specs.
- Exclude `docs/metasmith/handoff/2026-05-02/` because archived handoff links are provenance.
- Ignore external URLs, `mailto:`, and pure anchors.
- Strip anchors from local targets before resolving paths.
- Resolve relative links from the source file's parent directory.

Update `run()` to include route validation and Markdown link validation.

- [x] **Step 4: Update root routing docs**

In `AGENTS.md`, add:

```markdown
## Forge Conveyor

Smiths creating or modifying Agent Equipment should start with:

- `docs/agent-equipment-forge.md` for the Forge overview.
- `docs/smith-runbook.md` for the equipment creation workflow.
- `docs/interface-decision-guide.md` for choosing skills, MCP/tools, hooks, Agent Profiles, plugins, scripts, docs, and config.
- `docs/harness-capabilities.md` before making harness-specific claims.
- `templates/` for seed templates.
- `examples/` for annotated Forge Examples.
- `specs/` for downstream Smith specs.
```

In `README.md`, add a concise human-facing `## Forge` section that says:

```markdown
## Forge

The first public shape of this repository is the Agent Equipment Forge: a way to decide what kind of equipment an agent needs, where that equipment should live, and how to keep harness-specific claims source-backed.

Start with [docs/agent-equipment-forge.md](docs/agent-equipment-forge.md).
```

- [x] **Step 5: Run tests and validator**

Run:

```bash
python3.14 -m unittest tests/test_validate_forge_seed.py
python3.14 tools/validate_forge_seed.py
```

Expected: route tests PASS; validator may still FAIL for seed surfaces not yet created.

- [x] **Step 6: Commit**

Run:

```bash
git add AGENTS.md README.md tools/validate_forge_seed.py tests/test_validate_forge_seed.py
git commit -m "docs(forge): add canonical reading paths" -m "Co-authored-by: Codex <noreply@openai.com>"
```

## Task 4: Forge Canon

**Files:**
- Create: `docs/ubiquitous-language.md`
- Create: `docs/agent-equipment-forge.md`
- Create: `docs/smith-runbook.md`
- Create: `docs/forgewright-runbook.md`
- Create: `docs/interface-decision-guide.md`
- Create: `docs/harness-components.md`
- Create: `docs/evidence-taxonomy.md`
- Create: `docs/security-and-control.md`
- Create: `docs/equipment-promotion.md`

- [x] **Step 1: Write failing canonical doc validation tests**

Extend `tests/test_validate_forge_seed.py` to assert `run(root)` fails when:

- any canonical doc path is missing from a fixture root,
- a canonical doc omits `Status: Forge Seed`,
- a canonical doc omits one of its required sections.

- [x] **Step 2: Run tests to verify they fail**

Run:

```bash
python3.14 -m unittest tests/test_validate_forge_seed.py
```

Expected: FAIL because canonical doc paths and content are not all checked or not present.

- [x] **Step 3: Update required path and content validation**

Update `run()` required paths to include every canonical doc path listed for this task.

Add `validate_canonical_docs(root: Path)` so `run()` checks:

- each canonical document contains `Status: Forge Seed` near the top,
- each canonical document contains the required sections listed below,
- missing sections report the document path and section name.

- [x] **Step 4: Create canonical docs**

Each document must include `Status: Forge Seed` near the top.

Required sections:

- `docs/ubiquitous-language.md`: Language, Relationships, Precision rules.
- `docs/agent-equipment-forge.md`: Purpose, Least cognitive privilege, Component model, Context management, Security, Maintenance.
- `docs/smith-runbook.md`: Capability card, Interface decision record, Docs/config/scripts/hooks/skills/agents/plugins, Pressure Scenario Validation, Equipment Promotion Path, Closeout.
- `docs/forgewright-runbook.md`: Source handoff preservation, decision projection, Review Until Clean, Harness Fact Refresh, Issue Projection, downstream Smith specs.
- `docs/interface-decision-guide.md`: Decision tree and placement guide.
- `docs/harness-components.md`: Skills, MCP/tools, hooks, Agent Profiles, Harness Plugins, scripts, local docs, config.
- `docs/evidence-taxonomy.md`: documentation-supported, source-supported, implementation inference, practitioner wisdom, hypothesis, source hygiene.
- `docs/security-and-control.md`: least privilege, mutation gates, secrets, hooks, MCP/tool side effects, examples caveat.
- `docs/equipment-promotion.md`: states `example`, `specified`, `planned`, `implemented`, `validated`, `published`, entry/exit criteria.

- [x] **Step 5: Run validation**

Run:

```bash
python3.14 -m unittest tests/test_validate_forge_seed.py
python3.14 tools/validate_forge_seed.py
```

Expected: canonical doc path and content checks PASS; later template/example/spec/catalog checks may still FAIL.

- [x] **Step 6: Commit**

Run:

```bash
git add docs/ubiquitous-language.md docs/agent-equipment-forge.md docs/smith-runbook.md docs/forgewright-runbook.md docs/interface-decision-guide.md docs/harness-components.md docs/evidence-taxonomy.md docs/security-and-control.md docs/equipment-promotion.md tools/validate_forge_seed.py tests/test_validate_forge_seed.py
git commit -m "docs(forge): add forge canon" -m "Co-authored-by: Codex <noreply@openai.com>"
```

## Task 5: Harness Capability Catalog Refresh

**Files:**
- Create: `docs/harness-capabilities.md`
- Create: `docs/harness-capabilities.toml`
- Modify: `tools/validate_forge_seed.py`
- Modify: `tests/test_validate_forge_seed.py`

- [x] **Step 1: Write failing catalog validation tests**

Add tests that validate required TOML fields for each harness:

```python
from tools.validate_forge_seed import REQUIRED_HARNESSES, validate_harness_catalog


class HarnessCatalogTests(unittest.TestCase):
    def test_validate_harness_catalog_requires_evidence_metadata(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            catalog = root / "docs/harness-capabilities.toml"
            catalog.parent.mkdir(parents=True)
            entries = []
            for harness_id in REQUIRED_HARNESSES:
                entries.append(
                    textwrap.dedent(
                        f"""
                        [harness.{harness_id}]
                        display_name = "{harness_id}"
                        sources = [
                          {{ url = "https://example.com/{harness_id}", kind = "first_party", claim_scope = "docs" }},
                        ]
                        evidence = "documentation-supported"
                        checked_version = "source-documented"
                        version_basis = "official release or docs page"
                        uncertainty = "Fixture uncertainty."
                        components = ["skills"]
                        scheduling = "manual"
                        limitations = "Fixture limitation."
                        refresh_notes = "Fixture refresh note."
                        local_observations = []
                        """
                    )
                )
            catalog.write_text(
                'checked_at = "2026-05-03T00:00:00-04:00"\n\n' + "\n".join(entries),
                encoding="utf-8",
            )

            results = validate_harness_catalog(root)

        self.assertTrue(all(result.ok for result in results), results)

    def test_validate_harness_catalog_rejects_missing_required_harness(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            catalog = root / "docs/harness-capabilities.toml"
            catalog.parent.mkdir(parents=True)
            catalog.write_text(
                textwrap.dedent(
                    """
                    checked_at = "2026-05-03T00:00:00-04:00"

                    [harness.codex]
                    display_name = "Codex"
                    sources = [
                      { url = "https://github.com/openai/codex/releases", kind = "first_party", claim_scope = "releases" },
                    ]
                    evidence = "documentation-supported"
                    checked_version = "0.128.0"
                    version_basis = "GitHub releases"
                    uncertainty = "Verify installed CLI separately."
                    components = ["skills", "mcp", "hooks"]
                    scheduling = "manual"
                    limitations = "Fixture limitation."
                    refresh_notes = "Fixture refresh note."
                    local_observations = []
                    """
                ),
                encoding="utf-8",
            )

            results = validate_harness_catalog(root)

        self.assertIn(
            CheckResult(
                name="harness_catalog:coverage",
                ok=False,
                detail="missing required harnesses: claude_code, cursor, hermes_agent, opencode, openclaw",
                path="docs/harness-capabilities.toml",
            ),
            results,
        )
```

Add table-driven companion failing tests for every validation branch:

- missing global `checked_at`,
- unknown harness ids,
- missing required scalar fields: `display_name`, `evidence`, `uncertainty`, `scheduling`, `limitations`, `refresh_notes`, and `local_observations`,
- empty `sources`,
- missing source `url`, `kind`, or `claim_scope`,
- invalid source URL schemes,
- invalid source `kind`,
- invalid evidence category,
- missing both `checked_version` and `version_basis`,
- empty `components`,
- a `sources` entry with `kind = "third_party_fallback"` whose fallback status is not called out in `uncertainty` or `refresh_notes`,
- a `sources` entry with `kind = "local_observation"` instead of a separate `local_observations` entry.

- [x] **Step 2: Run tests to verify they fail**

Run:

```bash
python3.14 -m unittest tests/test_validate_forge_seed.py
```

Expected: ERROR because `validate_harness_catalog` is missing.

- [x] **Step 3: Refresh harness facts**

Use Firecrawl or equivalent web retrieval to refresh first-party evidence for:

- Codex
- OpenClaw
- Hermes Agent
- Claude Code
- Cursor
- OpenCode

Preferred source types:

- official docs,
- official changelogs,
- official release pages,
- first-party source repositories.

Use third-party metadata only when first-party version evidence is unavailable or inconsistent, and label it as fallback.

- [x] **Step 4: Implement catalog validation**

`validate_harness_catalog(root)` must check each harness entry has:

- required harness set: `codex`, `openclaw`, `hermes_agent`, `claude_code`, `cursor`, `opencode`,
- global `checked_at`,
- `display_name`
- non-empty structured `sources` entries with `url`, `kind`, and `claim_scope`,
- source entry `url` using `http://` or `https://`,
- source entry `kind` in `first_party`, `third_party_fallback`,
- `evidence` with an allowed category from `docs/evidence-taxonomy.md`,
- `checked_version` or `version_basis`
- `uncertainty`
- non-empty `components`
- `scheduling`
- `limitations`
- `refresh_notes`
- `local_observations` as a separate list, even when empty

The validator must also reject:

- unknown harness ids,
- duplicate or missing required harnesses,
- empty source lists,
- third-party fallback evidence that is not labeled in `uncertainty` or `refresh_notes`,
- local CLI observations mixed into first-party source claims instead of recorded as separate observation notes.

Update `run()` to include catalog validation.

- [x] **Step 5: Create refreshed catalog docs**

Create `docs/harness-capabilities.toml` and `docs/harness-capabilities.md`.

Required harnesses:

- Codex
- OpenClaw
- Hermes Agent
- Claude Code
- Cursor
- OpenCode

Each entry must include checked-at date, version or version basis, source URLs, evidence level, supported component types, scheduling mechanisms, limitations, uncertainty, and refresh notes.

- [x] **Step 6: Run validation**

Run:

```bash
python3.14 -m unittest tests/test_validate_forge_seed.py
python3.14 tools/validate_forge_seed.py
```

Expected: catalog tests PASS; validator may still FAIL for templates/examples/specs not yet created.

- [x] **Step 7: Commit**

Run:

```bash
git add docs/harness-capabilities.md docs/harness-capabilities.toml tools/validate_forge_seed.py tests/test_validate_forge_seed.py
git commit -m "docs(forge): refresh harness capability catalog" -m "Co-authored-by: Codex <noreply@openai.com>"
```

## Task 6: Templates

**Files:**
- Create every `templates/` path listed in the File Structure section.
- Modify: `tools/validate_forge_seed.py`
- Modify: `tests/test_validate_forge_seed.py`

- [x] **Step 1: Write failing template path and content tests**

Add tests that require every template path in the File Structure section. Also add tests that fail when:

- a root template file omits `Status: Template`,
- a template README omits Purpose, Required fields, Optional fields, Common mistakes, or Validation expectations.
- `templates/skill/SKILL.md` omits Status, Use when, Do not use when, Preflight, Procedure, Output contract, Failure handling, or Safety and policy notes,
- `templates/hook/hook.ts` omits side-effect classification, approval behavior, failure handling, and a non-empty exported hook contract,
- `templates/hook/hook.ts` does not bind `hookContract` and `handle()` at module top level,
- `templates/hook/hook.ts` does not require exact canonical contract values, full approval-gated side-effect approval behavior, fail-closed failure handling, and a handler-level fallback `return { allow: false, reason: "<literal>" }`,
- `templates/hook/hook.ts` accepts fail-open, non-literal, side-effectful, nested, computed, accessor, method, spread, duplicate, comment/regex/template-literal-masked decision shapes, missing literal reasons, missing malformed-event guards, or side-effectful module load, signatures, or branch conditions,
- `templates/agents/profile.toml` omits identity, mission, tools, typed tool allow/deny lists, permissions, read-only permission mode, and model/config placeholders,
- `templates/agents/profile.toml` omits canonical approval-gated labels or uses non-list/noncanonical approval labels,
- `templates/plugin/manifest.toml` omits plugin name, components, permissions, ownership/source, and version,
- `templates/plugin/manifest.toml` omits canonical approval-gated labels, external-disclosure approval, or a non-empty source field,
- `templates/script/validate-example.py` omits a plain module-level CLI entry point, deterministic exit-code contract, final guarded `raise SystemExit(main())`, stable `main` binding immediately before the guard, side-effect-safe script/class/main bodies, rejection of authority-bearing imports and network-capable APIs, exact import-shape validation, a narrow allowlist for benign call and expression shapes, rejection of delegated callable arguments, rejection of keyword-unpacking call shapes, or rejection of reserved call-name rebinding through assignments, imports, synchronous declarations, and asynchronous declarations,
- `templates/mcp/tool-spec.md` omits read/write classification, input schema, output schema, auth source, side effects, approval requirements, rate limits, pagination, rollback/cleanup, failure modes, or prose process-execution classification in the read/write classification section,
- `templates/config/example.toml` omits ownership, autonomy, enabled state, and review/approval placeholders,
- `templates/config/example.toml` allows continuation or initiative defaults, enables equipment by default, omits review/security/doc closeout flags, or omits canonical approval-gated labels,
- root safety templates omit visible, section-scoped external-disclosure prompts or visible capability promotion state in the template preamble.

- [x] **Step 2: Run tests to verify they fail**

Run:

```bash
python3.14 -m unittest tests/test_validate_forge_seed.py
```

Expected: FAIL for missing template paths or content checks.

- [x] **Step 3: Create templates**

Each template README must include:

- Purpose
- Required fields
- Optional fields
- Common mistakes
- Validation expectations

Each root template file must include `Status: Template`.

Update `tools/validate_forge_seed.py` with `validate_templates(root: Path)` so `run()` checks every required template path and template content rule from this task, including nested template bodies.

- [x] **Step 4: Run validation**

Run:

```bash
python3.14 -m unittest tests/test_validate_forge_seed.py
python3.14 tools/validate_forge_seed.py
```

Expected: template path and content checks PASS; examples/spec checks may still FAIL.

- [x] **Step 5: Commit**

Run:

```bash
git add templates tools/validate_forge_seed.py tests/test_validate_forge_seed.py
git commit -m "docs(templates): add Forge Seed templates" -m "Co-authored-by: Codex <noreply@openai.com>"
```

## Task 7: Forge Examples

**Files:**
- Create every `examples/` path listed in the File Structure section.
- Modify: `AGENTS.md`
- Modify: `docs/closeout/forge-seed-source-disposition.md`
- Modify: `docs/plans/2026-05-03-forge-seed.md`
- Modify: `tools/validate_forge_seed.py`
- Modify: `tests/test_validate_forge_seed.py`

- [x] **Step 1: Write failing example validation tests**

Add tests that require each example directory to contain:

- `capability-card.md`
- `interface-decision-record.md`
- `projected-components.md`

The tests must also check each example file includes `Promotion state: example`.

- [x] **Step 2: Run tests to verify they fail**

Run:

```bash
python3.14 -m unittest tests/test_validate_forge_seed.py
```

Expected: FAIL for missing example paths and promotion states.

- [x] **Step 3: Create examples**

Create PR review, docs research, and observability investigation examples. Each example must:

- declare `Promotion state: example`,
- say it is not Published Agent Equipment,
- trace from capability card to interface decision record to projected components,
- avoid claiming installability or production readiness.

- [x] **Step 4: Run validation**

Run:

```bash
python3.14 -m unittest tests/test_validate_forge_seed.py
python3.14 tools/validate_forge_seed.py
```

Expected: example checks PASS; specs may still FAIL.

- [x] **Step 5: Commit**

Run:

```bash
git add AGENTS.md docs/closeout/forge-seed-source-disposition.md docs/plans/2026-05-03-forge-seed.md examples tools/validate_forge_seed.py tests/test_validate_forge_seed.py
git commit -m "docs(examples): add Forge method examples" -m "Co-authored-by: Codex <noreply@openai.com>"
```

## Task 8: Equipment Blueprints

**Files:**
- Create: `specs/agent-ops.md`
- Create: `specs/periodic-actions.md`
- Create: `specs/harness-capability-refresh.md`
- Modify: `docs/closeout/forge-seed-source-disposition.md`
- Modify: `docs/plans/2026-05-03-forge-seed.md`
- Modify: `tools/validate_forge_seed.py`
- Modify: `tests/test_validate_forge_seed.py`

- [x] **Step 1: Write failing spec validation tests**

Add tests that require each spec to include:

- `Promotion state: specified`
- Purpose
- User stories
- Acceptance criteria
- Harness projections or harness-specific starting points
- Non-goals

- [x] **Step 2: Run tests to verify they fail**

Run:

```bash
python3.14 -m unittest tests/test_validate_forge_seed.py
```

Expected: FAIL for missing specs and required sections.

- [x] **Step 3: Create specs**

Create specs from `docs/metasmith/handoff/2026-05-02/08-initial-smith-task-specs.md`.

`specs/agent-ops.md` must include:

- promotion state `specified`,
- durable TOML config requirements,
- autonomy levels,
- owner/runbook config,
- safe defaults,
- policy enforcement behavior,
- harness projections for Codex, OpenClaw, Hermes Agent, Claude Code, Cursor, and OpenCode.

`specs/periodic-actions.md` must include:

- promotion state `specified`,
- first-session install prompt,
- list/view/install/uninstall/trigger-now/edit-period behavior,
- mechanism selection order,
- suggested `.agent-ops/` storage,
- harness-specific starting points.

`specs/harness-capability-refresh.md` must include:

- promotion state `specified`,
- required harnesses,
- required tracked fields,
- change-response issue behavior,
- fallback issue-candidate path,
- weekly starting cadence,
- prioritization order.

- [x] **Step 4: Run validation**

Run:

```bash
python3.14 -m unittest tests/test_validate_forge_seed.py
python3.14 tools/validate_forge_seed.py
```

Expected: spec checks PASS. The full repository validator may still report the final closeout surfaces from Task 9 as missing until that task lands.

- [x] **Step 5: Commit**

Run:

```bash
git add docs/closeout/forge-seed-source-disposition.md docs/plans/2026-05-03-forge-seed.md specs tools/validate_forge_seed.py tests/test_validate_forge_seed.py
git commit -m "docs(specs): add initial smith task specs" -m "Co-authored-by: Codex <noreply@openai.com>"
```

## Task 9: Final Validation, Security Closeout, Documentation Closeout, Review, and Issue Projection

**Files:**
- Modify: `docs/closeout/forge-seed-source-disposition.md`
- Modify: `AGENTS.md`
- Modify: `CONTEXT.md`
- Modify: `docs/prd/forge-seed.md`
- Modify: `docs/smith-runbook.md`
- Modify: `docs/forgewright-runbook.md`
- Create or modify: `docs/security/threat-model.md`
- Create or modify: `docs/security/forge-seed-closeout.md`
- Create or modify: `docs/closeout/forge-seed-documentation.md`
- Create or modify: `docs/story-closeout.md`
- Modify: affected agent-facing or human-facing docs as documentation closeout requires.
- Modify: any canonical docs, templates, examples, specs, or validation files needed by final review.

- [x] **Step 1: Write failing tests for the Repository Threat Model surface**

Extend `tests/test_validate_forge_seed.py` with failing tests that require:

- `docs/security/threat-model.md` exists,
- the threat model contains sections for assets, trust boundaries, attacker-controlled inputs, invariants, assumptions, and high-impact failure modes,
- the threat model is linked or referenced from `docs/security-and-control.md` or another canonical security surface.

Run:

```bash
python3.14 -m unittest tests/test_validate_forge_seed.py
```

Expected: FAIL because the threat model surface or validator checks are missing.

- [x] **Step 2: Create the Repository Threat Model and validator**

Use Codex Security threat-model workflow to create or update `docs/security/threat-model.md` as the persistent Repository Threat Model for Agent Armory.

Update `tools/validate_forge_seed.py` so `run()` validates the threat model requirements from Step 1.

- [x] **Step 2a: Write failing tests for the completed documentation closeout summary**

Extend `tests/test_validate_forge_seed.py` with failing tests that require `docs/closeout/forge-seed-documentation.md` to exist and contain these sections:

- scope of inspected docs,
- docs changed,
- docs unchanged with rationale,
- stale-language cleanup result,
- established precedents added or updated,
- review cycles and latest clean review,
- residual documentation risk.

Run:

```bash
python3.14 -m unittest tests/test_validate_forge_seed.py
```

Expected: FAIL because the completed documentation closeout summary is not populated yet.

- [x] **Step 3: Perform Change Set Documentation Closeout**

Completed: documentation inventory, stale-language cleanup, closeout draft,
Repository Threat Model linkage, Agent Profile template terminology cleanup, and
Smith-to-Forgewright Tooling Request docs have landed in the
worktree. `docs/closeout/forge-seed-documentation.md` records
`Status: Completed Closeout` and is the source of truth for the latest clean
documentation closeout review.

Inspect every agent-facing and human-facing doc that the Forge Seed could plausibly affect:

- `README.md`,
- `AGENTS.md`,
- `CONTEXT.md`,
- `docs/agents/*.md`,
- Forge Canon,
- `docs/security/*.md`,
- `docs/closeout/*.md`,
- `docs/prd/forge-seed.md`,
- `docs/adr/*.md`,
- `docs/plans/*.md`,
- `specs/*.md`,
- `templates/**/*.md`,
- `examples/**/*.md`.

For each doc, either update it or record why no change is needed in the closeout summary. Check for:

- stale initial-state language that says no structure, concepts, or precedents are established,
- missing or inaccurate mentions of Forge Seed deliverables when the doc's audience should see them,
- agent-facing policy that belongs in `AGENTS.md`, `docs/agents/`, or triggered workflow docs rather than human-facing README prose,
- human-facing docs that expose maintainer-only or agent-only machinery without a reader need,
- unresolved ambiguities that should still reserve judgment rather than overstate the Seed's precedent.

Record documentation closeout evidence in `docs/closeout/forge-seed-documentation.md` with these fields:

- scope of inspected docs,
- docs changed,
- docs unchanged with rationale,
- stale-language cleanup result,
- established precedents added or updated,
- review cycles and latest clean review,
- residual documentation risk.

Apply the appropriate doc-writing guidance during edits:

- agent-facing docs: honing-agent-facing-docs and writing-skills guidance,
- human-facing docs: honing-human-facing-docs and documentation-writer guidance,
- all prose: writing-clearly-and-concisely guidance.

Update `tools/validate_forge_seed.py` so `run()` validates the completed documentation closeout summary requirements from Step 2a.

Run:

```bash
python3.14 -m unittest tests/test_validate_forge_seed.py
python3.14 tools/validate_forge_seed.py
```

Expected: documentation closeout structure and evidence checks are populated.
Before Step 4 records a clean review, the full repository validator is expected
to remain red on `docs/closeout/forge-seed-documentation.md` status and
latest-clean-review fields.

- [x] **Step 4: Ralph-review documentation closeout**

Dispatch an xhigh reviewer for documentation closeout. Give the reviewer the updated docs, `docs/closeout/forge-seed-documentation.md`, and the applicable guidance from honing-agent-facing-docs, honing-human-facing-docs, documentation-writer, writing-clearly-and-concisely, and writing-skills when skill or agent-facing policy is involved.

Require review for:

- audience fit,
- policy placement,
- stale initial-state language,
- missing or overstated deliverable mentions,
- lost information,
- link flow,
- clear and concise prose.

Repeat until the latest documentation closeout review has no findings.

- [x] **Step 5: Write failing tests for the completed security closeout summary**

Extend `tests/test_validate_forge_seed.py` with failing tests that require `docs/security/forge-seed-closeout.md` to contain:

- scan scope,
- commands,
- scan artifact disposition,
- report disposition,
- findings disposition,
- hardening changes,
- re-validation status,
- deferred-risk tracking.

Run:

```bash
python3.14 -m unittest tests/test_validate_forge_seed.py
```

Expected: FAIL because the completed security closeout summary is not populated yet.

- [x] **Step 6: Perform Codex Security scan and hardening**

Use Codex Security workflows before the Forge Seed is considered merge-ready:

1. Run Codex Security's phase sequence against the Seed change set: threat modeling, finding discovery, validation when candidates or workflow rules require it, attack-path analysis when validation leaves reportable candidates or workflow rules require it, and final report assembly.
2. Scope the scan to the full merge-base-to-working-tree diff, including committed changes, staged changes, unstaged changes, and untracked intended files. Capture untracked files with `git ls-files --others --exclude-standard` and include their contents in the scan context, or stage all intended files before scanning. The final scan target must include `docs/closeout/forge-seed-documentation.md`, hardening changes, and review fixes that have not yet been committed. Keep the Repository Threat Model repository-scoped.
3. Classify every scan artifact by durability before commit or external projection. Record the scan scope, commands, scan artifact disposition, report disposition, findings dispositions, hardening changes, re-validation status, and deferred-risk tracking in `docs/security/forge-seed-closeout.md`. Do not commit or externally project raw instance-scoped scratch artifacts unless a later policy explicitly makes them durable repo artifacts in a neutral project path with scope, review status, and staleness boundaries.
4. Fix reportable findings, suppress false positives with evidence, or escalate deferment requests to the human operator with risk rationale and tracking issue.
5. After hardening changes, rerun or update the applicable Codex Security phases so the final security report and closeout summary describe the current repo state. At minimum, rerun validation and final report assembly for fixed findings; rerun finding discovery when the fix changes trust boundaries, side effects, or exposed inputs.
6. Update `tools/validate_forge_seed.py` so `run()` validates the completed security closeout summary requirements from Step 5.

- [x] **Step 6a: Define story closeout order and interdependency rules**

Create `docs/story-closeout.md` as the canonical Story Closeout process. It must define:

- Story Closeout as the story-level gate;
- Change Set Security Closeout and Change Set Documentation Closeout as subordinate gates;
- gate order from validation through security, documentation, projection drafts, Cross-Boundary Coherence review, Story Quality review, final validation, projection publication, and final publication actions;
- rerun rules for security, documentation, validation, PRD/spec/plan scope, and issue/PR projection changes;
- recursion boundaries and bookkeeping-only updates;
- completion criteria.

Wire the process through `AGENTS.md`, `CONTEXT.md`, `docs/smith-runbook.md`, `docs/forgewright-runbook.md`, `docs/prd/forge-seed.md`, `tools/validate_forge_seed.py`, and `tests/test_validate_forge_seed.py`.

Run:

```bash
python3.14 -m unittest tests.test_validate_forge_seed.CanonicalDocTests.test_validate_canonical_docs_requires_story_closeout_doc
python3.14 -m unittest tests/test_validate_forge_seed.py
python3.14 tools/validate_forge_seed.py
git diff --check
```

Expected: the targeted test fails before the validator and doc are updated, then passes with the full test suite and validator after the closeout process is wired.

- [x] **Step 6b: Refresh security and documentation closeout after closeout-process changes**

Defining `docs/story-closeout.md` changes agent-facing policy, documentation closeout claims, validator behavior, and the final closeout order. Treat that as a substantive upstream change:

1. Rerun or update the Codex Security scan so `docs/security/forge-seed-closeout.md` describes the current final diff, including `docs/story-closeout.md`, Story Closeout wiring, validator changes, tests, closeout documents, and untracked intended files.
2. Update `docs/security/forge-seed-closeout.md` with the current scan artifact disposition, report disposition, findings disposition, phase applicability, hardening changes, and re-validation counts.
3. Update `docs/closeout/forge-seed-documentation.md` for Story Closeout, the refreshed security closeout, and any closeout-process review fixes.
4. Run a narrow xhigh documentation closeout review for the updated security docs, closeout docs, Story Closeout process, and referenced agent-facing docs using the same doc-writing guidance as Step 4.

After the security closeout summary is populated and any hardening changes are complete, rerun:

```bash
python3.14 -m unittest
python3.14 tools/validate_forge_seed.py
python3.14 tools/validate_forge_seed.py --json
git diff --check
```

Ralph Review Cycle 52 verified the Cycle 51 fixes and found no remaining
Step 6b closeout-process issues.

- [x] **Step 6c: Prepare projection drafts for closeout review**

Before Cross-Boundary Coherence review, prepare the projection surfaces that the reviewer must check:

- a draft Published PRD Issue body for `docs/prd/forge-seed.md`, including the intended issue action and all fields listed in Step 11;
- a draft PR body or explicit note that PR creation is intentionally paused after branch push in this session;
- any release or handoff summary needed for the active closeout, or an explicit non-applicability note;
- a pending-projection rationale if an external surface cannot be drafted yet.

Store the draft in the plan, a closeout note, or another neutral project surface if it must be reviewable before publication. If the draft is intentionally kept outside committed files, include it in the reviewer context and record where it was reviewed.

- [x] **Step 7: Ralph-review closeout coherence and quality**

Dispatch an xhigh reviewer with the full merge-base-to-working-tree diff, including committed changes, staged changes, unstaged changes, and untracked intended files. Capture untracked files with `git ls-files --others --exclude-standard` and include their contents in the review context, or stage all intended files before review. Require review for:

1. Cross-Boundary Coherence Ralph Review:
   - PRD/spec/plan/implementation agreement,
   - source-disposition completeness,
   - AGENTS/README boundary,
   - harness evidence quality,
   - validation coverage,
   - templates/examples/spec promotion states,
   - downstream-equipment non-goals,
   - documentation closeout evidence and latest clean documentation closeout review,
   - security threat model and closeout evidence,
   - Codex Security findings disposition,
   - prepared issue/PR projection drafts or pending-projection rationale,
   - release/handoff draft surface consistency.

2. Story Quality Ralph Review:
   - confirmation that Intent Model Refresh ran before downstream closeout gates,
   - general and specific DX,
   - general and specific UX,
   - code quality,
   - clean architecture and cohesive module boundaries,
   - robustness against unspecified situations, interactions, user personas, and attack vectors,
   - mitigations implemented or planned for pathological dev/ops cycles observed in prior sessions,
   - coherent and plausibly realizable strategic vision,
   - direct or indirect alignment of current and planned work toward that vision,
   - alignment between Effective Intent actually imposed by ADRs, PRDs, specs, plans, acceptance criteria, review dispositions, and other declarations, and the agent's refreshed evidence-backed model of Underlying Intent after Cross-Boundary Coherence has made Effective Intent legible,
   - escalation of any non-dismissible likelihood of Effective Intent and Underlying Intent misalignment unless observable evidence supports realigning and reprojecting the affected declarations beyond reasonable doubt,
   - treatment of internal-state hypotheses as reasons to ask sharper questions, not as evidence that can justify unilateral realignment.

Expected: latest review cycle has no findings.

Clean closeout review cycles:

- Source-retirement and Projection Consistency Ralph Review Cycle 74 found no
  findings.
- Cross-Boundary Coherence Ralph Review Cycle 75 found no findings.
- Story Quality Ralph Review Cycle 76 found no findings and raised no
  intent-alignment question.

- [x] **Step 8: Apply fixes and rerun validation**

If review finds issues, fix them, rerun:

```bash
python3.14 -m unittest
python3.14 tools/validate_forge_seed.py
python3.14 tools/validate_forge_seed.py --json
git diff --check
```

Repeat review until clean.

After clean Cross-Boundary Coherence and Story Quality review cycles are
recorded in the projection draft, rerun:

```bash
python3.14 tools/validate_forge_seed.py --final-closeout
```

Expected: PASS. This strict final-closeout mode rejects unresolved story-review
placeholders and host-local or scratch artifact paths in external projection
drafts.

If review fixes affect security policy, side effects, exposed inputs, trust boundaries, MCP/tool behavior, hooks, executable code, or the threat model, rerun or update the applicable Codex Security phases and `docs/security/forge-seed-closeout.md` before the next review cycle.
If review fixes affect agent-facing or human-facing docs, rerun documentation closeout review with the applicable doc-writing guidance before the next full Forge Seed review cycle.
If review fixes affect PRD, spec, or plan scope, rerun the affected source-disposition, acceptance-criteria, and Cross-Boundary Coherence checks before the next review cycle.
If review fixes affect issue/PR projection drafts, release drafts, or handoff drafts, rerun projection consistency checks and include the corrected draft in the next Cross-Boundary Coherence review cycle.
If final validation or publication-readiness checks change evidence carried by a projection surface, update the draft before publishing and rerun projection consistency checks.

- [x] **Step 9: Commit final adjustments**

Run:

```bash
git add .gitignore README.md AGENTS.md CONTEXT.md docs templates examples specs tools tests
git commit -m "feat(forge): implement forge seed" -m "Co-authored-by: Codex <noreply@openai.com>"
```

If no changes remain after prior task commits, skip this commit and record that the branch is clean.

The final evidence update records the clean closeout review cycles and final
validation state before branch push. No further implementation changes are
planned before Step 10.

- [ ] **Step 10: Push branch and pause point**

After the final commit and validation, run the strict final closeout check and
push the Seed-completed branch:

```bash
python3.14 tools/validate_forge_seed.py --final-closeout
```

```bash
git push -u origin forge-seed
```

Pause the session after the branch is pushed and before PR creation. Report the
pushed branch, validation state, and whether the Published PRD Issue has been
created or remains a reviewed draft.

The operator has requested a side quest at this point. Do not create the PR
before the operator resumes or explicitly redirects this session.

- [ ] **Step 11: Issue Projection**

Use GitHub MCP or `gh` to create or update the Published PRD Issue for `docs/prd/forge-seed.md`.

Issue Projection is an external projection action and should use a pushed branch
or pushed commit reference. If the session pauses immediately after branch push,
leave `docs/closeout/forge-seed-projection-drafts.md` as the reviewed
projection draft and keep Issue Projection pending until work resumes.

The issue body must include:

- PRD title,
- status,
- link or branch/path reference to `docs/prd/forge-seed.md`,
- success criteria,
- implementation summary,
- validation commands and results,
- security closeout summary, including threat model path, report disposition, findings disposition, and deferred-risk tracking,
- documentation closeout summary, including affected docs inspected, material updates, and review result,
- Cross-Boundary Coherence and Story Quality review results,
- current commit SHA,
- note that repo draft remains the detailed review artifact while the issue is the tracking surface.

Immediately before writing to the issue tracker, capture the projected SHA:

```bash
git rev-parse HEAD
```

Use that SHA in the issue body. If GitHub issue creation is unavailable, update `docs/closeout/forge-seed-projection-drafts.md` or a neutral closeout note with `Issue Projection pending`, the reason, and the attempted projection SHA captured immediately before the fallback note. Then rerun validation, Ralph-review that repo-file adjustment, and commit it before closeout.

After creating or updating the Published PRD Issue, verify the published issue body matches the reviewed projection draft and the projected SHA. If the published issue differs materially from the reviewed draft, correct the issue and run a narrow Cross-Boundary Coherence review for the corrected projection surface.

After any fallback commit, rerun:

```bash
git rev-parse HEAD
```

Report that post-fallback final SHA only in external closeout surfaces, such as the final response, PR body, or a later issue update. Do not require a committed file to contain the SHA of the commit that contains that file.

- [ ] **Step 12: Rollback and recovery paths**

- If final review or security closeout finds a blocking flaw, keep the branch open, fix forward in the worktree, rerun validation and applicable security phases, and restart Ralph review.
- If Issue Projection targets the wrong issue or publishes stale content, update the issue with a correction that names the superseded SHA and current SHA; if a repo fallback note was committed, amend it with the correction in a new commit.
- Do not rewrite public history or force-push to hide a failed projection or security finding. Preserve the audit trail and fix forward unless the human operator explicitly requests a destructive history operation.

- [ ] **Step 13: Verify branch closeout state**

Run:

```bash
git status --short --branch
```

Expected: branch is clean after final commit or documented issue-projection fallback commit.

## Post-Seed Follow-Ups

These notes are deferred follow-ups. They are not Forge Seed acceptance
criteria and should not be promoted into `AGENTS.md`, `README.md`, PRD success
criteria, or Forge Canon until the corresponding post-Seed task is
actively designed.

### Post-Seed Skill Migration

After the initial Forge Seed is merged, migrate the operator's current
engineering workflow skills into repo-local Agent Equipment so local repo use,
Smith references, and future equipment bundles do not depend on global user
installation state.

Before bulk import, design the repository structure and promotion policy for
imported skills. Preserve source/provenance and licensing context, identify
global-installation assumptions, and classify each migrated skill as an example,
candidate, internal repo workflow, or publishable/bundleable equipment.

Before importing the operator's current equipment, run a dedicated engineering
story for the ingestion pipeline itself. Start with a `grill-with-docs` session
to resolve ambiguities with the operator and produce any warranted ADRs, then
proceed through the full engineering flow: PRD, specs, implementation plan, TDD,
SDD, security analysis, documentation review, Ralph review, projection, and
closeout.

Scope that pipeline as generic reusable Agent Equipment. The operator's
immediate import source is mostly skills, but the pipeline must support any kind
of equipment and must be usable in other compatible harnesses and repositories,
not only in this repository.

Before planning imports item by item, inspect the candidate source set and the
target repository's existing equipment as one system. Catalog group relations:
overlap, integration points, conflicts, implicit dependencies, indirect
relationships, containment or inclusion relationships such as plugin contents,
and candidate bundles that should be planned or reviewed together. When the best
planning granularity is uncertain, escalate to the operator before committing to
per-item or group-level import planning.

Treat source materials as evidence about the source's intended capability, not
as authority over the user's current Underlying Intent or the final equipment
form. They are instructive or advisory on concrete techniques and details, and
only suggestive on names, structure, and phrasing. Critically evaluate each
piece or cohesive bundle according to the criteria a Smith would use to build
the intended capability. If the source-projected capability appears to diverge
from the agent's current model of Underlying Intent, resolve that ambiguity with
the operator.

Design the ingestion UX and configuration model for progressive policy choice.
The importer should offer best-practice defaults while allowing the invoking user
to choose different ingestion policies for a source, bundle, function, facet, or
aspect when useful. The goal is to render the best possible equipment from the
available material under the selected policy, not merely to copy source files.

Handle externally sourced or upstream-maintained materials explicitly. Preserve
provenance, licensing context, update channels, and local adaptation choices.
For each material or bundle, support strategies such as ingesting as-is,
dropping/rejecting it, wrapping it, extending it, adding modification hooks,
overlaying or forking it, or rebuilding from captured intent. Account for cases
where upstream material is useful but misaligned with this repository's
standards, and escalate when the strategy depends on operator preference rather
than established project policy.

### Side-Thread Hand-Back Workflow

After the Forge Seed, specify the Agent Ops workflow for side conversations
that inspect, advise, or make narrow operator-requested edits while a main worker
owns the active change set.

The workflow should define the default non-mutating side-thread boundary, the
conditions for narrow side-thread edits, and the hand-back note contract. A
hand-back note should record provenance, operator intent, files touched, review
and validation implications, and commit guidance. The main worker remains
responsible for integration, validation, review, and commit/PR handling.

### Portable Agentic Engineering Workflow Equipment

After the Forge Seed, process the side-thread workflow reflection handoff at
`docs/follow-ups/portable-agentic-engineering-workflow-equipment.md`
into rigorously engineered Agent Equipment.

Begin with handoff ingestion and a `grill-with-docs` loop. The grill loop should
challenge terminology, scope, portability, ceremony, and placement against the
then-current `CONTEXT.md`, Forge Canon, existing templates, and Agent Ops
policy before drafting requirements.

If the Post-Seed Skill Migration or Side-Thread Hand-Back Workflow tasks have
already landed, ingest their outputs as source material. Treat their repo-local
skills, provenance notes, side-thread contracts, and progressive-disclosure
routes as evidence to reconcile rather than decisions to bypass.

Also ingest the linked
[Seed Closeout Addendum](../closeout/forge-seed-workflow-lessons.md).
It is the current capture for workflow lessons that emerged after the original
handoff was written, including subagent review availability, closeout-gate
ordering, projection drafts versus external publication, security and
documentation evidence freshness, review recursion, process-validation
semantics, and plan-state hygiene.

Keep the addendum current through full Forge Seed completion. For this
capture, full completion means the Seed branch has been pushed, the PR lifecycle
has run, the Seed has been merged, external issue and PR surfaces have been
reconciled with repo-file projections, merge cleanup has completed or been
explicitly deferred, and the final hand-back records that state. The capture
window includes final local validation, closeout reviews, issue projection,
branch push, PR creation, PR review orchestration, merge, and merge cleanup. If
those steps expose new insights, guardrails, policies, techniques, failure
modes, or harness-specific constraints, append them before treating the Seed as
fully closed.

If the operator explicitly holds or cancels the Seed instead of merging it,
continue capture through the hold or cancellation hand-back. Record the
unmerged state directly; do not describe it as full Seed completion.

If the Seed work pauses after branch push and before PR creation, the pause
handoff must say that the addendum remains open through the PR, merge, and
cleanup lifecycle. The later post-Seed story should ingest the captured
material, not defer first capture until its own start.

The resulting story should define the minimal repo equipment needed for future
agents to recover the agent-operated engineering workflow from repo files alone.
It should consider always-loaded policy, triggered skills, templates,
validators, examples, security closeout, documentation closeout, review loops,
side-thread hand-back, and issue or PR projection. It should be robustly
portable across repos, adaptable across software engineering and operations
work, and usable by humans as well as agents.

The story should include pressure-scenario validation for prompt reduction,
right-sized ceremony, missing control surfaces, security-sensitive changes,
side-thread hand-back, and use in a repo without the operator's user-global
skills installed.

### Ephemeral Workflow Opportunity Capture

After the Forge Seed, process the side-thread opportunity-capture handoff at
`docs/follow-ups/ephemeral-workflow-opportunity-capture.md`
into rigorously engineered Agent Equipment.

Begin with handoff ingestion and a `grill-with-docs` loop. The grill loop should
challenge terminology, detection thresholds, routing surfaces, privacy
constraints, harness adapters, and right-sizing rules before drafting
requirements.

The resulting story should define how agents notice session-scoped workflow
constructs that may deserve durable extraction, recommend an appropriate
handling route, and preserve source material without silently promoting
undeveloped doctrine. It should condition recommendations on harness
capabilities, operator preference, current-thread disruption, security/privacy
risk, and locally preferred follow-up mechanisms.

If the Portable Agentic Engineering Workflow Equipment, Side-Thread Hand-Back
Workflow, or Post-Seed Skill Migration tasks have already landed, ingest their
outputs as source material. Treat their workflow routing, side-thread boundary,
hand-back contracts, migrated skill provenance, and progressive-disclosure paths
as evidence to reconcile rather than decisions to bypass.

The story should include pressure-scenario validation for side-chat,
subagent-thread, current-thread, active-plan, queued-plan, backlog, issue
tracker, and no-action routes. It should prove that agents can surface useful
durability recommendations without creating excessive noise or leaking sensitive
session content.

## Self-Review

Spec coverage:

- Source Handoff provenance: Task 2 validates the archived handoff manifest, files, and provenance boundary.
- Forge Conveyor and Forge Tour: Task 3.
- Canonical docs: Task 4.
- Harness Capability Catalog refresh: Task 5.
- Templates: Task 6.
- Examples: Task 7.
- Equipment Blueprints: Task 8.
- Seed Validation: Tasks 1 through 8.
- Change Set Security Closeout and Repository Threat Model: Task 9.
- Change Set Documentation Closeout: Task 9.
- Issue Projection: Task 9.

Placeholder scan:

- No `TBD`, `TODO`, `fill in`, or `implement later` placeholders are intended in this plan.
- Each deferred scope is named as a non-goal or Equipment Blueprint, not a placeholder.

Type and name consistency:

- Use `Seed Validation Tool` for `tools/validate_forge_seed.py`.
- Use `Source Disposition Ledger` for `docs/closeout/forge-seed-source-disposition.md`.
- Use `Repository Threat Model` for `docs/security/threat-model.md`.
- Use `Change Set Security Closeout` for the merge-readiness security gate.
- Use `Change Set Documentation Closeout` for the affected-doc sweep and review gate.
- Use `Published Agent Equipment` only for equipment that has completed promotion.
- Use `Forge Example` for example surfaces.

## Execution Handoff

Plan complete and saved to `docs/plans/2026-05-03-forge-seed.md`.

Execution mode for this repo is Subagent-Driven Development. Dispatch one implementer per task, then run spec-compliance review and code-quality/doc-quality review before moving to the next task.
