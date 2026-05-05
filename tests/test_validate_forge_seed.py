import json
import subprocess
import tempfile
import textwrap
import unittest
from unittest import mock
from pathlib import Path

from tools.validate_forge_seed import (
    ACCEPTED_SOURCE_REQUIREMENTS,
    CheckResult,
    REQUIRED_HARNESSES,
    SOURCE_DISPOSITION_ITEM_FIELDS,
    SOURCE_DISPOSITION_MANIFEST_FIELDS,
    SOURCE_DISPOSITION_PATH,
    find_markdown_links,
    harness_matrix_rows,
    load_toml,
    render_human,
    run,
    source_disposition_table_digest,
    validate_final_source_retired_stamp,
    validate_final_closeout,
    validate_canonical_docs,
    validate_documentation_closeout,
    validate_examples,
    validate_forge_routes,
    validate_harness_catalog,
    validate_markdown_links,
    validate_projection_drafts,
    validate_python_runtime_declaration,
    validate_specs,
    validate_source_disposition,
    validate_source_retired_tree,
    validate_source_handoff_provenance,
    validate_source_projection,
    SOURCE_PROJECTION_PLANNED_REQUIREMENTS,
    validate_required_paths,
    validate_security_closeout,
    validate_templates,
    validate_threat_model,
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

    def test_find_markdown_links_includes_outer_link_wrapping_badge(self):
        markdown = "[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)\n"

        self.assertEqual(find_markdown_links(markdown), ["LICENSE"])

    def test_find_markdown_links_strips_inline_titles(self):
        markdown = textwrap.dedent(
            """
            [quoted](docs/quoted.md "Title")
            [single](docs/single.md 'Title')
            [paren](docs/paren.md (Title))
            [angled](<docs/angled.md> "Title")
            """
        )

        self.assertEqual(
            find_markdown_links(markdown),
            [
                "docs/quoted.md",
                "docs/single.md",
                "docs/paren.md",
                "docs/angled.md",
            ],
        )

    def test_validate_python_runtime_declaration_accepts_matching_references(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".python-version").write_text("3.14\n", encoding="utf-8")
            (root / "tools").mkdir()
            (root / "tools/validate.py").write_text("#!/usr/bin/env python3.14\n", encoding="utf-8")
            (root / "docs").mkdir()
            (root / "docs/runtime.md").write_text("Use Python 3.14.\n", encoding="utf-8")

            results = validate_python_runtime_declaration(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    name="python_runtime:.python-version",
                    ok=True,
                    detail="declares Python 3.14",
                    path=".python-version",
                )
            ],
        )

    def test_validate_python_runtime_declaration_rejects_drifted_reference(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".python-version").write_text("3.15\n", encoding="utf-8")
            (root / "tools").mkdir()
            (root / "tools/validate.py").write_text("#!/usr/bin/env python3.14\n", encoding="utf-8")

            results = validate_python_runtime_declaration(root)

        self.assertIn(
            CheckResult(
                name="python_runtime:reference:tools/validate.py:3.14",
                ok=False,
                detail="Python runtime reference 3.14 does not match .python-version 3.15",
                path="tools/validate.py",
            ),
            results,
        )

    def test_validate_python_runtime_declaration_rejects_invalid_version_shape(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".python-version").write_text("python3.14\n", encoding="utf-8")

            results = validate_python_runtime_declaration(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    name="python_runtime:.python-version",
                    ok=False,
                    detail="must contain MAJOR.MINOR",
                    path=".python-version",
                )
            ],
        )

    def test_validate_python_runtime_declaration_ignores_historical_and_source_bearing_docs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            drifted_reference = "Python " + "3.13"
            (root / ".python-version").write_text("3.14\n", encoding="utf-8")
            (root / "tools").mkdir()
            (root / "tools/validate.py").write_text("#!/usr/bin/env python3.14\n", encoding="utf-8")
            (root / "docs/adr").mkdir(parents=True)
            (root / "docs/adr/0001-runtime-history.md").write_text(
                f"This historical decision mentioned {drifted_reference}.\n",
                encoding="utf-8",
            )
            (root / "docs/metasmith/handoff/2026-05-02").mkdir(parents=True)
            (root / "docs/metasmith/handoff/2026-05-02/provenance.md").write_text(
                f"Source-bearing provenance mentioned {drifted_reference}.\n",
                encoding="utf-8",
            )

            results = validate_python_runtime_declaration(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    name="python_runtime:.python-version",
                    ok=True,
                    detail="declares Python 3.14",
                    path=".python-version",
                )
            ],
        )

    def test_validate_python_runtime_declaration_rejects_closeout_reference_drift(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            drifted_version = "3.13"
            drifted_reference = f"Python {drifted_version}"
            (root / ".python-version").write_text("3.14\n", encoding="utf-8")
            (root / "docs/closeout").mkdir(parents=True)
            (root / "docs/closeout/summary.md").write_text(
                f"Closeout evidence mentioned {drifted_reference}.\n",
                encoding="utf-8",
            )

            results = validate_python_runtime_declaration(root)

        self.assertIn(
            CheckResult(
                name="python_runtime:reference:docs/closeout/summary.md:3.13",
                ok=False,
                detail=f"Python runtime reference {drifted_version} does not match .python-version 3.14",
                path="docs/closeout/summary.md",
            ),
            results,
        )

    def test_validate_python_runtime_declaration_ignores_symlinked_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            root = workspace / "repo"
            root.mkdir()
            drifted_reference = "Python " + "3.13"
            (root / ".python-version").write_text("3.14\n", encoding="utf-8")
            external_note = workspace / "external-runtime.md"
            external_note.write_text(f"External note mentioned {drifted_reference}.\n", encoding="utf-8")
            (root / "docs").mkdir()
            (root / "docs/runtime.md").symlink_to(external_note)

            results = validate_python_runtime_declaration(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    name="python_runtime:.python-version",
                    ok=True,
                    detail="declares Python 3.14",
                    path=".python-version",
                )
            ],
        )

    def test_validate_python_runtime_declaration_ignores_directory_iteration_errors(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".python-version").write_text("3.14\n", encoding="utf-8")

            with mock.patch.object(Path, "iterdir", side_effect=OSError("unreadable")):
                results = validate_python_runtime_declaration(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    name="python_runtime:.python-version",
                    ok=True,
                    detail="declares Python 3.14",
                    path=".python-version",
                )
            ],
        )

    def test_validate_python_runtime_declaration_ignores_local_work_directories(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            drifted_reference = "Python " + "3.13"
            (root / ".python-version").write_text("3.14\n", encoding="utf-8")
            (root / "tools").mkdir()
            (root / "tools/validate.py").write_text("#!/usr/bin/env python3.14\n", encoding="utf-8")
            (root / ".venv/lib").mkdir(parents=True)
            (root / ".venv/lib/runtime.txt").write_text(
                f"Tool output mentioned {drifted_reference}.\n",
                encoding="utf-8",
            )
            (root / "scratch").mkdir()
            (root / "scratch/runtime.txt").write_text(
                f"Scratch notes mentioned {drifted_reference}.\n",
                encoding="utf-8",
            )
            (root / "node_modules/demo").mkdir(parents=True)
            (root / "node_modules/demo/runtime.txt").write_text(
                f"Dependency notes mentioned {drifted_reference}.\n",
                encoding="utf-8",
            )

            results = validate_python_runtime_declaration(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    name="python_runtime:.python-version",
                    ok=True,
                    detail="declares Python 3.14",
                    path=".python-version",
                )
            ],
        )

    def test_find_markdown_links_includes_local_image_targets(self):
        markdown = "![Diagram](docs/diagram.png)\n"

        self.assertEqual(find_markdown_links(markdown), ["docs/diagram.png"])

    def test_find_markdown_links_ignores_inline_code_spans(self):
        markdown = "Use `[example](docs/missing.md)` when describing Markdown syntax.\n"

        self.assertEqual(find_markdown_links(markdown), [])

    def test_find_markdown_links_ignores_indented_code_blocks(self):
        markdown = textwrap.dedent(
            """
            [real](docs/real.md)

                [example](docs/missing.md)
            """
        )

        self.assertEqual(find_markdown_links(markdown), ["docs/real.md"])

    def test_find_markdown_links_includes_reference_definitions(self):
        markdown = textwrap.dedent(
            """
            See [guide][framework].

            [framework]: docs/framework.md "Framework"
            [absolute]: https://example.com/reference
            [anchor]: #local
            """
        )

        self.assertEqual(find_markdown_links(markdown), ["docs/framework.md"])

    def test_find_markdown_links_ignores_footnote_definitions(self):
        markdown = textwrap.dedent(
            """
            See this note.[^1]

            [^1]: This note is prose, not a link target.
            """
        )

        self.assertEqual(find_markdown_links(markdown), [])

    def test_validate_markdown_links_ignores_escaped_reference_use(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            (root / "docs/start.md").write_text(r"\[guide][missing]" + "\n", encoding="utf-8")

            results = validate_markdown_links(root)

        self.assertTrue(all(result.ok for result in results), results)

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
                f"| {requirement_id} | {metadata['source_file']} | {metadata['source_anchor']} | Summary | projected | docs/ubiquitous-language.md |  | {'planned' if requirement_id in SOURCE_PROJECTION_PLANNED_REQUIREMENTS else 'validated'} |"
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
                f"| {requirement_id} | {metadata['source_file']} | {metadata['source_anchor']} | Summary | projected | docs/ubiquitous-language.md |  | {'planned' if requirement_id in SOURCE_PROJECTION_PLANNED_REQUIREMENTS else 'validated'} |"
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
                f"| {requirement_id} | {metadata['source_file']} | {metadata['source_anchor']} | Summary | projected | docs/ubiquitous-language.md |  | {'planned' if requirement_id in SOURCE_PROJECTION_PLANNED_REQUIREMENTS else 'validated'} |"
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
                f"| {requirement_id} | {metadata['source_file']} | {metadata['source_anchor']} | Summary | projected | docs/ubiquitous-language.md |  | {'planned' if requirement_id in SOURCE_PROJECTION_PLANNED_REQUIREMENTS else 'validated'} |"
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
                    "| H001 | 00-metasmith-handoff-prompt.md | Your objective | Summary | projected | docs/target.md |  | validated |"
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
                    "| H001 | 00-metasmith-handoff-prompt.md | Your objective | Summary | projected | docs/target.md |  | validated |"
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
                f"| {requirement_id} | {metadata['source_file']} | {metadata['source_anchor']} | Summary | projected | docs/target.md |  | {'planned' if requirement_id in SOURCE_PROJECTION_PLANNED_REQUIREMENTS else 'validated'} |"
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
                f"| {requirement_id} | {metadata['source_file']} | {metadata['source_anchor']} | Summary | projected | docs/missing.md |  | {'planned' if requirement_id in SOURCE_PROJECTION_PLANNED_REQUIREMENTS else 'validated'} |"
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
                f"| {requirement_id} | {metadata['source_file']} | {metadata['source_anchor']} | Summary | projected | docs/ubiquitous-language.md |  | {'planned' if requirement_id in SOURCE_PROJECTION_PLANNED_REQUIREMENTS else 'validated'} |"
                for requirement_id, metadata in ACCEPTED_SOURCE_REQUIREMENTS.items()
            ]
            rows[0] = "| H001 | 00-metasmith-handoff-prompt.md | Your objective | Defer seed objective | deferred | specs/future-work.md | Deferred until follow-up. | planned |"
            self.write_register(root, rows)

            results = validate_source_projection(root)

        self.assertTrue(all(result.ok for result in results), results)

    def test_validate_source_projection_rejects_unknown_validation_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            self.write_source_handoff_fixture(root)
            (root / "docs/ubiquitous-language.md").write_text("# Fixture\n", encoding="utf-8")
            rows = [
                f"| {requirement_id} | {metadata['source_file']} | {metadata['source_anchor']} | Summary | projected | docs/ubiquitous-language.md |  | {'planned' if requirement_id in SOURCE_PROJECTION_PLANNED_REQUIREMENTS else 'validated'} |"
                for requirement_id, metadata in ACCEPTED_SOURCE_REQUIREMENTS.items()
            ]
            rows[0] = rows[0].replace(" | validated |", " | done |")
            self.write_register(root, rows)

            results = validate_source_projection(root)

        self.assertIn(
            CheckResult(
                name="source_projection:H001",
                ok=False,
                detail="validation_status must be planned or validated",
                path="docs/metasmith/source-projection.md",
            ),
            results,
        )

    def test_validate_source_projection_rejects_premature_validated_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            self.write_source_handoff_fixture(root)
            (root / "docs/ubiquitous-language.md").write_text("# Fixture\n", encoding="utf-8")
            rows = []
            for requirement_id, metadata in ACCEPTED_SOURCE_REQUIREMENTS.items():
                status = "validated" if requirement_id in SOURCE_PROJECTION_PLANNED_REQUIREMENTS else "planned"
                rows.append(
                    f"| {requirement_id} | {metadata['source_file']} | {metadata['source_anchor']} | Summary | projected | docs/ubiquitous-language.md |  | {status} |"
                )
            self.write_register(root, rows)

            results = validate_source_projection(root)

        self.assertIn(
            CheckResult(
                name="source_projection:H012",
                ok=False,
                detail="validation_status must remain planned until closeout evidence lands",
                path="docs/metasmith/source-projection.md",
            ),
            results,
        )

    def test_validate_source_projection_rejects_stale_planned_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            self.write_source_handoff_fixture(root)
            (root / "docs/ubiquitous-language.md").write_text("# Fixture\n", encoding="utf-8")
            rows = []
            for requirement_id, metadata in ACCEPTED_SOURCE_REQUIREMENTS.items():
                status = "planned" if requirement_id == "H001" else "validated"
                if requirement_id in SOURCE_PROJECTION_PLANNED_REQUIREMENTS:
                    status = "planned"
                rows.append(
                    f"| {requirement_id} | {metadata['source_file']} | {metadata['source_anchor']} | Summary | projected | docs/ubiquitous-language.md |  | {status} |"
                )
            self.write_register(root, rows)

            results = validate_source_projection(root)

        self.assertIn(
            CheckResult(
                name="source_projection:H001",
                ok=False,
                detail="validation_status must be validated for completed projected requirement",
                path="docs/metasmith/source-projection.md",
            ),
            results,
        )

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
                f"| {requirement_id} | {metadata['source_file']} | {metadata['source_anchor']} | Summary | projected | docs/ubiquitous-language.md |  | {'planned' if requirement_id in SOURCE_PROJECTION_PLANNED_REQUIREMENTS else 'validated'} |"
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


class SourceDispositionTests(unittest.TestCase):
    def write_source_disposition(
        self,
        root: Path,
        *,
        synthetic_payload: str = "accepted requirement constants H001 H002",
    ) -> None:
        path = root / SOURCE_DISPOSITION_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        manifest_rows = [
            {
                "source_id": "SYN001",
                "source_kind": "synthetic",
                "original_path": "tools/validate_forge_seed.py",
                "git_blob_id": "abc123",
                "sha256": "def456",
                "normalized_payload_digest": "789abc",
                "durable_payload": synthetic_payload,
            }
        ]
        item_rows = [
            {
                "item_id": "I001",
                "source_id": "SYN001",
                "coverage_status": "adequately_captured",
                "challenge_status": "unchallenged",
                "challenge_operator_confirmation_required": "false",
                "arbitration_required": "false",
                "disposition": "kept_current",
                "operator_decision": "",
                "evidence_target": "docs/agent-equipment-forge.md",
                "normalized_claim_summary": "Keep the synthetic accepted requirement in the Forge docs.",
            },
            {
                "item_id": "I002",
                "source_id": "SYN001",
                "coverage_status": "partially_captured",
                "challenge_status": "resolved",
                "challenge_operator_confirmation_required": "true",
                "arbitration_required": "true",
                "disposition": "integrated",
                "operator_decision": "Operator accepted integration.",
                "evidence_target": "docs/follow-ups/portable-agentic-engineering-workflow-equipment.md",
                "normalized_claim_summary": "Capture the portable workflow equipment follow-up.",
            },
        ]
        source_manifest_digest = source_disposition_table_digest(
            manifest_rows,
            SOURCE_DISPOSITION_MANIFEST_FIELDS,
        )
        source_disposition_digest = source_disposition_table_digest(
            item_rows,
            SOURCE_DISPOSITION_ITEM_FIELDS,
        )
        path.write_text(
            textwrap.dedent(
                f"""
                # Forge Seed Source Disposition

                Status: Source Bearing

                ## Source Manifest

                | source_id | source_kind | original_path | git_blob_id | sha256 | normalized_payload_digest | durable_payload |
                | --- | --- | --- | --- | --- | --- | --- |
                | SYN001 | synthetic | tools/validate_forge_seed.py | abc123 | def456 | 789abc | {synthetic_payload} |

                ## Disposition Items

                | item_id | source_id | coverage_status | challenge_status | challenge_operator_confirmation_required | arbitration_required | disposition | operator_decision | evidence_target | normalized_claim_summary |
                | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
                | I001 | SYN001 | adequately_captured | unchallenged | false | false | kept_current |  | docs/agent-equipment-forge.md | Keep the synthetic accepted requirement in the Forge docs. |
                | I002 | SYN001 | partially_captured | resolved | true | true | integrated | Operator accepted integration. | docs/follow-ups/portable-agentic-engineering-workflow-equipment.md | Capture the portable workflow equipment follow-up. |

                ## Source-Bearing Stamp

                source_bearing_snapshot_tree_id: source-tree
                source_bearing_stamp_id: source-bearing-1
                source_manifest_digest: {source_manifest_digest}
                source_disposition_digest: {source_disposition_digest}
                source_bearing_result: passed

                ## Final Source-Retired Stamp

                source_retired: true
                """
            ).strip()
            + "\n",
            encoding="utf-8",
        )

    def test_validate_source_disposition_accepts_self_contained_synthetic_payload(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            (root / "docs/agent-equipment-forge.md").write_text("# Forge\n", encoding="utf-8")
            (root / "docs/follow-ups").mkdir()
            (root / "docs/follow-ups/portable-agentic-engineering-workflow-equipment.md").write_text(
                "# Follow-up\n",
                encoding="utf-8",
            )
            self.write_source_disposition(root)

            results = validate_source_disposition(root)

        self.assertTrue(all(result.ok for result in results), results)

    def test_validate_source_disposition_rejects_synthetic_source_without_durable_payload(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_source_disposition(root, synthetic_payload="")

            results = validate_source_disposition(root)

        self.assertIn(
            CheckResult(
                "source_disposition:source:SYN001",
                False,
                "synthetic source missing durable payload",
                SOURCE_DISPOSITION_PATH,
            ),
            results,
        )

    def test_validate_source_disposition_rejects_malformed_file_source_identity(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_source_disposition(root)
            path = root / SOURCE_DISPOSITION_PATH
            path.write_text(
                path.read_text(encoding="utf-8").replace(
                    "| SYN001 | synthetic | tools/validate_forge_seed.py | abc123 | def456 | 789abc | accepted requirement constants H001 H002 |",
                    "| SYN001 | file | docs/metasmith/source-projection.md |  | def456 | 789abc | retired source file |",
                ),
                encoding="utf-8",
            )

            results = validate_source_disposition(root)

        self.assertIn(
            CheckResult(
                "source_disposition:source:SYN001",
                False,
                "file source git_blob_id must be a 40-character hex object id",
                SOURCE_DISPOSITION_PATH,
            ),
            results,
        )

    def test_validate_source_disposition_rejects_integrated_item_without_arbitration(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_source_disposition(root)
            path = root / SOURCE_DISPOSITION_PATH
            path.write_text(
                path.read_text(encoding="utf-8").replace(
                    "| I002 | SYN001 | partially_captured | resolved | true | true | integrated | Operator accepted integration. | docs/follow-ups/portable-agentic-engineering-workflow-equipment.md | Capture the portable workflow equipment follow-up. |",
                    "| I002 | SYN001 | partially_captured | resolved | false | false | integrated |  | docs/follow-ups/portable-agentic-engineering-workflow-equipment.md | Capture the portable workflow equipment follow-up. |",
                ),
                encoding="utf-8",
            )

            results = validate_source_disposition(root)

        self.assertIn(
            CheckResult(
                "source_disposition:item:I002",
                False,
                "integrated disposition requires arbitration and operator_decision",
                SOURCE_DISPOSITION_PATH,
            ),
            results,
        )

    def test_validate_source_disposition_rejects_missing_normalized_claim_summary(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_source_disposition(root)
            path = root / SOURCE_DISPOSITION_PATH
            path.write_text(
                path.read_text(encoding="utf-8").replace(" | normalized_claim_summary", ""),
                encoding="utf-8",
            )

            results = validate_source_disposition(root)

        self.assertIn(
            CheckResult(
                "source_disposition:item:I001",
                False,
                "missing fields: normalized_claim_summary",
                SOURCE_DISPOSITION_PATH,
            ),
            results,
        )

    def test_validate_source_disposition_rejects_empty_normalized_claim_summary(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_source_disposition(root)
            path = root / SOURCE_DISPOSITION_PATH
            path.write_text(
                path.read_text(encoding="utf-8").replace(
                    "| I001 | SYN001 | adequately_captured | unchallenged | false | false | kept_current |  | docs/agent-equipment-forge.md | Keep the synthetic accepted requirement in the Forge docs. |",
                    "| I001 | SYN001 | adequately_captured | unchallenged | false | false | kept_current |  | docs/agent-equipment-forge.md |  |",
                ),
                encoding="utf-8",
            )

            results = validate_source_disposition(root)

        self.assertIn(
            CheckResult(
                "source_disposition:item:I001",
                False,
                "normalized_claim_summary required",
                SOURCE_DISPOSITION_PATH,
            ),
            results,
        )

    def test_validate_source_disposition_rejects_source_manifest_digest_mismatch(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_source_disposition(root)
            path = root / SOURCE_DISPOSITION_PATH
            path.write_text(
                path.read_text(encoding="utf-8").replace(
                    "source_manifest_digest: ",
                    "source_manifest_digest: bad",
                    1,
                ),
                encoding="utf-8",
            )

            results = validate_source_disposition(root)

        self.assertIn(
            CheckResult(
                "source_disposition:source_manifest_digest",
                False,
                "source_manifest_digest mismatch",
                SOURCE_DISPOSITION_PATH,
            ),
            results,
        )

    def test_validate_source_disposition_rejects_missing_source_bearing_stamp_field(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_source_disposition(root)
            path = root / SOURCE_DISPOSITION_PATH
            path.write_text(
                path.read_text(encoding="utf-8").replace(
                    "\nsource_bearing_result: passed",
                    "",
                ),
                encoding="utf-8",
            )

            results = validate_source_disposition(root)

        self.assertIn(
            CheckResult(
                "source_disposition:stamp:source_bearing_result",
                False,
                "missing source_bearing_result",
                SOURCE_DISPOSITION_PATH,
            ),
            results,
        )

    def test_validate_source_retired_tree_requires_final_source_item_coverage(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            (root / "docs/agent-equipment-forge.md").write_text("# Forge\n", encoding="utf-8")
            (root / "docs/follow-ups").mkdir()
            (root / "docs/follow-ups/portable-agentic-engineering-workflow-equipment.md").write_text(
                "# Follow-up\n",
                encoding="utf-8",
            )
            self.write_source_disposition(root)

            results = validate_source_retired_tree(root)

        self.assertTrue(
            any(
                result
                == CheckResult(
                    "source_disposition:required_items",
                    False,
                    result.detail,
                    SOURCE_DISPOSITION_PATH,
                )
                and "H001" in result.detail
                for result in results
            ),
            results,
        )

    def test_validate_source_disposition_rejects_symlink_evidence_target(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            outside = root / "outside.md"
            outside.write_text("# Outside\n", encoding="utf-8")
            (root / "docs").mkdir()
            (root / "docs/agent-equipment-forge.md").symlink_to(outside)
            (root / "docs/follow-ups").mkdir()
            (root / "docs/follow-ups/portable-agentic-engineering-workflow-equipment.md").write_text(
                "# Follow-up\n",
                encoding="utf-8",
            )
            self.write_source_disposition(root)

            results = validate_source_disposition(root)

        self.assertIn(
            CheckResult(
                "source_disposition:item:I001:target:docs/agent-equipment-forge.md",
                False,
                "evidence target path contains symlink",
                SOURCE_DISPOSITION_PATH,
            ),
            results,
        )

    def test_validate_source_retired_tree_rejects_raw_forgewright_sources(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs/metasmith/handoff").mkdir(parents=True)
            self.write_source_disposition(root)

            results = validate_source_retired_tree(root)

        self.assertIn(
            CheckResult(
                "source_retired:raw_sources",
                False,
                "docs/metasmith must be removed after source disposition",
                "docs/metasmith",
            ),
            results,
        )

    def test_validate_source_retired_tree_rejects_dangling_raw_source_symlink(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            (root / "docs/metasmith").symlink_to(root / "missing")
            self.write_source_disposition(root)

            results = validate_source_retired_tree(root)

        self.assertIn(
            CheckResult(
                "source_retired:raw_sources",
                False,
                "docs/metasmith must be removed after source disposition",
                "docs/metasmith",
            ),
            results,
        )

    def test_validate_final_source_retired_stamp_accepts_stable_retired_marker(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_source_disposition(root)

            results = validate_final_source_retired_stamp(root)

        self.assertTrue(all(result.ok for result in results), results)
        self.assertIn(
            CheckResult(
                "source_retired_stamp:source_retired",
                True,
                "true",
                SOURCE_DISPOSITION_PATH,
            ),
            results,
        )

    def test_validate_final_source_retired_stamp_scopes_fields_to_final_section(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_source_disposition(root)
            path = root / SOURCE_DISPOSITION_PATH
            markdown = path.read_text(encoding="utf-8")
            path.write_text(
                markdown.replace(
                    "## Final Source-Retired Stamp",
                    "\n".join(
                        [
                            "stamp_target: source-bearing tree",
                            "canonical_tree_digest: legacy-source-bearing-digest",
                            "timestamp: 2026-05-04T00:00:00Z",
                            "",
                            "## Final Source-Retired Stamp",
                        ]
                    ),
                ),
                encoding="utf-8",
            )

            results = validate_final_source_retired_stamp(root)

        self.assertTrue(all(result.ok for result in results), results)
        self.assertIn(
            CheckResult(
                "source_retired_stamp:source_retired",
                True,
                "true",
                SOURCE_DISPOSITION_PATH,
            ),
            results,
        )

    def test_validate_final_source_retired_stamp_rejects_volatile_digest_fields(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_source_disposition(root)
            path = root / SOURCE_DISPOSITION_PATH
            markdown = path.read_text(encoding="utf-8")
            path.write_text(
                markdown.replace(
                    "source_retired: true",
                    "\n".join(
                        [
                            "stamp_target: placeholder-normalized canonical tree",
                            "canonical_tree_digest: abc123",
                            "source_retired: true",
                            "timestamp: 2026-05-04T00:00:00Z",
                        ]
                    ),
                ),
                encoding="utf-8",
            )

            results = validate_final_source_retired_stamp(root)

        self.assertIn(
            CheckResult(
                "source_retired_stamp:canonical_tree_digest",
                False,
                "canonical_tree_digest is volatile and must be removed",
                SOURCE_DISPOSITION_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "source_retired_stamp:stamp_target",
                False,
                "stamp_target is volatile and must be removed",
                SOURCE_DISPOSITION_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "source_retired_stamp:timestamp",
                False,
                "timestamp is volatile and must be removed",
                SOURCE_DISPOSITION_PATH,
            ),
            results,
        )

    def test_run_source_bearing_requires_raw_source_inputs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = run(root, source_mode="source-bearing")

        self.assertIn(
            CheckResult(
                "required_path:docs/metasmith/source-projection.md",
                False,
                "missing",
                "docs/metasmith/source-projection.md",
            ),
            results,
        )
        self.assertTrue(any(result.name.startswith("source_handoff:") for result in results), results)

    def test_run_source_retired_final_skips_raw_source_inputs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            (root / "docs/agent-equipment-forge.md").write_text("# Forge\n", encoding="utf-8")
            (root / "docs/follow-ups").mkdir()
            (root / "docs/follow-ups/portable-agentic-engineering-workflow-equipment.md").write_text(
                "# Follow-up\n",
                encoding="utf-8",
            )
            self.write_source_disposition(root)

            results = run(root, source_mode="source-retired-final")

        self.assertNotIn(
            CheckResult(
                "required_path:docs/metasmith/source-projection.md",
                False,
                "missing",
                "docs/metasmith/source-projection.md",
            ),
            results,
        )
        self.assertFalse(
            any(result.name.startswith(("source_projection:", "source_handoff:")) for result in results),
            results,
        )
        self.assertIn(
            CheckResult(
                "source_retired_stamp:source_retired",
                True,
                "true",
                SOURCE_DISPOSITION_PATH,
            ),
            results,
        )


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

                    - `docs/vision.md`
                    - `docs/agent-equipment-forge.md`
                    - `docs/smith-runbook.md`
                    - `docs/harness-capabilities.md`
                    - `templates/`
                    - `specs/`
                    """
                ),
                encoding="utf-8",
            )
            (root / "README.md").write_text(
                "## Agent Equipment Forge\n\nStart with [Forge Tour](docs/forge-tour.md).\n",
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
            (root / "specs").mkdir()
            for path in [
                "docs/vision.md",
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

                    - `docs/vision.md`
                    - `docs/agent-equipment-forge.md`
                    - `docs/smith-runbook.md`
                    - `docs/interface-decision-guide.md`
                    - `docs/harness-capabilities.md`
                    - `templates/`
                    - `specs/`
                    """
                ),
                encoding="utf-8",
            )
            (root / "README.md").write_text(
                "## Agent Equipment Forge\n\nStart with [Forge Tour](docs/forge-tour.md).\n",
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

    def test_validate_forge_routes_rejects_wrong_route_target_kind(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            (root / "docs/vision.md").write_text("# Fixture\n", encoding="utf-8")
            (root / "docs/agent-equipment-forge.md").mkdir()
            (root / "docs/smith-runbook.md").write_text("# Fixture\n", encoding="utf-8")
            (root / "docs/interface-decision-guide.md").write_text("# Fixture\n", encoding="utf-8")
            (root / "docs/harness-capabilities.md").write_text("# Fixture\n", encoding="utf-8")
            (root / "templates").write_text("not a directory\n", encoding="utf-8")
            (root / "specs").mkdir()
            (root / "AGENTS.md").write_text(
                textwrap.dedent(
                    """
                    # AGENTS

                    ## Forge Conveyor

                    - `docs/vision.md`
                    - `docs/agent-equipment-forge.md`
                    - `docs/smith-runbook.md`
                    - `docs/interface-decision-guide.md`
                    - `docs/harness-capabilities.md`
                    - `templates/`
                    - `specs/`
                    """
                ),
                encoding="utf-8",
            )
            (root / "README.md").write_text(
                "## Agent Equipment Forge\n\nStart with [Forge Tour](docs/forge-tour.md).\n",
                encoding="utf-8",
            )

            results = validate_forge_routes(root)

        self.assertIn(
            CheckResult(
                "forge_route:target:docs/agent-equipment-forge.md",
                False,
                "route target not a file",
                "AGENTS.md",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "forge_route:target:templates/",
                False,
                "route target not a directory",
                "AGENTS.md",
            ),
            results,
        )


class CanonicalDocTests(unittest.TestCase):
    canonical_docs = {
        "docs/vision.md": [
            "Experience",
            "Equipment",
            "Deterministic boundaries",
            "Harness lifecycle",
            "Self-onboarding",
            "Metacognitive loop",
            "Reflection",
            "Lifecycle use",
        ],
        "docs/ubiquitous-language.md": ["Language", "Relationships", "Precision rules"],
        "docs/agent-equipment-forge.md": [
            "Purpose",
            "Vision alignment",
            "Least cognitive privilege",
            "Component model",
            "Context management",
            "Security",
            "Maintenance",
        ],
        "docs/smith-runbook.md": [
            "Capability card",
            "Interface decision record",
            "Docs/config/scripts/hooks/skills/agents/plugins",
            "Pressure Scenario Validation",
            "Equipment Promotion Path",
            "Tooling Request",
            "Closeout",
        ],
        "docs/forgewright-runbook.md": [
            "Source handoff preservation",
            "decision projection",
            "Review Until Clean",
            "Harness Fact Refresh",
            "Change set closeout",
            "Issue Projection",
            "Equipment Blueprints",
            "Tooling Gap intake",
        ],
        "docs/interface-decision-guide.md": ["Decision tree", "placement guide"],
        "docs/harness-components.md": [
            "Skills",
            "MCP/tools",
            "hooks",
            "Agent Profiles",
            "Harness Plugins",
            "scripts",
            "local docs",
            "config",
        ],
        "docs/harness-capabilities.md": [
            "Catalog policy",
            "Refresh summary",
            "Harness matrix",
            "Harness notes",
            "Periodic Actions projection order",
            "Refresh requirement",
        ],
        "docs/evidence-taxonomy.md": [
            "documentation-supported",
            "source-supported",
            "implementation inference",
            "practitioner wisdom",
            "hypothesis",
            "artifact durability",
            "source hygiene",
        ],
        "docs/security-and-control.md": [
            "least privilege",
            "mutation gates",
            "secrets",
            "hooks",
            "MCP/tool side effects",
            "examples caveat",
        ],
        "docs/equipment-promotion.md": [
            "example",
            "specified",
            "planned",
            "implemented",
            "validated",
            "published",
            "entry/exit criteria",
        ],
        "docs/story-closeout.md": [
            "Purpose",
            "Gate order",
            "Interdependency rules",
            "Review gates",
            "Recursion and bookkeeping",
            "Completion criteria",
        ],
    }
    canonical_doc_required_text = {
        "docs/vision.md": [
            "autonomous self-onboarding to purpose-built assemblies of harness components",
            "Use this vision as an input throughout the engineering lifecycle.",
        ],
        "docs/smith-runbook.md": [
            "When a Smith finds an unsatisfied Tooling Gap that blocks or materially weakens the current equipment task, treat the Tooling Work as a dependency and escalate to a Forgewright before continuing.",
            "Choose the least disruptive Forgewright path supported by the harness and operator policy: current session, subagent session, peer agent session, forked session, or new session.",
            "The handoff must include the blocked task, unsatisfied Tooling Gap, dependency impact, evidence checked, requested Forgewright deliverable, selected session path, and hand-back expectation.",
            "docs, config, scripts, hooks, skills, MCP/tools, Agent Profiles, plugins, and templates are discoverable from the Forge Conveyor",
            "Run a Cross-Boundary Coherence Ralph Review before story closeout.",
            "Run a Story Quality Ralph Review before story closeout.",
        ],
        "docs/forgewright-runbook.md": [
            "A Forgewright intake from a Smith starts by preserving the Smith handoff, refining the Tooling Gap, updating canonical surfaces and validation, and returning a hand-back note.",
            "The hand-back note names files changed, validation and review results, dependency updates, remaining risks, and the context the Smith needs to resume.",
        ],
        "docs/story-closeout.md": [
            "Story Closeout is the story-level gate; Change Set Security Closeout and Change Set Documentation Closeout are subordinate gates.",
            "Refresh the Intent Model before downstream closeout gates.",
            "Before committing or externally projecting closeout evidence, classify evidence artifacts by durability.",
            "Durable project evidence and portable review summaries may be committed or projected.",
            "Instance-scoped scratch artifacts, including raw tool reports, local scan bundles, copied diffs, host-local paths, screenshots, or work directories, should be summarized by scope, disposition, and durable conclusions instead of treated as project truth.",
            "Classify privacy and disclosure limits for actionable Reflection Findings",
            "Run Cross-Boundary Coherence before Story Quality because quality review depends on coherent process evidence.",
            "Intent Model Refresh is the first closeout gate.",
            "Update the agent's model of Underlying Intent by reviewing recent operator input, accepted ADR/PRD/spec/plan changes, review dispositions, handoff notes, and observed corrections relevant to the story before running downstream closeout gates.",
            "Story Quality also runs an Intent Alignment Check.",
            "Compare Effective Intent, meaning the Intent actually imposed by ADRs, PRDs, specs, plans, acceptance criteria, review dispositions, and other declarations, with the refreshed model of Underlying Intent after Cross-Boundary Coherence has made Effective Intent legible.",
            "Refresh the model again if closeout evidence introduced new intent signals.",
            "An agent does not directly know a stakeholder's or other intent-capable actor's Underlying Intent; it maintains an evidence-backed model that can be tested through questions, experiments, and observed corrections.",
            "Hypotheses about emotion, belief state, attention, engagement, discipline, or other internal disposition can explain why a mismatch might exist, but they are not evidence by themselves and must not justify unilateral realignment.",
            "When observable evidence shows misalignment beyond reasonable doubt, realign the affected declarations and reproject downstream implications.",
            "When the model remains uncertain, the case depends on internal-state inference, or the evidence otherwise creates a non-dismissible likelihood of misalignment without certainty, raise a concise question to the operator, using an interactive question tool when available.",
            "If a revision changes security, documentation, validation, PRD/spec/plan scope, or issue/PR projection, rerun the affected upstream gate before the next closeout review.",
            "Evidence-artifact durability changes rerun the closeout gate that owns the artifact and any projection surface that carries its claims.",
            "after privacy and disclosure limits are classified",
            "Recording the latest clean review result is bookkeeping and does not reopen the full review loop unless it changes substantive claims.",
            "Published issue, PR, release, or handoff corrections rerun a projection consistency check and a narrow Cross-Boundary Coherence review for the corrected surface.",
            "closeout evidence artifacts are classified by durability",
            "instance-scoped scratch artifacts are summarized rather than committed or externally projected as project truth",
        ],
    }

    def write_canonical_doc(self, root: Path, relative_path: str, sections: list[str] | None = None) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if relative_path == "docs/story-closeout.md" and sections is None:
            section_markdown = textwrap.dedent(
                """
                ## Purpose

                Content.

                ## Gate order

                1. Refresh the Intent Model before downstream closeout gates.
                2. Confirm the implementation, specs, plans, and deterministic validation reflect the same scope.
                3. Complete Change Set Security Closeout for the current change set.
                4. Complete Change Set Documentation Closeout for affected human-facing and agent-facing docs.
                5. Prepare projection drafts for issues, PR bodies, handoff notes, and release summaries from the current story evidence.
                6. Classify privacy and disclosure limits for actionable Reflection Findings discovered during the story, then route publishable findings into the issue tracker, Tooling Request, or the relevant Equipment Candidate, or record why the insight is not durable or not projectable.
                7. Run Cross-Boundary Coherence before Story Quality because quality review depends on coherent process evidence.
                8. Run Story Quality Ralph Review after coherence findings are fixed or soundly rejected.
                9. Run final validation and publication-readiness checks required by the active plan or repository policy.
                10. Push or otherwise publish the branch only when the active plan, operator direction, or issue-projection surface needs a pushed commit before PR creation.
                11. Publish or update issue, PR, release, and handoff surfaces from the clean final story evidence.
                12. Perform publication actions that remain in scope.

                ## Interdependency rules

                Content.

                ## Review gates

                Content.

                ## Recursion and bookkeeping

                Content.

                ## Completion criteria

                Content.
                """
            )
        else:
            section_markdown = "\n".join(f"## {section}\n\nContent.\n" for section in (sections or self.canonical_docs[relative_path]))
        required_text = "\n".join(self.canonical_doc_required_text.get(relative_path, []))
        path.write_text(f"# {path.stem}\n\nStatus: Forge Seed\n\n{section_markdown}\n{required_text}\n", encoding="utf-8")

    def write_all_canonical_docs(self, root: Path) -> None:
        for relative_path in self.canonical_docs:
            self.write_canonical_doc(root, relative_path)

    def test_validate_canonical_docs_reports_missing_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = validate_canonical_docs(root)

        self.assertIn(
            CheckResult(
                "canonical_doc:docs/agent-equipment-forge.md",
                False,
                "missing",
                "docs/agent-equipment-forge.md",
            ),
            results,
        )

    def test_validate_canonical_docs_requires_story_closeout_doc(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            for relative_path in self.canonical_docs:
                if relative_path != "docs/story-closeout.md":
                    self.write_canonical_doc(root, relative_path)

            results = validate_canonical_docs(root)

        self.assertIn(
            CheckResult(
                "canonical_doc:docs/story-closeout.md",
                False,
                "missing",
                "docs/story-closeout.md",
            ),
            results,
        )

    def test_validate_canonical_docs_rejects_story_closeout_gate_order(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_canonical_docs(root)
            story_path = root / "docs/story-closeout.md"
            story_text = story_path.read_text(encoding="utf-8")
            story_text = story_text.replace(
                "5. Prepare projection drafts for issues, PR bodies, handoff notes, and release summaries from the current story evidence.",
                "5. Run Cross-Boundary Coherence before Story Quality because quality review depends on coherent process evidence.",
            ).replace(
                "7. Run Cross-Boundary Coherence before Story Quality because quality review depends on coherent process evidence.",
                "7. Prepare projection drafts for issues, PR bodies, handoff notes, and release summaries from the current story evidence.",
            )
            story_path.write_text(story_text, encoding="utf-8")

            results = validate_canonical_docs(root)

        self.assertIn(
            CheckResult(
                name="canonical_doc:story_closeout_gate_order:docs/story-closeout.md",
                ok=False,
                detail="gate order must include required items in order",
                path="docs/story-closeout.md",
            ),
            results,
        )

    def test_validate_canonical_docs_rejects_story_closeout_missing_reflection_route(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_canonical_docs(root)
            story_path = root / "docs/story-closeout.md"
            story_text = story_path.read_text(encoding="utf-8").replace(
                "6. Classify privacy and disclosure limits for actionable Reflection Findings discovered during the story, then route publishable findings into the issue tracker, Tooling Request, or the relevant Equipment Candidate, or record why the insight is not durable or not projectable.",
                "6. Record workflow observations before review.",
            )
            story_path.write_text(story_text, encoding="utf-8")

            results = validate_canonical_docs(root)

        self.assertIn(
            CheckResult(
                name="canonical_doc:story_closeout_gate_order:docs/story-closeout.md",
                ok=False,
                detail="gate order must include required items in order",
                path="docs/story-closeout.md",
            ),
            results,
        )

    def test_validate_canonical_docs_rejects_story_closeout_missing_branch_push_gate(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_canonical_docs(root)
            story_path = root / "docs/story-closeout.md"
            story_text = story_path.read_text(encoding="utf-8").replace(
                "10. Push or otherwise publish the branch only when the active plan, operator direction, or issue-projection surface needs a pushed commit before PR creation.",
                "10. Record local publication notes.",
            )
            story_path.write_text(story_text, encoding="utf-8")

            results = validate_canonical_docs(root)

        self.assertIn(
            CheckResult(
                name="canonical_doc:story_closeout_gate_order:docs/story-closeout.md",
                ok=False,
                detail="gate order must include required items in order",
                path="docs/story-closeout.md",
            ),
            results,
        )

    def test_validate_canonical_docs_requires_story_closeout_publication_correction_rule(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_canonical_docs(root)
            story_path = root / "docs/story-closeout.md"
            missing_text = "Published issue, PR, release, or handoff corrections rerun a projection consistency check and a narrow Cross-Boundary Coherence review for the corrected surface."
            story_path.write_text(story_path.read_text(encoding="utf-8").replace(missing_text, ""), encoding="utf-8")

            results = validate_canonical_docs(root)

        self.assertIn(
            CheckResult(
                f"canonical_doc:text:docs/story-closeout.md:{missing_text}",
                False,
                f"missing text: {missing_text}",
                "docs/story-closeout.md",
            ),
            results,
        )

    def test_validate_canonical_docs_requires_framework_seed_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_canonical_docs(root)
            (root / "docs/agent-equipment-forge.md").write_text(
                "# Equipment Framework\n\n## Purpose\n\nContent.\n",
                encoding="utf-8",
            )

            results = validate_canonical_docs(root)

        self.assertIn(
            CheckResult(
                "canonical_doc:status:docs/agent-equipment-forge.md",
                False,
                "missing Status: Forge Seed",
                "docs/agent-equipment-forge.md",
            ),
            results,
        )

    def test_validate_canonical_docs_ignores_status_in_fenced_code(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_canonical_docs(root)
            fence = "`" * 3
            (root / "docs/agent-equipment-forge.md").write_text(
                f"# Equipment Framework\n\n{fence}\nStatus: Forge Seed\n{fence}\n\n## Purpose\n\nContent.\n",
                encoding="utf-8",
            )

            results = validate_canonical_docs(root)

        self.assertIn(
            CheckResult(
                "canonical_doc:status:docs/agent-equipment-forge.md",
                False,
                "missing Status: Forge Seed",
                "docs/agent-equipment-forge.md",
            ),
            results,
        )

    def test_validate_canonical_docs_requires_sections(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_canonical_docs(root)
            self.write_canonical_doc(root, "docs/agent-equipment-forge.md", sections=["Purpose"])

            results = validate_canonical_docs(root)

        self.assertIn(
            CheckResult(
                "canonical_doc:section:docs/agent-equipment-forge.md:Maintenance",
                False,
                "missing section: Maintenance",
                "docs/agent-equipment-forge.md",
            ),
            results,
        )

    def test_validate_canonical_docs_ignores_sections_in_indented_code(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_canonical_docs(root)
            (root / "docs/agent-equipment-forge.md").write_text(
                textwrap.dedent(
                    """
                    # Equipment Framework

                    Status: Forge Seed

                    ## Purpose

                    Content.

                        ## Maintenance
                    """
                ),
                encoding="utf-8",
            )

            results = validate_canonical_docs(root)

        self.assertIn(
            CheckResult(
                "canonical_doc:section:docs/agent-equipment-forge.md:Maintenance",
                False,
                "missing section: Maintenance",
                "docs/agent-equipment-forge.md",
            ),
            results,
        )

    def test_validate_canonical_docs_requires_closeout_text(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_canonical_docs(root)
            self.write_canonical_doc(root, "docs/smith-runbook.md")
            missing_text = self.canonical_doc_required_text["docs/smith-runbook.md"][0]
            (root / "docs/smith-runbook.md").write_text(
                (root / "docs/smith-runbook.md").read_text(encoding="utf-8").replace(missing_text, ""),
                encoding="utf-8",
            )

            results = validate_canonical_docs(root)

        self.assertIn(
            CheckResult(
                f"canonical_doc:text:docs/smith-runbook.md:{missing_text}",
                False,
                f"missing text: {missing_text}",
                "docs/smith-runbook.md",
            ),
            results,
        )

    def test_validate_canonical_docs_requires_story_closeout_review_gates(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_canonical_docs(root)
            self.write_canonical_doc(root, "docs/smith-runbook.md")
            missing_text = "Run a Cross-Boundary Coherence Ralph Review before story closeout."
            (root / "docs/smith-runbook.md").write_text(
                (root / "docs/smith-runbook.md").read_text(encoding="utf-8").replace(missing_text, ""),
                encoding="utf-8",
            )

            results = validate_canonical_docs(root)

        self.assertIn(
            CheckResult(
                f"canonical_doc:text:docs/smith-runbook.md:{missing_text}",
                False,
                f"missing text: {missing_text}",
                "docs/smith-runbook.md",
            ),
            results,
        )

    def test_run_reports_missing_canonical_docs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = run(root)

        self.assertIn(
            CheckResult(
                "required_path:docs/agent-equipment-forge.md",
                False,
                "missing",
                "docs/agent-equipment-forge.md",
            ),
            results,
        )

    def test_run_reports_every_missing_canonical_doc(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = run(root)

        for relative_path in self.canonical_docs:
            self.assertIn(
                CheckResult(f"required_path:{relative_path}", False, "missing", relative_path),
                results,
            )
            self.assertIn(
                CheckResult(f"canonical_doc:{relative_path}", False, "missing", relative_path),
                results,
            )

    def test_run_reports_canonical_doc_status_and_section_failures(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_canonical_docs(root)
            (root / "docs/agent-equipment-forge.md").write_text(
                "# Equipment Framework\n\n## Purpose\n\nContent.\n",
                encoding="utf-8",
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "canonical_doc:status:docs/agent-equipment-forge.md",
                False,
                "missing Status: Forge Seed",
                "docs/agent-equipment-forge.md",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "canonical_doc:section:docs/agent-equipment-forge.md:Maintenance",
                False,
                "missing section: Maintenance",
                "docs/agent-equipment-forge.md",
            ),
            results,
        )


class ThreatModelValidationTests(unittest.TestCase):
    threat_model_path = "docs/security/threat-model.md"
    security_surface_path = "docs/security-and-control.md"
    required_sections = [
        "Assets",
        "Trust boundaries",
        "Attacker-controlled inputs",
        "Invariants",
        "Assumptions",
        "High-impact failure modes",
    ]

    def valid_threat_model(self) -> str:
        sections = "\n".join(f"## {section}\n\nContent.\n" for section in self.required_sections)
        return f"# Agent Armory Repository Threat Model\n\nStatus: Repository Threat Model\n\n{sections}"

    def write_valid_threat_model_surface(self, root: Path) -> None:
        threat_model = root / self.threat_model_path
        threat_model.parent.mkdir(parents=True, exist_ok=True)
        threat_model.write_text(self.valid_threat_model(), encoding="utf-8")
        security_surface = root / self.security_surface_path
        security_surface.parent.mkdir(parents=True, exist_ok=True)
        security_surface.write_text(
            "# Security and Control\n\nSee [Repository Threat Model](security/threat-model.md).\n",
            encoding="utf-8",
        )

    def test_validate_threat_model_reports_missing_surface(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = validate_threat_model(root)

        self.assertIn(
            CheckResult(
                f"threat_model:path:{self.threat_model_path}",
                False,
                "missing",
                self.threat_model_path,
            ),
            results,
        )

    def test_validate_threat_model_accepts_complete_surface(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_threat_model_surface(root)

            results = validate_threat_model(root)

        self.assertTrue(all(result.ok for result in results), results)

    def test_validate_threat_model_requires_sections(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_threat_model_surface(root)
            path = root / self.threat_model_path
            path.write_text(self.valid_threat_model().replace("## Invariants\n\nContent.\n", ""), encoding="utf-8")

            results = validate_threat_model(root)

        self.assertIn(
            CheckResult(
                f"threat_model:section:{self.threat_model_path}:Invariants",
                False,
                "missing section: Invariants",
                self.threat_model_path,
            ),
            results,
        )

    def test_validate_threat_model_requires_canonical_reference(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_threat_model_surface(root)
            (root / self.security_surface_path).write_text("# Security and Control\n", encoding="utf-8")

            results = validate_threat_model(root)

        self.assertIn(
            CheckResult(
                f"threat_model:reference:{self.security_surface_path}",
                False,
                "missing threat model reference",
                self.security_surface_path,
            ),
            results,
        )

    def test_run_requires_threat_model_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = run(root)

        self.assertIn(
            CheckResult(f"required_path:{self.threat_model_path}", False, "missing", self.threat_model_path),
            results,
        )


class DocumentationCloseoutValidationTests(unittest.TestCase):
    closeout_path = "docs/closeout/forge-seed-documentation.md"
    required_sections = [
        "Scope of inspected docs",
        "Docs changed",
        "Docs unchanged with rationale",
        "Stale-language cleanup result",
        "Established precedents added or updated",
        "Review status",
        "Residual documentation risk",
    ]

    def valid_closeout(self) -> str:
        sections = "\n\n".join(
            [
                "## Scope of inspected docs\n\nInspected `README.md`, `AGENTS.md`, `CONTEXT.md`, `docs/agents/*.md`, Forge Canon under `docs/*.md`, `docs/prd/forge-seed.md`, `docs/adr/*.md`, `docs/plans/2026-05-03-forge-seed.md`, `docs/security/*.md`, `docs/closeout/*.md`, `docs/closeout/forge-seed-source-disposition.md`, `specs/*.md`, `templates/**/*.md`, and `examples/**/*.md`.",
                "## Docs changed\n\nUpdated `docs/security/threat-model.md` and `docs/metasmith/source-projection.md`.",
                "## Docs unchanged with rationale\n\nRecorded why `README.md` and `AGENTS.md` needed no change.",
                "## Stale-language cleanup result\n\nStale initial-state language was searched and resolved.",
                "## Established precedents added or updated\n\nRecorded Forge Seed precedents. Portable workflow capture says a branch-push pause does not close the capture. Full Seed completion requires a merged Seed. An explicit hold or cancellation continues capture through an unmerged-state hand-back and should record the unmerged state directly.",
                "## Review status\n\n- Documentation closeout: Ralph Review Cycle 99.\n- Cross-Boundary Coherence: Ralph Review Cycle 100.\n- Story Quality: Ralph Review Cycle 101.",
                "## Residual documentation risk\n\nResidual documentation risk is tracked for pending security closeout.",
            ]
        )
        return f"# Forge Seed Documentation Closeout\n\nStatus: Completed Closeout\n\n{sections}"

    def write_closeout(self, root: Path, content: str | None = None) -> None:
        path = root / self.closeout_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content or self.valid_closeout(), encoding="utf-8")

    def test_validate_documentation_closeout_reports_missing_surface(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = validate_documentation_closeout(root)

        self.assertIn(
            CheckResult(
                f"documentation_closeout:path:{self.closeout_path}",
                False,
                "missing",
                self.closeout_path,
            ),
            results,
        )

    def test_validate_documentation_closeout_accepts_complete_surface(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_closeout(root)

            results = validate_documentation_closeout(root)

        self.assertTrue(all(result.ok for result in results), results)

    def test_validate_documentation_closeout_requires_sections(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_closeout(
                root,
                self.valid_closeout().replace(
                    "## Stale-language cleanup result\n\nStale initial-state language was searched and resolved.\n\n",
                    "",
                ),
            )

            results = validate_documentation_closeout(root)

        self.assertIn(
            CheckResult(
                f"documentation_closeout:section:{self.closeout_path}:Stale-language cleanup result",
                False,
                "missing section: Stale-language cleanup result",
                self.closeout_path,
            ),
            results,
        )

    def test_validate_documentation_closeout_rejects_incomplete_review_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_closeout(root, self.valid_closeout().replace("Status: Completed Closeout", "Status: In Progress"))

            results = validate_documentation_closeout(root)

        self.assertIn(
            CheckResult(
                f"documentation_closeout:status:{self.closeout_path}",
                False,
                "missing completed closeout status",
                self.closeout_path,
            ),
            results,
        )

    def test_validate_documentation_closeout_rejects_unresolved_review_placeholder(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_closeout(
                root,
                self.valid_closeout()
                + "\n\nThis final documentation closeout summary still requires review. Record that review result here after it completes.\n",
            )

            results = validate_documentation_closeout(root)

        self.assertIn(
            CheckResult(
                f"documentation_closeout:review:{self.closeout_path}",
                False,
                "contains unresolved review placeholder",
                self.closeout_path,
            ),
            results,
        )

    def test_validate_documentation_closeout_rejects_pending_review_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_closeout(
                root,
                self.valid_closeout().replace(
                    "- Documentation closeout: Ralph Review Cycle 99.",
                    "- Documentation closeout: pending.",
                ),
            )

            results = validate_documentation_closeout(root)

        self.assertIn(
            CheckResult(
                f"documentation_closeout:review:{self.closeout_path}:Documentation closeout",
                False,
                "review status must name a Ralph Review Cycle: Documentation closeout",
                self.closeout_path,
            ),
            results,
        )

    def test_validate_documentation_closeout_requires_closeout_evidence(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            sections = "\n".join(f"## {section}\n\nContent.\n" for section in self.required_sections)
            self.write_closeout(root, f"# Forge Seed Documentation Closeout\n\nStatus: Completed Closeout\n\n{sections}")

            results = validate_documentation_closeout(root)

        self.assertIn(
            CheckResult(
                f"documentation_closeout:evidence:{self.closeout_path}:Cross-Boundary Coherence",
                False,
                "missing evidence: Cross-Boundary Coherence",
                self.closeout_path,
            ),
            results,
        )

    def test_validate_documentation_closeout_requires_full_scope_evidence(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_closeout(root, self.valid_closeout().replace("`specs/*.md`, ", ""))

            results = validate_documentation_closeout(root)

        self.assertIn(
            CheckResult(
                f"documentation_closeout:evidence:{self.closeout_path}:specs/*.md",
                False,
                "missing evidence: specs/*.md",
                self.closeout_path,
            ),
            results,
        )

    def test_validate_documentation_closeout_requires_completion_window_evidence(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_closeout(
                root,
                self.valid_closeout().replace(
                    "Portable workflow capture says a branch-push pause does not close the capture. Full Seed completion requires a merged Seed. An explicit hold or cancellation continues capture through an unmerged-state hand-back and should record the unmerged state directly.",
                    "Portable workflow capture is recorded.",
                ),
            )

            results = validate_documentation_closeout(root)

        self.assertIn(
            CheckResult(
                f"documentation_closeout:evidence:{self.closeout_path}:branch-push pause does not close the capture",
                False,
                "missing evidence: branch-push pause does not close the capture",
                self.closeout_path,
            ),
            results,
        )

    def test_validate_documentation_closeout_requires_hold_cancel_condition(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_closeout(
                root,
                self.valid_closeout().replace(
                    "An explicit hold or cancellation continues capture through an unmerged-state hand-back and should record the unmerged state directly.",
                    "A stopped Seed keeps an unmerged-state hand-back.",
                ),
            )

            results = validate_documentation_closeout(root)

        self.assertIn(
            CheckResult(
                f"documentation_closeout:evidence:{self.closeout_path}:An explicit hold or cancellation continues",
                False,
                "missing evidence: An explicit hold or cancellation continues",
                self.closeout_path,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                f"documentation_closeout:evidence:{self.closeout_path}:record the unmerged state directly",
                False,
                "missing evidence: record the unmerged state directly",
                self.closeout_path,
            ),
            results,
        )

    def test_validate_documentation_closeout_accepts_wrapped_completion_window_evidence(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_closeout(
                root,
                self.valid_closeout()
                .replace("Full Seed completion requires a merged Seed.", "Full Seed completion\nrequires a merged Seed.")
                .replace("unmerged-state hand-back and should record", "unmerged-state\nhand-back and should record"),
            )

            results = validate_documentation_closeout(root)

        self.assertTrue(all(result.ok for result in results), results)

    def test_run_requires_documentation_closeout_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = run(root)

        self.assertIn(
            CheckResult(f"required_path:{self.closeout_path}", False, "missing", self.closeout_path),
            results,
        )


class SecurityCloseoutValidationTests(unittest.TestCase):
    closeout_path = "docs/security/forge-seed-closeout.md"
    required_sections = [
        "Scan scope",
        "Commands",
        "Scan artifact disposition",
        "Report disposition",
        "Findings disposition",
        "Hardening changes",
        "Re-validation status",
        "Deferred-risk tracking",
    ]

    def valid_closeout(self) -> str:
        sections = "\n\n".join(
            [
                "## Scan scope\n\nMerge-base-to-working-tree Forge Seed diff, including committed, staged, unstaged, and untracked intended files.",
                "## Commands\n\n- `python3.14 -m unittest tests/test_validate_forge_seed.py`\n- `python3.14 tools/validate_forge_seed.py`\n- Codex Security phase sequence: threat modeling, finding discovery, validation, attack-path analysis, final report.\n\nValidation and attack-path analysis were not separately run because finding discovery produced no technically plausible candidates.",
                "## Scan artifact disposition\n\nThe raw bundle is ephemeral scratch evidence, not a tracked project artifact, not portable review evidence, and not a standing source of project truth.\n\nArtifact durability classification: instance-scoped scratch evidence. Durable security evidence is this closeout summary.",
                "## Report disposition\n\nThe raw report is not committed and should not be cited as reusable project doctrine.",
                "## Findings disposition\n\nNo reportable findings. Suppressed findings: none.",
                "## Hardening changes\n\nNo hardening changes required.",
                "## Re-validation status\n\nRe-validation passed for unit tests, seed validator, and security closeout checks.",
                "## Deferred-risk tracking\n\nDeferred risks: none.",
            ]
        )
        return f"# Forge Seed Security Closeout\n\nStatus: Completed Security Closeout\n\n{sections}"

    def write_closeout(self, root: Path, content: str | None = None) -> None:
        path = root / self.closeout_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content or self.valid_closeout(), encoding="utf-8")

    def test_validate_security_closeout_reports_missing_surface(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = validate_security_closeout(root)

        self.assertIn(
            CheckResult(
                f"security_closeout:path:{self.closeout_path}",
                False,
                "missing",
                self.closeout_path,
            ),
            results,
        )

    def test_validate_security_closeout_accepts_complete_surface(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_closeout(root)

            results = validate_security_closeout(root)

        self.assertTrue(all(result.ok for result in results), results)

    def test_validate_security_closeout_requires_sections(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_closeout(
                root,
                self.valid_closeout().replace("## Findings disposition\n\nNo reportable findings. Suppressed findings: none.\n\n", ""),
            )

            results = validate_security_closeout(root)

        self.assertIn(
            CheckResult(
                f"security_closeout:section:{self.closeout_path}:Findings disposition",
                False,
                "missing section: Findings disposition",
                self.closeout_path,
            ),
            results,
        )

    def test_validate_security_closeout_requires_completed_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_closeout(root, self.valid_closeout().replace("Status: Completed Security Closeout", "Status: In Progress"))

            results = validate_security_closeout(root)

        self.assertIn(
            CheckResult(
                f"security_closeout:status:{self.closeout_path}",
                False,
                "missing completed security closeout status",
                self.closeout_path,
            ),
            results,
        )

    def test_validate_security_closeout_requires_evidence(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            sections = "\n".join(f"## {section}\n\nContent.\n" for section in self.required_sections)
            self.write_closeout(root, f"# Forge Seed Security Closeout\n\nStatus: Completed Security Closeout\n\n{sections}")

            results = validate_security_closeout(root)

        self.assertIn(
            CheckResult(
                f"security_closeout:evidence:{self.closeout_path}:not a tracked project artifact",
                False,
                "missing evidence: not a tracked project artifact",
                self.closeout_path,
            ),
            results,
        )

    def test_validate_security_closeout_accepts_completed_phase_disposition(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_closeout(
                root,
                self.valid_closeout().replace(
                    "Validation and attack-path analysis were not separately run because finding discovery produced no technically plausible candidates.",
                    "Validation phase completed. Attack-path analysis completed.",
                ),
            )

            results = validate_security_closeout(root)

        self.assertTrue(all(result.ok for result in results), results)

    def test_validate_security_closeout_requires_phase_disposition(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_closeout(
                root,
                self.valid_closeout().replace(
                    "\n\nValidation and attack-path analysis were not separately run because finding discovery produced no technically plausible candidates.",
                    "",
                ),
            )

            results = validate_security_closeout(root)

        self.assertIn(
            CheckResult(
                f"security_closeout:evidence:{self.closeout_path}:validation and attack-path disposition",
                False,
                "missing validation and attack-path disposition",
                self.closeout_path,
            ),
            results,
        )

    def test_run_requires_security_closeout_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = run(root)

        self.assertIn(
            CheckResult(f"required_path:{self.closeout_path}", False, "missing", self.closeout_path),
            results,
        )


class ProjectionDraftValidationTests(unittest.TestCase):
    projection_path = "docs/closeout/forge-seed-projection-drafts.md"
    plan_path = "docs/plans/2026-05-03-forge-seed.md"

    def valid_projection_drafts(self) -> str:
        return textwrap.dedent(
            """
            # Forge Seed Projection Drafts

            Status: Review Draft

            Projection state: PR published; issue projection pending.

            ## Published PRD Issue Draft

            Projected commit SHA: `TO_CAPTURE_IMMEDIATELY_BEFORE_ISSUE_PUBLICATION`

            Report disposition: recorded in `docs/security/forge-seed-closeout.md`.

            Documentation closeout review: Ralph Review Cycle 99.

            Cross-Boundary Coherence review: `TO_FILL_AFTER_CLEAN_REVIEW`

            Story Quality review: `TO_FILL_AFTER_CLEAN_REVIEW`

            ## Published Pull Request

            Published PR: <https://github.com/nisavid/agent-armory/pull/1>

            Documentation closeout: Ralph Review Cycle 99.

            ## Release Draft

            No release publication is planned for the Forge Seed.

            ## Handoff Draft

            No separate handoff publication is required during PR review.

            The Seed Closeout Addendum remains open through PR review orchestration, merge, merge cleanup, external surface reconciliation, and final hand-back.
            """
        ).strip()

    def write_projection_drafts(self, root: Path, content: str | None = None) -> None:
        path = root / self.projection_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content or self.valid_projection_drafts(), encoding="utf-8")

    def write_plan_with_step7(self, root: Path, checked: bool) -> None:
        path = root / self.plan_path
        path.parent.mkdir(parents=True, exist_ok=True)
        checkbox = "x" if checked else " "
        path.write_text(
            f"# Plan\n\n- [{checkbox}] **Step 7: Ralph-review closeout coherence and quality**\n",
            encoding="utf-8",
        )

    def test_validate_projection_drafts_reports_missing_surface(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = validate_projection_drafts(root)

        self.assertIn(
            CheckResult(
                f"projection_drafts:path:{self.projection_path}",
                False,
                "missing",
                self.projection_path,
            ),
            results,
        )

    def test_validate_projection_drafts_accepts_complete_surface(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_projection_drafts(root)

            results = validate_projection_drafts(root)

        self.assertTrue(all(result.ok for result in results), results)

    def test_validate_projection_drafts_accepts_final_story_review_cycles_after_step7(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_plan_with_step7(root, checked=True)
            self.write_projection_drafts(
                root,
                self.valid_projection_drafts()
                .replace("Cross-Boundary Coherence review: `TO_FILL_AFTER_CLEAN_REVIEW`", "Cross-Boundary Coherence review: Ralph Review Cycle 53.")
                .replace("Story Quality review: `TO_FILL_AFTER_CLEAN_REVIEW`", "Story Quality review: Ralph Review Cycle 54."),
            )

            results = validate_projection_drafts(root)

        self.assertTrue(all(result.ok for result in results), results)

    def test_validate_projection_drafts_requires_sections(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_projection_drafts(
                root,
                self.valid_projection_drafts().replace(
                    "\n\n## Published Pull Request\n\nPublished PR: <https://github.com/nisavid/agent-armory/pull/1>\n\nDocumentation closeout: Ralph Review Cycle 99.",
                    "",
                ),
            )

            results = validate_projection_drafts(root)

        self.assertIn(
            CheckResult(
                f"projection_drafts:section:{self.projection_path}:Published Pull Request",
                False,
                "missing section: Published Pull Request",
                self.projection_path,
            ),
            results,
        )

    def test_validate_projection_drafts_requires_security_report_disposition_field(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_projection_drafts(
                root,
                self.valid_projection_drafts().replace(
                    "\nReport disposition: recorded in `docs/security/forge-seed-closeout.md`.\n",
                    "",
                ),
            )

            results = validate_projection_drafts(root)

        self.assertIn(
            CheckResult(
                f"projection_drafts:evidence:{self.projection_path}:Report disposition: recorded in `docs/security/forge-seed-closeout.md`",
                False,
                "missing evidence: Report disposition: recorded in `docs/security/forge-seed-closeout.md`",
                self.projection_path,
            ),
            results,
        )

    def test_validate_projection_drafts_rejects_unresolved_documentation_closeout_placeholder(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_projection_drafts(
                root,
                self.valid_projection_drafts().replace(
                    "Documentation closeout review: Ralph Review Cycle 99.",
                    "Review result: `TO_FILL_AFTER_FINAL_CLEAN_DOCUMENTATION_CLOSEOUT_REVIEW`",
                ),
            )

            results = validate_projection_drafts(root)

        self.assertIn(
            CheckResult(
                f"projection_drafts:evidence:{self.projection_path}:documentation closeout review",
                False,
                "documentation closeout review must name a Ralph Review Cycle",
                self.projection_path,
            ),
            results,
        )

    def test_validate_projection_drafts_rejects_pending_story_review_placeholders_after_step7(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_plan_with_step7(root, checked=True)
            self.write_projection_drafts(root)

            results = validate_projection_drafts(root)

        self.assertIn(
            CheckResult(
                f"projection_drafts:evidence:{self.projection_path}:story closeout reviews",
                False,
                "completed story closeout must name Cross-Boundary Coherence and Story Quality Ralph Review cycles",
                self.projection_path,
            ),
            results,
        )

    def test_validate_projection_drafts_rejects_final_closeout_passed_with_pending_story_reviews(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_projection_drafts(
                root,
                self.valid_projection_drafts()
                + "\n\n- `python3.14 tools/validate_forge_seed.py --final-closeout`: passed.\n",
            )

            results = validate_projection_drafts(root)

        self.assertIn(
            CheckResult(
                f"projection_drafts:evidence:{self.projection_path}:final closeout status",
                False,
                "projection drafts must not claim final-closeout passed while story-review placeholders remain",
                self.projection_path,
            ),
            results,
        )

    def test_validate_projection_drafts_rejects_conflicting_story_review_cycles(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_projection_drafts(
                root,
                self.valid_projection_drafts()
                .replace("Cross-Boundary Coherence review: `TO_FILL_AFTER_CLEAN_REVIEW`", "Cross-Boundary Coherence review: Ralph Review Cycle 101.")
                .replace("Story Quality review: `TO_FILL_AFTER_CLEAN_REVIEW`", "Story Quality review: Ralph Review Cycle 102.")
                + "\n\n## PR Reviews\n\n- Cross-Boundary Coherence: Ralph Review Cycle 71.\n- Story Quality: Ralph Review Cycle 72.\n",
            )

            results = validate_projection_drafts(root)

        self.assertIn(
            CheckResult(
                f"projection_drafts:evidence:{self.projection_path}:cross-boundary coherence review consistency",
                False,
                "projection drafts must not publish conflicting cross-boundary coherence review cycles",
                self.projection_path,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                f"projection_drafts:evidence:{self.projection_path}:story quality review consistency",
                False,
                "projection drafts must not publish conflicting story quality review cycles",
                self.projection_path,
            ),
            results,
        )

    def test_validate_final_closeout_rejects_pending_story_review_placeholders_without_step7_dependency(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_plan_with_step7(root, checked=False)
            self.write_projection_drafts(root)

            results = validate_final_closeout(root)

        self.assertIn(
            CheckResult(
                f"final_closeout:evidence:{self.projection_path}:story closeout reviews",
                False,
                "final closeout must name Cross-Boundary Coherence and Story Quality Ralph Review cycles",
                self.projection_path,
            ),
            results,
        )

    def test_validate_final_closeout_rejects_clean_story_review_evidence_when_plan_step_open(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_plan_with_step7(root, checked=False)
            self.write_projection_drafts(
                root,
                self.valid_projection_drafts()
                .replace("Cross-Boundary Coherence review: `TO_FILL_AFTER_CLEAN_REVIEW`", "Cross-Boundary Coherence review: Ralph Review Cycle 53.")
                .replace("Story Quality review: `TO_FILL_AFTER_CLEAN_REVIEW`", "Story Quality review: Ralph Review Cycle 54."),
            )

            results = validate_final_closeout(root)

        self.assertIn(
            CheckResult(
                f"final_closeout:evidence:{self.plan_path}:story closeout reviews",
                False,
                "final closeout requires completed story closeout review step in the plan",
                self.plan_path,
            ),
            results,
        )

    def test_validate_final_closeout_rejects_host_local_artifact_paths_in_projection_drafts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_projection_drafts(
                root,
                self.valid_projection_drafts()
                .replace("Cross-Boundary Coherence review: `TO_FILL_AFTER_CLEAN_REVIEW`", "Cross-Boundary Coherence review: Ralph Review Cycle 53.")
                .replace("Story Quality review: `TO_FILL_AFTER_CLEAN_REVIEW`", "Story Quality review: Ralph Review Cycle 54.")
                + "\n\nScan report: `/tmp/codex-security-scans/forge-seed/report.md`\n",
            )

            results = validate_final_closeout(root)

        self.assertIn(
            CheckResult(
                f"final_closeout:evidence:{self.projection_path}:portable evidence",
                False,
                "external projection drafts must not publish host-local or scratch artifact paths",
                self.projection_path,
            ),
            results,
        )

    def test_validate_final_closeout_rejects_generic_scratch_artifact_paths_in_projection_drafts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_projection_drafts(
                root,
                self.valid_projection_drafts()
                .replace("Cross-Boundary Coherence review: `TO_FILL_AFTER_CLEAN_REVIEW`", "Cross-Boundary Coherence review: Ralph Review Cycle 53.")
                .replace("Story Quality review: `TO_FILL_AFTER_CLEAN_REVIEW`", "Story Quality review: Ralph Review Cycle 54.")
                + "\n\nScratch report: `/home/example/project/security-scan/report.md`\n",
            )

            results = validate_final_closeout(root)

        self.assertIn(
            CheckResult(
                f"final_closeout:evidence:{self.projection_path}:portable evidence",
                False,
                "external projection drafts must not publish host-local or scratch artifact paths",
                self.projection_path,
            ),
            results,
        )

    def test_validate_final_closeout_rejects_hard_coded_validation_counts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_projection_drafts(
                root,
                self.valid_projection_drafts()
                .replace("Cross-Boundary Coherence review: `TO_FILL_AFTER_CLEAN_REVIEW`", "Cross-Boundary Coherence review: Ralph Review Cycle 53.")
                .replace("Story Quality review: `TO_FILL_AFTER_CLEAN_REVIEW`", "Story Quality review: Ralph Review Cycle 54.")
                + "\n\n- `python3.14 -m unittest tests/test_validate_forge_seed.py`: 264 tests passed.\n",
            )

            results = validate_final_closeout(root)

        self.assertIn(
            CheckResult(
                f"final_closeout:evidence:{self.projection_path}:validation evidence",
                False,
                "final closeout evidence should cite validation commands without hard-coded pass counts",
                self.projection_path,
            ),
            results,
        )

    def test_validate_final_closeout_rejects_conflicting_story_review_cycles(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_plan_with_step7(root, checked=True)
            self.write_projection_drafts(
                root,
                self.valid_projection_drafts()
                .replace("Cross-Boundary Coherence review: `TO_FILL_AFTER_CLEAN_REVIEW`", "Cross-Boundary Coherence review: Ralph Review Cycle 101.")
                .replace("Story Quality review: `TO_FILL_AFTER_CLEAN_REVIEW`", "Story Quality review: Ralph Review Cycle 102.")
                + "\n\n## PR Reviews\n\n- Cross-Boundary Coherence: Ralph Review Cycle 71.\n- Story Quality: Ralph Review Cycle 72.\n",
            )

            results = validate_final_closeout(root)

        self.assertIn(
            CheckResult(
                f"final_closeout:evidence:{self.projection_path}:cross-boundary coherence review consistency",
                False,
                "final closeout must not publish conflicting cross-boundary coherence review cycles",
                self.projection_path,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                f"final_closeout:evidence:{self.projection_path}:story quality review consistency",
                False,
                "final closeout must not publish conflicting story quality review cycles",
                self.projection_path,
            ),
            results,
        )

    def test_validate_final_closeout_accepts_clean_story_review_evidence(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_plan_with_step7(root, checked=True)
            self.write_projection_drafts(
                root,
                self.valid_projection_drafts()
                .replace("Cross-Boundary Coherence review: `TO_FILL_AFTER_CLEAN_REVIEW`", "Cross-Boundary Coherence review: Ralph Review Cycle 53.")
                .replace("Story Quality review: `TO_FILL_AFTER_CLEAN_REVIEW`", "Story Quality review: Ralph Review Cycle 54."),
            )

            results = validate_final_closeout(root)

        self.assertEqual([], [result for result in results if not result.ok])
        self.assertIn(CheckResult("final_closeout:forge-seed", True, "ready", self.projection_path), results)

    def test_validate_projection_drafts_requires_open_capture_pause_handoff(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_projection_drafts(
                root,
                self.valid_projection_drafts().replace(
                    "The Seed Closeout Addendum remains open through PR review orchestration, merge, merge cleanup, external surface reconciliation, and final hand-back.",
                    "The Seed Closeout Addendum remains open through PR review orchestration, merge, and merge cleanup.",
                ),
            )

            results = validate_projection_drafts(root)

        self.assertIn(
            CheckResult(
                f"projection_drafts:evidence:{self.projection_path}:Seed Closeout Addendum remains open through PR review orchestration, merge, merge cleanup, external surface reconciliation, and final hand-back",
                False,
                "missing evidence: Seed Closeout Addendum remains open through PR review orchestration, merge, merge cleanup, external surface reconciliation, and final hand-back",
                self.projection_path,
            ),
            results,
        )

    def test_run_requires_projection_drafts_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = run(root)

        self.assertIn(
            CheckResult(f"required_path:{self.projection_path}", False, "missing", self.projection_path),
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

    def test_validate_markdown_links_rejects_symlinked_markdown_source(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            outside = root / "outside.md"
            outside.write_text("[missing](missing.md)\n", encoding="utf-8")
            (root / "docs/source.md").symlink_to(outside)

            results = validate_markdown_links(root)

        self.assertIn(
            CheckResult(
                "markdown_file:docs/source.md",
                False,
                "markdown file path contains symlink",
                "docs/source.md",
            ),
            results,
        )

    def test_validate_markdown_links_rejects_symlinked_link_target(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            (root / "docs/start.md").write_text("[target](target.md)\n", encoding="utf-8")
            (root / "docs/real.md").write_text("# Real\n", encoding="utf-8")
            (root / "docs/target.md").symlink_to(root / "docs/real.md")

            results = validate_markdown_links(root)

        self.assertIn(
            CheckResult(
                "markdown_link:docs/start.md:target.md",
                False,
                "target missing",
                "docs/start.md",
            ),
            results,
        )

    def test_validate_markdown_links_checks_reference_definition_targets(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            (root / "docs/start.md").write_text("[framework]: missing.md\n", encoding="utf-8")

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

    def test_validate_markdown_links_uses_first_duplicate_reference_definition(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            (root / "docs/start.md").write_text(
                textwrap.dedent(
                    """
                    [guide][ref]

                    [ref]: missing.md
                    [ref]: exists.md
                    """
                ),
                encoding="utf-8",
            )
            (root / "docs/exists.md").write_text("# Exists\n", encoding="utf-8")

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

    def test_validate_markdown_links_rejects_undefined_reference_uses(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            (root / "docs/start.md").write_text("[guide][missing]\n", encoding="utf-8")

            results = validate_markdown_links(root)

        self.assertIn(
            CheckResult(
                "markdown_reference:docs/start.md:missing",
                False,
                "undefined reference",
                "docs/start.md",
            ),
            results,
        )


class HarnessCatalogTests(unittest.TestCase):
    def catalog_entry(self, harness_id: str, overrides: dict[str, object] | None = None) -> dict[str, object]:
        entry: dict[str, object] = {
            "display_name": harness_id,
            "sources": [
                {"url": f"https://example.com/{harness_id}", "kind": "first_party", "claim_scope": "docs"},
            ],
            "evidence": "documentation-supported",
            "checked_version": "source-documented",
            "version_basis": "official release or docs page",
            "uncertainty": "Fixture uncertainty.",
            "components": ["skills"],
            "summary_scheduling": "Fixture scheduling summary.",
            "scheduling": "manual",
            "limitations": "Fixture limitation.",
            "refresh_notes": "Fixture refresh note.",
            "local_observations": [],
        }
        if overrides:
            entry.update(overrides)
        return entry

    def toml_value(self, value: object, indent: str = "") -> str:
        if isinstance(value, str):
            return json.dumps(value)
        if isinstance(value, list):
            if not value:
                return "[]"
            if all(isinstance(item, str) for item in value):
                return "[" + ", ".join(json.dumps(item) for item in value) + "]"
            items = []
            for item in value:
                if isinstance(item, dict):
                    fields = ", ".join(f"{key} = {self.toml_value(field)}" for key, field in item.items())
                    items.append(f"{indent}  {{ {fields} }}")
            return "[\n" + ",\n".join(items) + f"\n{indent}]"
        raise TypeError(f"unsupported TOML fixture value: {value!r}")

    def write_catalog(
        self,
        root: Path,
        entries: dict[str, dict[str, object]] | None = None,
        *,
        include_checked_at: bool = True,
    ) -> None:
        catalog = root / "docs/harness-capabilities.toml"
        catalog.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = []
        if include_checked_at:
            lines.append('checked_at = "2026-05-03T00:00:00-04:00"')
            lines.append("")
        for harness_id, entry in (entries or {harness_id: self.catalog_entry(harness_id) for harness_id in REQUIRED_HARNESSES}).items():
            lines.append(f"[harness.{harness_id}]")
            for key, value in entry.items():
                lines.append(f"{key} = {self.toml_value(value)}")
            lines.append("")
        catalog.write_text("\n".join(lines), encoding="utf-8")
        self.write_catalog_markdown(root, entries)

    def write_catalog_markdown(self, root: Path, entries: dict[str, dict[str, object]] | None = None) -> None:
        markdown = root / "docs/harness-capabilities.md"
        markdown.parent.mkdir(parents=True, exist_ok=True)
        current_entries = entries or {harness_id: self.catalog_entry(harness_id) for harness_id in REQUIRED_HARNESSES}
        rows: list[str] = [
            "# Harness Capability Catalog",
            "",
            "## Harness matrix",
            "",
            "| Harness | Version basis | Checked version | Evidence | Scheduling posture |",
            "| --- | --- | --- | --- | --- |",
        ]
        for harness_id in REQUIRED_HARNESSES:
            entry = current_entries.get(harness_id, {})
            rows.append(
                " | ".join(
                    [
                        f"| {entry.get('display_name', '')}",
                        str(entry.get("version_basis", "")),
                        str(entry.get("checked_version", "")),
                        str(entry.get("evidence", "")),
                        f"{entry.get('summary_scheduling', '')} |",
                    ]
                )
            )
        markdown.write_text("\n".join(rows), encoding="utf-8")

    def test_harness_matrix_rows_extracts_rows_by_harness_name(self):
        markdown = textwrap.dedent(
            """
            # Harness Capability Catalog

            ## Harness matrix

            | Harness | Version basis | Checked version | Evidence | Scheduling posture |
            | --- | --- | --- | --- | --- |
            | Codex | GitHub releases | 0.128.0 | source-supported | App automations. |
            """
        )

        self.assertEqual(
            harness_matrix_rows(markdown)["Codex"],
            {
                "Harness": "Codex",
                "Version basis": "GitHub releases",
                "Checked version": "0.128.0",
                "Evidence": "source-supported",
                "Scheduling posture": "App automations.",
            },
        )

    def test_validate_harness_catalog_requires_evidence_metadata(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_catalog(root)

            results = validate_harness_catalog(root)

        self.assertTrue(all(result.ok for result in results), results)

    def test_validate_harness_catalog_rejects_missing_required_harness(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_catalog(root, {"codex": self.catalog_entry("codex")})

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

    def test_validate_harness_catalog_rejects_missing_checked_at(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_catalog(root, include_checked_at=False)

            results = validate_harness_catalog(root)

        self.assertIn(
            CheckResult("harness_catalog:checked_at", False, "missing checked_at", "docs/harness-capabilities.toml"),
            results,
        )

    def test_validate_harness_catalog_rejects_unknown_harness_ids(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            entries = {harness_id: self.catalog_entry(harness_id) for harness_id in REQUIRED_HARNESSES}
            entries["unknown"] = self.catalog_entry("unknown")
            self.write_catalog(root, entries)

            results = validate_harness_catalog(root)

        self.assertIn(
            CheckResult("harness_catalog:coverage", False, "unknown harness ids: unknown", "docs/harness-capabilities.toml"),
            results,
        )

    def test_validate_harness_catalog_rejects_missing_scalar_fields(self):
        for field in [
            "display_name",
            "evidence",
            "uncertainty",
            "summary_scheduling",
            "scheduling",
            "limitations",
            "refresh_notes",
            "local_observations",
        ]:
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmpdir:
                root = Path(tmpdir)
                entries = {harness_id: self.catalog_entry(harness_id) for harness_id in REQUIRED_HARNESSES}
                entries["codex"].pop(field)
                self.write_catalog(root, entries)

                results = validate_harness_catalog(root)

            self.assertIn(
                CheckResult(f"harness_catalog:codex:{field}", False, f"missing {field}", "docs/harness-capabilities.toml"),
                results,
            )

    def test_validate_harness_catalog_rejects_empty_sources(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            entries = {harness_id: self.catalog_entry(harness_id) for harness_id in REQUIRED_HARNESSES}
            entries["codex"]["sources"] = []
            self.write_catalog(root, entries)

            results = validate_harness_catalog(root)

        self.assertIn(
            CheckResult("harness_catalog:codex:sources", False, "sources must be non-empty", "docs/harness-capabilities.toml"),
            results,
        )

    def test_validate_harness_catalog_rejects_missing_source_fields(self):
        for field in ["url", "kind", "claim_scope"]:
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmpdir:
                root = Path(tmpdir)
                entries = {harness_id: self.catalog_entry(harness_id) for harness_id in REQUIRED_HARNESSES}
                source = dict(entries["codex"]["sources"][0])
                source.pop(field)
                entries["codex"]["sources"] = [source]
                self.write_catalog(root, entries)

                results = validate_harness_catalog(root)

            self.assertIn(
                CheckResult(
                    f"harness_catalog:codex:sources:0:{field}",
                    False,
                    f"missing source {field}",
                    "docs/harness-capabilities.toml",
                ),
                results,
            )

    def test_validate_harness_catalog_rejects_invalid_source_url_scheme(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            entries = {harness_id: self.catalog_entry(harness_id) for harness_id in REQUIRED_HARNESSES}
            entries["codex"]["sources"] = [{"url": "file:///tmp/source", "kind": "first_party", "claim_scope": "docs"}]
            self.write_catalog(root, entries)

            results = validate_harness_catalog(root)

        self.assertIn(
            CheckResult(
                "harness_catalog:codex:sources:0:url",
                False,
                "source url must be http or https with a host",
                "docs/harness-capabilities.toml",
            ),
            results,
        )

    def test_validate_harness_catalog_rejects_source_url_without_host(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            entries = {harness_id: self.catalog_entry(harness_id) for harness_id in REQUIRED_HARNESSES}
            entries["codex"]["sources"] = [{"url": "https:///docs", "kind": "first_party", "claim_scope": "docs"}]
            self.write_catalog(root, entries)

            results = validate_harness_catalog(root)

        self.assertIn(
            CheckResult(
                "harness_catalog:codex:sources:0:url",
                False,
                "source url must be http or https with a host",
                "docs/harness-capabilities.toml",
            ),
            results,
        )

    def test_validate_harness_catalog_rejects_invalid_source_kind(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            entries = {harness_id: self.catalog_entry(harness_id) for harness_id in REQUIRED_HARNESSES}
            entries["codex"]["sources"] = [{"url": "https://example.com", "kind": "local_observation", "claim_scope": "docs"}]
            self.write_catalog(root, entries)

            results = validate_harness_catalog(root)

        self.assertIn(
            CheckResult(
                "harness_catalog:codex:sources:0:kind",
                False,
                "source kind must be first_party or third_party_fallback",
                "docs/harness-capabilities.toml",
            ),
            results,
        )

    def test_validate_harness_catalog_rejects_invalid_evidence_category(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            entries = {harness_id: self.catalog_entry(harness_id) for harness_id in REQUIRED_HARNESSES}
            entries["codex"]["evidence"] = "rumor"
            self.write_catalog(root, entries)

            results = validate_harness_catalog(root)

        self.assertIn(
            CheckResult("harness_catalog:codex:evidence", False, "invalid evidence category", "docs/harness-capabilities.toml"),
            results,
        )

    def test_validate_harness_catalog_requires_version_or_basis(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            entries = {harness_id: self.catalog_entry(harness_id) for harness_id in REQUIRED_HARNESSES}
            entries["codex"].pop("checked_version")
            entries["codex"].pop("version_basis")
            self.write_catalog(root, entries)

            results = validate_harness_catalog(root)

        self.assertIn(
            CheckResult(
                "harness_catalog:codex:version",
                False,
                "missing checked_version or version_basis",
                "docs/harness-capabilities.toml",
            ),
            results,
        )

    def test_validate_harness_catalog_rejects_empty_components(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            entries = {harness_id: self.catalog_entry(harness_id) for harness_id in REQUIRED_HARNESSES}
            entries["codex"]["components"] = []
            self.write_catalog(root, entries)

            results = validate_harness_catalog(root)

        self.assertIn(
            CheckResult("harness_catalog:codex:components", False, "components must be non-empty", "docs/harness-capabilities.toml"),
            results,
        )

    def test_validate_harness_catalog_accepts_fallback_source_kind_as_labeling(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            entries = {harness_id: self.catalog_entry(harness_id) for harness_id in REQUIRED_HARNESSES}
            entries["codex"]["sources"] = [{"url": "https://example.com", "kind": "third_party_fallback", "claim_scope": "metadata"}]
            entries["codex"]["uncertainty"] = "Fixture uncertainty."
            entries["codex"]["refresh_notes"] = "Fixture refresh note."
            self.write_catalog(root, entries)

            results = validate_harness_catalog(root)

        self.assertNotIn("harness_catalog:codex:fallback", {result.name for result in results})

    def test_validate_harness_catalog_requires_local_observations_as_separate_list(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            entries = {harness_id: self.catalog_entry(harness_id) for harness_id in REQUIRED_HARNESSES}
            entries["codex"]["sources"] = [{"url": "https://example.com", "kind": "local_observation", "claim_scope": "cli"}]
            self.write_catalog(root, entries)

            results = validate_harness_catalog(root)

        self.assertIn(
            CheckResult(
                "harness_catalog:codex:sources:0:kind",
                False,
                "source kind must be first_party or third_party_fallback",
                "docs/harness-capabilities.toml",
            ),
            results,
        )

    def test_validate_harness_catalog_rejects_non_string_local_observations(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            entries = {harness_id: self.catalog_entry(harness_id) for harness_id in REQUIRED_HARNESSES}
            entries["codex"]["local_observations"] = [{"command": "codex --version"}]
            self.write_catalog(root, entries)

            results = validate_harness_catalog(root)

        self.assertIn(
            CheckResult(
                "harness_catalog:codex:local_observations",
                False,
                "local_observations must be a list of strings",
                "docs/harness-capabilities.toml",
            ),
            results,
        )

    def test_validate_harness_catalog_checks_markdown_summary_sync(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_catalog(root)
            markdown = root / "docs/harness-capabilities.md"
            self.write_catalog_markdown(root)

            results = validate_harness_catalog(root)

        self.assertNotIn("harness_catalog_markdown:codex:checked_version", {result.name for result in results})

    def test_validate_harness_catalog_rejects_stale_markdown_summary(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_catalog(root)
            markdown = root / "docs/harness-capabilities.md"
            markdown.write_text(
                textwrap.dedent(
                    """
                    # Harness Capability Catalog

                    ## Harness matrix

                    | Harness | Version basis | Checked version | Evidence | Scheduling posture |
                    | --- | --- | --- | --- | --- |
                    | codex | official release or docs page | stale-version | documentation-supported | Fixture scheduling summary. |
                    """
                ),
                encoding="utf-8",
            )

            results = validate_harness_catalog(root)

        self.assertIn(
            CheckResult(
                "harness_catalog_markdown:codex:checked_version",
                False,
                "markdown matrix Checked version mismatch: expected source-documented",
                "docs/harness-capabilities.md",
            ),
            results,
        )

    def test_validate_harness_catalog_rejects_wrong_row_even_when_value_appears_elsewhere(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_catalog(root)
            markdown = root / "docs/harness-capabilities.md"
            markdown.write_text(
                textwrap.dedent(
                    """
                    # Harness Capability Catalog

                    ## Harness matrix

                    | Harness | Version basis | Checked version | Evidence | Scheduling posture |
                    | --- | --- | --- | --- | --- |
                    | codex | official release or docs page | stale-version | documentation-supported | Fixture scheduling summary. |
                    | claude_code | official release or docs page | source-documented | documentation-supported | Fixture scheduling summary. |
                    """
                ),
                encoding="utf-8",
            )

            results = validate_harness_catalog(root)

        self.assertIn(
            CheckResult(
                "harness_catalog_markdown:codex:checked_version",
                False,
                "markdown matrix Checked version mismatch: expected source-documented",
                "docs/harness-capabilities.md",
            ),
            results,
        )


class TemplateValidationTests(unittest.TestCase):
    required_template_paths = [
        "templates/capability-card.md",
        "templates/interface-decision-record.md",
        "templates/skill/README.md",
        "templates/skill/SKILL.md",
        "templates/hook/README.md",
        "templates/hook/hook.ts",
        "templates/agents/README.md",
        "templates/agents/profile.toml",
        "templates/plugin/README.md",
        "templates/plugin/manifest.toml",
        "templates/script/README.md",
        "templates/script/validate-example.py",
        "templates/mcp/README.md",
        "templates/mcp/tool-spec.md",
        "templates/config/README.md",
        "templates/config/example.toml",
        "templates/security-review.md",
        "templates/context-budget-review.md",
    ]
    template_readmes = [
        "templates/skill/README.md",
        "templates/hook/README.md",
        "templates/agents/README.md",
        "templates/plugin/README.md",
        "templates/script/README.md",
        "templates/mcp/README.md",
        "templates/config/README.md",
    ]
    root_template_files = [
        "templates/capability-card.md",
        "templates/interface-decision-record.md",
        "templates/security-review.md",
        "templates/context-budget-review.md",
    ]
    readme_sections = ["Purpose", "Required fields", "Optional fields", "Common mistakes", "Validation expectations"]
    skill_sections = [
        "Status",
        "Use when",
        "Do not use when",
        "Preflight",
        "Procedure",
        "Output contract",
        "Failure handling",
        "Safety and policy notes",
    ]

    def write_template(self, root: Path, relative_path: str, content: str) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")

    def valid_readme(self, title: str) -> str:
        return f"""\
        # {title} Template

        ## Purpose

        Content.

        ## Required fields

        Content.

        ## Optional fields

        Content.

        ## Common mistakes

        Content.

        ## Validation expectations

        Content.
        """

    def write_all_templates(self, root: Path) -> None:
        self.write_template(
            root,
            "templates/capability-card.md",
            """\
            # Capability Card: <name>

            Status: Template
            Promotion state: <specified|planned|implemented|validated|example|published>

            ## Purpose

            ## Vision alignment

            ## Users

            ## Target harnesses

            ## Risks

            ## External systems

            ## Side effects

            Classify external disclosure here.

            ## Needed Harness Components

            ## Hard rules

            ## Deterministic checks

            ## Output contract

            ## Failure modes

            ## Evidence

            ## Open questions
            """,
        )
        self.write_template(
            root,
            "templates/interface-decision-record.md",
            """\
            # Interface Decision Record: <capability>

            Status: Template

            ## Requirement

            ## Vision alignment

            ## Decision

            ## Chosen surface

            ## Rationale

            ## Evidence category

            ## Harness-specific projection

            ## Alternatives rejected

            ## Risks

            ## Maintenance notes
            """,
        )
        self.write_template(root, "templates/skill/README.md", self.valid_readme("Skill"))
        self.write_template(
            root,
            "templates/skill/SKILL.md",
            """\
            <!-- Replace this commented frontmatter before publishing:
            ---
            name: example-skill
            description: Use when a Smith needs a reusable procedural template
            ---
            -->

            # Skill: <name>

            Status: Template

            ## Use when

            ## Do not use when

            ## Preflight

            ## Procedure

            ## Output contract

            ## Failure handling

            ## Safety and policy notes
            """,
        )
        self.write_template(root, "templates/hook/README.md", self.valid_readme("Hook"))
        self.write_template(
            root,
            "templates/hook/hook.ts",
            """\
            /**
             * Side-effect classification: choose one of read-only, external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation.
             * Approval behavior: require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation.
             * Failure handling: fail closed for unsafe mutations.
             */
            export type SideEffectClassification =
              | "read-only"
              | "external disclosure"
              | "local write"
              | "network write"
              | "process execution"
              | "privileged operation"
              | "irreversible mutation";

            export const hookContract = {
              sideEffectClassification: "read-only",
              approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
              failureHandling: "fail closed for unsafe mutations",
            } as const satisfies {
              sideEffectClassification: SideEffectClassification;
              approvalBehavior: string;
              failureHandling: string;
            };

            export async function handle(event: HookEvent | null | undefined): Promise<{ allow: boolean; reason: string }> {
              if (!event || !event.kind) {
                return { allow: false, reason: "missing event kind" };
              }

              return { allow: false, reason: "template requires an explicit allow decision" };
            }
            """,
        )
        self.write_template(root, "templates/agents/README.md", self.valid_readme("Agent Profile"))
        self.write_template(
            root,
            "templates/agents/profile.toml",
            """\
            [identity]
            name = "example-agent"

            mission = "Describe the agent mission."

            [tools]
            allow = []
            deny = []

            [permissions]
            mode = "read-only"
            approval_required_for = ["external disclosure", "local write", "network write", "process execution", "privileged operation", "irreversible mutation"]

            [model]
            preference = "inherit"

            [config]
            placeholder = "value"

            [output]
            contract = "Describe the deliverable and return shape."
            format = "structured-report"
            """,
        )
        self.write_template(root, "templates/plugin/README.md", self.valid_readme("Plugin"))
        self.write_template(
            root,
            "templates/plugin/manifest.toml",
            """\
            name = "example-plugin"
            version = "0.1.0"

            [components]
            skills = []
            hooks = []
            tools = []

            [ownership]
            owner = "human"
            source = "repo"

            [permissions]
            required = []
            approval_required_for = ["external disclosure", "local write", "network write", "process execution", "privileged operation", "irreversible mutation"]
            """,
        )
        self.write_template(root, "templates/script/README.md", self.valid_readme("Script"))
        self.write_template(
            root,
            "templates/script/validate-example.py",
            """\
            #!/usr/bin/env python3.14
            \"\"\"Template validator with deterministic exit-code contract.\"\"\"

            def main() -> int:
                \"\"\"CLI entry point. Exit 0 for pass and 1 for validation failure.\"\"\"
                return 0


            if __name__ == "__main__":
                raise SystemExit(main())
            """,
        )
        self.write_template(root, "templates/mcp/README.md", self.valid_readme("MCP Tool"))
        self.write_template(
            root,
            "templates/mcp/tool-spec.md",
            """\
            # MCP/tool definition notes

            ## Purpose

            ## Read/write classification

            Classify the operation as read-only, local write, network write, external disclosure, process execution, privileged operation, or irreversible mutation.

            ## Input schema

            ## Output schema

            ## Auth source

            ## Side effects

            ## Approval requirements

            ## Rate limits

            ## Pagination

            ## Rollback and cleanup

            ## Failure modes
            """,
        )
        self.write_template(root, "templates/config/README.md", self.valid_readme("Config"))
        self.write_template(
            root,
            "templates/config/example.toml",
            """\
            [ownership]
            owner = "human"

            [autonomy]
            level = "assisted"
            agent_may_continue_sessions = false
            agent_may_initiate_project_initiatives = false

            [enabled]
            default = false

            [review]
            required_before_publish = true
            review_until_clean = true
            doc_closeout_required = true
            security_closeout_required = true

            [approval]
            required_for = ["external disclosure", "local write", "network write", "process execution", "privileged operation", "irreversible mutation"]
            """,
        )
        self.write_template(
            root,
            "templates/security-review.md",
            """\
            # Security Review

            Status: Template

            ## Scope

            ## Assets

            ## Trust boundaries

            ## Side effects

            Classify external disclosure here.

            ## Threats

            ## Controls

            ## Findings

            ## Residual risk
            """,
        )
        self.write_template(
            root,
            "templates/context-budget-review.md",
            """\
            # Context Budget Review

            Status: Template

            ## Scope

            ## Always-loaded context

            ## On-demand context

            ## Budget risks

            ## Relocation decisions

            ## Verification
            """,
        )

    def test_run_requires_all_template_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = run(root)

        for relative_path in self.required_template_paths:
            self.assertIn(
                CheckResult(f"required_path:{relative_path}", False, "missing", relative_path),
                results,
            )

    def test_validate_templates_accepts_complete_templates(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)

            results = run(root)

        self.assertTrue(all(result.ok for result in results if result.name.startswith("template:")), results)

    def test_validate_templates_requires_root_template_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(root, "templates/capability-card.md", "# Capability Card\n")

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:status:templates/capability-card.md",
                False,
                "missing Status: Template",
                "templates/capability-card.md",
            ),
            results,
        )

    def test_validate_templates_requires_root_template_sections(self):
        cases = [
            (
                "templates/capability-card.md",
                "# Capability Card: <name>\n\nStatus: Template\n\n## Purpose\n",
                "Risks",
            ),
            (
                "templates/interface-decision-record.md",
                "# Interface Decision Record: <capability>\n\nStatus: Template\n\n## Requirement\n",
                "Rationale",
            ),
            (
                "templates/security-review.md",
                "# Security Review\n\nStatus: Template\n\n## Scope\n",
                "Controls",
            ),
            (
                "templates/context-budget-review.md",
                "# Context Budget Review\n\nStatus: Template\n\n## Scope\n",
                "Verification",
            ),
        ]
        for relative_path, content, missing_section in cases:
            with self.subTest(relative_path=relative_path):
                with tempfile.TemporaryDirectory() as tmpdir:
                    root = Path(tmpdir)
                    self.write_all_templates(root)
                    self.write_template(root, relative_path, content)

                    results = run(root)

                self.assertIn(
                    CheckResult(
                        f"template:section:{relative_path}:{missing_section}",
                        False,
                        f"missing section: {missing_section}",
                        relative_path,
                    ),
                    results,
                )

    def test_validate_templates_requires_capability_card_vision_alignment(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            path = root / "templates/capability-card.md"
            self.write_template(
                root,
                "templates/capability-card.md",
                path.read_text(encoding="utf-8").replace("## Vision alignment\n\n", ""),
            )

            results = validate_templates(root)

        self.assertIn(
            CheckResult(
                name="template:section:templates/capability-card.md:Vision alignment",
                ok=False,
                detail="missing section: Vision alignment",
                path="templates/capability-card.md",
            ),
            results,
        )

    def test_validate_templates_requires_interface_decision_vision_alignment(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            path = root / "templates/interface-decision-record.md"
            self.write_template(
                root,
                "templates/interface-decision-record.md",
                path.read_text(encoding="utf-8").replace("## Vision alignment\n\n", ""),
            )

            results = validate_templates(root)

        self.assertIn(
            CheckResult(
                name="template:section:templates/interface-decision-record.md:Vision alignment",
                ok=False,
                detail="missing section: Vision alignment",
                path="templates/interface-decision-record.md",
            ),
            results,
        )

    def test_validate_templates_requires_external_disclosure_side_effect_prompt(self):
        cases = [
            "templates/capability-card.md",
            "templates/security-review.md",
        ]
        for relative_path in cases:
            with self.subTest(relative_path=relative_path):
                with tempfile.TemporaryDirectory() as tmpdir:
                    root = Path(tmpdir)
                    self.write_all_templates(root)
                    text = (root / relative_path).read_text(encoding="utf-8").replace("Classify external disclosure here.\n", "")
                    self.write_template(root, relative_path, text)

                    results = run(root)

                self.assertIn(
                    CheckResult(
                        f"template:text:{relative_path}:external disclosure",
                        False,
                        "missing external disclosure",
                        relative_path,
                    ),
                    results,
                )

    def test_validate_templates_requires_mcp_process_execution_side_effect_label(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            text = (root / "templates/mcp/tool-spec.md").read_text(encoding="utf-8").replace("process execution", "")
            self.write_template(root, "templates/mcp/tool-spec.md", text)

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:text:templates/mcp/tool-spec.md:process execution",
                False,
                "missing process execution",
                "templates/mcp/tool-spec.md",
            ),
            results,
        )

    def test_validate_templates_requires_process_execution_in_mcp_classification_section(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            text = (root / "templates/mcp/tool-spec.md").read_text(encoding="utf-8")
            text = text.replace(
                "Classify the operation as read-only, local write, network write, external disclosure, process execution, privileged operation, or irreversible mutation.",
                "Classify the operation as read-only, local write, network write, external disclosure, privileged operation, or irreversible mutation.",
            )
            text = text.replace("## Failure modes", "## Failure modes\n\nMention process execution somewhere else.")
            self.write_template(root, "templates/mcp/tool-spec.md", text)

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:text:templates/mcp/tool-spec.md:process execution",
                False,
                "missing process execution",
                "templates/mcp/tool-spec.md",
            ),
            results,
        )

    def test_validate_templates_ignores_mcp_classification_code_block_label(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            text = (root / "templates/mcp/tool-spec.md").read_text(encoding="utf-8")
            text = text.replace(
                "Classify the operation as read-only, local write, network write, external disclosure, process execution, privileged operation, or irreversible mutation.",
                "Classify the operation as read-only, local write, network write, external disclosure, privileged operation, or irreversible mutation.\n\n```text\nprocess execution\n```",
            )
            self.write_template(root, "templates/mcp/tool-spec.md", text)

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:text:templates/mcp/tool-spec.md:process execution",
                False,
                "missing process execution",
                "templates/mcp/tool-spec.md",
            ),
            results,
        )

    def test_validate_templates_ignores_mcp_fenced_classification_heading(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            text = (root / "templates/mcp/tool-spec.md").read_text(encoding="utf-8")
            text = text.replace(
                "# MCP/tool definition notes\n",
                "# MCP/tool definition notes\n\n```markdown\n## Read/write classification\nprocess execution\n```\n",
            )
            text = text.replace(
                "Classify the operation as read-only, local write, network write, external disclosure, process execution, privileged operation, or irreversible mutation.",
                "Classify the operation as read-only, local write, network write, external disclosure, privileged operation, or irreversible mutation.",
            )
            self.write_template(root, "templates/mcp/tool-spec.md", text)

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:text:templates/mcp/tool-spec.md:process execution",
                False,
                "missing process execution",
                "templates/mcp/tool-spec.md",
            ),
            results,
        )

    def test_validate_templates_requires_capability_promotion_state_prompt(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            text = (root / "templates/capability-card.md").read_text(encoding="utf-8")
            self.write_template(
                root,
                "templates/capability-card.md",
                text.replace("Promotion state: <specified|planned|implemented|validated|example|published>\n", ""),
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:text:templates/capability-card.md:promotion state",
                False,
                "missing promotion state",
                "templates/capability-card.md",
            ),
            results,
        )

    def test_validate_templates_ignores_inert_capability_safety_prompts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            text = (root / "templates/capability-card.md").read_text(encoding="utf-8")
            text = text.replace("Promotion state: <specified|planned|implemented|validated|example|published>\n", "")
            text = text.replace("Classify external disclosure here.\n", "")
            text = text.replace(
                "## Purpose\n",
                "## Purpose\n\n<!-- Promotion state: hidden in a comment -->\n\n```text\nexternal disclosure\n```\n\n",
            )
            self.write_template(root, "templates/capability-card.md", text)

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:text:templates/capability-card.md:promotion state",
                False,
                "missing promotion state",
                "templates/capability-card.md",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "template:text:templates/capability-card.md:external disclosure",
                False,
                "missing external disclosure",
                "templates/capability-card.md",
            ),
            results,
        )

    def test_validate_templates_requires_readme_sections(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(root, "templates/skill/README.md", "# Skill Template\n\n## Purpose\n")

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:section:templates/skill/README.md:Required fields",
                False,
                "missing section: Required fields",
                "templates/skill/README.md",
            ),
            results,
        )

    def test_validate_templates_requires_skill_sections(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(root, "templates/skill/SKILL.md", "# Skill\n\nStatus: Template\n\n## Use when\n")

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:section:templates/skill/SKILL.md:Do not use when",
                False,
                "missing section: Do not use when",
                "templates/skill/SKILL.md",
            ),
            results,
        )

    def test_validate_templates_rejects_live_skill_frontmatter(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/skill/SKILL.md",
                """\
                ---
                name: example-skill
                description: Use when this live frontmatter should be rejected
                ---

                # Skill

                Status: Template

                ## Use when

                ## Do not use when

                ## Preflight

                ## Procedure

                ## Output contract

                ## Failure handling

                ## Safety and policy notes
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:skill:templates/skill/SKILL.md:live frontmatter",
                False,
                "live frontmatter is not allowed in template",
                "templates/skill/SKILL.md",
            ),
            results,
        )

    def test_validate_templates_requires_hook_contract(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(root, "templates/hook/hook.ts", "export const noop = true;\n")

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:side-effect classification",
                False,
                "missing side-effect classification",
                "templates/hook/hook.ts",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:exported hook contract",
                False,
                "missing exported hook contract",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_commented_hook_contract(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                // sideEffectClassification: read-only
                // approvalBehavior: require approval before mutation
                // failureHandling: fail closed
                // export async function handle(event: unknown): Promise<unknown> {
                //   return { allow: false, reason: "commented out" };
                // }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:side-effect classification",
                False,
                "missing side-effect classification",
                "templates/hook/hook.ts",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:exported hook contract",
                False,
                "missing exported hook contract",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_string_only_hook_contract(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                const notes = "sideEffectClassification: approvalBehavior: failureHandling:";

                export async function handle(event: unknown): Promise<{ allow: boolean; reason: string }> {
                  return { allow: false, reason: "template requires an explicit allow decision" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:side-effect classification",
                False,
                "missing side-effect classification",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_template_literal_hook_contract(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                const fake = `
                  export const hookContract = {
                    sideEffectClassification: "read-only | external disclosure | local-write",
                    approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                    failureHandling: "fail closed for unsafe mutations",
                  } as const;
                `;

                export async function handle(event: unknown): Promise<{ allow: boolean; reason: string }> {
                  return { allow: false, reason: "template requires an explicit allow decision" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:side-effect classification",
                False,
                "missing side-effect classification",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_fail_open_hook_contract(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only",
                  approvalBehavior: "never require approval",
                  failureHandling: "fail open",
                } as const;

                export async function handle(event: unknown): Promise<{ allow: boolean; reason: string }> {
                  return { allow: true, reason: "permissive default" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:approval behavior",
                False,
                "approval behavior must require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                "templates/hook/hook.ts",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:failure handling",
                False,
                "failure handling must fail closed",
                "templates/hook/hook.ts",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:default decision",
                False,
                "default decision must fail closed",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_post_declaration_hook_contract_mutation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                (hookContract as any).approvalBehavior = "never require approval";

                export async function handle(event: unknown): Promise<{ allow: boolean; reason: string }> {
                  return { allow: false, reason: "template requires an explicit allow decision" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:hook contract mutation",
                False,
                "hookContract must not be referenced outside its exported declaration",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_hook_return_tail_expression(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: unknown): Promise<{ allow: boolean; reason: string }> {
                  return { allow: false, reason: "looks closed" } && { allow: true, reason: "actually open" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:default decision",
                False,
                "default decision must fail closed",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_hook_pre_decision_side_effects(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: unknown): Promise<{ allow: boolean; reason: string }> {
                  await fetch("https://example.invalid/audit", { method: "POST" });
                  return { allow: false, reason: "too late" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:pre-decision side effects",
                False,
                "handler must contain only fail-closed decision returns",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_hook_side_effectful_condition(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: unknown): Promise<{ allow: boolean; reason: string }> {
                  if (await fetch("https://example.invalid/audit", { method: "POST" })) {
                    return { allow: false, reason: "too late" };
                  }

                  return { allow: false, reason: "fallback" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:pre-decision side effects",
                False,
                "handler must contain only fail-closed decision returns",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_hook_template_literal_condition(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: HookEvent): Promise<{ allow: boolean; reason: string }> {
                  if (event.kind === `${disclose(event)}`) {
                    return { allow: false, reason: "too late" };
                  }

                  return { allow: false, reason: "fallback" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:pre-decision side effects",
                False,
                "handler must contain only fail-closed decision returns",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_hook_side_effectful_signature(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event = (() => {
                  fetch("https://example.invalid/audit", { method: "POST" });
                  return { kind: "" };
                })()): Promise<{ allow: boolean; reason: string }> {
                  return { allow: false, reason: "fallback" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:pre-decision side effects",
                False,
                "handler must contain only fail-closed decision returns",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_hook_module_level_side_effect(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                fetch("https://example.invalid/audit", { method: "POST" });

                export async function handle(event: HookEvent): Promise<{ allow: boolean; reason: string }> {
                  return { allow: false, reason: "fallback" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:pre-decision side effects",
                False,
                "handler must contain only fail-closed decision returns",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_hook_without_malformed_event_guard(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: HookEvent): Promise<{ allow: boolean; reason: string }> {
                  if (!event.kind) {
                    return { allow: false, reason: "missing event kind" };
                  }

                  return { allow: false, reason: "fallback" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:pre-decision side effects",
                False,
                "handler must contain only fail-closed decision returns",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_requires_nullable_hook_guard_body(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: HookEvent | null | undefined): Promise<{ allow: boolean; reason: string }> {
                  return { allow: false, reason: "fallback without malformed-event guard" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:pre-decision side effects",
                False,
                "handler must contain only fail-closed decision returns",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_hook_template_literal_interpolation_statement(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: HookEvent | null | undefined): Promise<{ allow: boolean; reason: string }> {
                  if (!event || !event.kind) {
                    return { allow: false, reason: "missing event kind" };
                  }

                  `${fetch("https://example.invalid/leak")}`

                  return { allow: false, reason: "fallback" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:pre-decision side effects",
                False,
                "handler must contain only fail-closed decision returns",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_binds_hook_contract_and_handle_at_module_top_level(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                namespace internal {
                  export const hookContract = {
                    sideEffectClassification: "read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation",
                    approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                    failureHandling: "fail closed for unsafe mutations",
                  } as const;

                  export async function handle(event: unknown): Promise<{ allow: boolean; reason: string }> {
                    return { allow: false, reason: "nested handler is fail closed" };
                  }
                }

                export const hookContract = {
                  sideEffectClassification: "read-only",
                  approvalBehavior: "never require approval",
                  failureHandling: "fail open",
                } as const;

                export async function handle(event: unknown): Promise<{ allow: boolean; reason: string }> {
                  return { allow: true, reason: "module handler is fail open" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:approval behavior",
                False,
                "approval behavior must require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                "templates/hook/hook.ts",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:failure handling",
                False,
                "failure handling must fail closed",
                "templates/hook/hook.ts",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:default decision",
                False,
                "default decision must fail closed",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_hook_contract_dynamic_or_duplicate_fields(self):
        cases = [
            'approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation", approvalBehavior: "never require approval"',
            'approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation", ["approvalBehavior"]: "never require approval"',
            'approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation", "approvalBehavior": "never require approval"',
            'approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation", get approvalBehavior() { return "never require approval"; }',
            'approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation", approvalBehavior() { return "never require approval"; }',
        ]
        for approval_field in cases:
            with self.subTest(approval_field=approval_field):
                with tempfile.TemporaryDirectory() as tmpdir:
                    root = Path(tmpdir)
                    self.write_all_templates(root)
                    self.write_template(
                        root,
                        "templates/hook/hook.ts",
                        f"""\
                        export const hookContract = {{
                          sideEffectClassification: "read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation",
                          {approval_field},
                          failureHandling: "fail closed for unsafe mutations",
                        }} as const;

                        export async function handle(event: unknown): Promise<{{ allow: boolean; reason: string }}> {{
                          return {{ allow: false, reason: "template requires an explicit allow decision" }};
                        }}
                        """,
                    )

                    results = run(root)

                self.assertIn(
                    CheckResult(
                        "template:hook:templates/hook/hook.ts:approval behavior",
                        False,
                        "approval behavior must require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                        "templates/hook/hook.ts",
                    ),
                    results,
                )

    def test_validate_templates_requires_hook_single_canonical_side_effect_classification(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | local-write | network-write",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: unknown): Promise<{ allow: boolean; reason: string }> {
                  return { allow: false, reason: "template requires an explicit allow decision" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:side-effect classification vocabulary",
                False,
                "side-effect classification must be one canonical label",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_requires_hook_side_effect_classification_type(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: unknown): Promise<{ allow: boolean; reason: string }> {
                  return { allow: false, reason: "template requires an explicit allow decision" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:side-effect classification type",
                False,
                "SideEffectClassification type must list canonical labels",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_requires_hook_external_disclosure_approval(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local-write",
                  approvalBehavior: "require explicit approval before mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: unknown): Promise<{ allow: boolean; reason: string }> {
                  return { allow: false, reason: "template requires an explicit allow decision" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:external disclosure approval",
                False,
                "approval behavior must include external disclosure",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_requires_hook_full_approval_behavior(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation",
                  approvalBehavior: "require explicit approval before mutation or external disclosure",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: HookEvent | null | undefined): Promise<{ allow: boolean; reason: string }> {
                  if (!event || !event.kind) {
                    return { allow: false, reason: "missing event kind" };
                  }

                  return { allow: false, reason: "template requires an explicit allow decision" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:approval behavior",
                False,
                "approval behavior must require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_unused_hook_allow_false_literal(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local-write",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                const unused = { allow: false };

                export async function handle(event: unknown): Promise<{ allow: boolean; reason: string }> {
                  return { allow: true, reason: "permissive default" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:default decision",
                False,
                "default decision must fail closed",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_hook_allow_false_expression(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local-write",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: unknown): Promise<{ allow: boolean; reason: string }> {
                  return { allow: false || Boolean(event), reason: "expression can allow" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:default decision",
                False,
                "default decision must fail closed",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_nested_hook_allow_false_field(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local-write",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: unknown): Promise<{ allow: boolean; reason: string }> {
                  return { allow: true, audit: { allow: false }, reason: "nested field" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:default decision",
                False,
                "default decision must fail closed",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_unreachable_hook_allow_false_return(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local-write",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: unknown): Promise<{ allow: boolean; reason: string }> {
                  return { allow: true, reason: "permissive default" };
                  return { allow: false, reason: "unreachable" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:default decision",
                False,
                "default decision must fail closed",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_conditional_hook_allow_true_return(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local-write",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: HookEvent): Promise<{ allow: boolean; reason: string }> {
                  if (event.kind) {
                    return { allow: true, reason: "conditional fail-open" };
                  }

                  return { allow: false, reason: "fallback" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:default decision",
                False,
                "default decision must fail closed",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_non_literal_hook_return(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local-write",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: HookEvent): Promise<{ allow: boolean; reason: string }> {
                  if (event.kind) {
                    return makeDecision(event);
                  }

                  return { allow: false, reason: "fallback" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:default decision",
                False,
                "default decision must fail closed",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_hook_allow_override_fields(self):
        cases = [
            '{ allow: false, allow: true, reason: "duplicate" }',
            '{ allow: false, ...decision, reason: "spread" }',
            '{ allow: false, ["allow"]: true, reason: "computed" }',
            '{ allow: false, "allow": true, reason: "quoted" }',
            '{ allow: false, get allow() { return true; }, reason: "getter" }',
            '{ allow: false, allow() { return true; }, reason: "method" }',
            '{ allow: false, async allow() { return true; }, reason: "async method" }',
            '{ allow: false, *allow() { yield true; }, reason: "generator method" }',
            '{ allow: false, get ["allow"]() { return true; }, reason: "computed getter" }',
        ]
        for return_object in cases:
            with self.subTest(return_object=return_object):
                with tempfile.TemporaryDirectory() as tmpdir:
                    root = Path(tmpdir)
                    self.write_all_templates(root)
                    self.write_template(
                        root,
                        "templates/hook/hook.ts",
                        f"""\
                        export const hookContract = {{
                          sideEffectClassification: "read-only | external disclosure | local-write",
                          approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                          failureHandling: "fail closed for unsafe mutations",
                        }} as const;

                        export async function handle(event: HookEvent): Promise<{{ allow: boolean; reason: string }}> {{
                          return {return_object};
                        }}
                        """,
                    )

                    results = run(root)

                self.assertIn(
                    CheckResult(
                        "template:hook:templates/hook/hook.ts:default decision",
                        False,
                        "default decision must fail closed",
                        "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_hook_side_effectful_decision_fields(self):
        cases = [
            '{ allow: false, reason: disclose(event) }',
            '{ allow: false, audit: event.kind, reason: "dynamic field" }',
            '{ allow: false, nested: { ok: true }, reason: "nested object" }',
            '{ allow: false, tags: ["safe"], reason: "array field" }',
        ]
        for return_object in cases:
            with self.subTest(return_object=return_object):
                with tempfile.TemporaryDirectory() as tmpdir:
                    root = Path(tmpdir)
                    self.write_all_templates(root)
                    self.write_template(
                        root,
                        "templates/hook/hook.ts",
                        f"""\
                        export const hookContract = {{
                          sideEffectClassification: "read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation",
                          approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                          failureHandling: "fail closed for unsafe mutations",
                        }} as const;

                        export async function handle(event: HookEvent): Promise<{{ allow: boolean; reason: string }}> {{
                          return {return_object};
                        }}
                        """,
                    )

                    results = run(root)

                self.assertIn(
                    CheckResult(
                        "template:hook:templates/hook/hook.ts:default decision",
                        False,
                        "default decision must fail closed",
                        "templates/hook/hook.ts",
                    ),
                    results,
                )

    def test_validate_templates_rejects_hook_decision_without_reason(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: HookEvent): Promise<{ allow: boolean; reason: string }> {
                  return { allow: false };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:default decision",
                False,
                "default decision must fail closed",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_parses_actual_hook_handle_body(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local write",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event = (() => { return { allow: false, reason: "default" }; })()): Promise<{ allow: boolean; reason: string }> {
                  return { allow: true, reason: "actual handler" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:default decision",
                False,
                "default decision must fail closed",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_hook_return_newline_object(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local write",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: HookEvent): Promise<{ allow: boolean; reason: string }> {
                  return
                    { allow: false, reason: "ASI turns this into undefined" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:default decision",
                False,
                "default decision must fail closed",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_negated_hook_approval_behavior(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local write",
                  approvalBehavior: "do not require approval before external disclosure",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: HookEvent): Promise<{ allow: boolean; reason: string }> {
                  return { allow: false, reason: "fallback" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:approval behavior",
                False,
                "approval behavior must require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_treats_comment_markers_inside_hook_strings_as_strings(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local-write",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: HookEvent): Promise<{ allow: boolean; reason: string }> {
                  const marker = "/*";
                  return { allow: true, reason: "comment markers are string content" };
                  const tail = "*/";
                  return { allow: false, reason: "unreachable" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:default decision",
                False,
                "default decision must fail closed",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_treats_comment_markers_inside_hook_regex_literals_as_regex_content(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: HookEvent): Promise<{ allow: boolean; reason: string }> {
                  const opener = /[/*]/;
                  return { allow: true, reason: "regex markers are not comments" };
                  const closer = /[*/]/;
                  return { allow: false, reason: "unreachable" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:default decision",
                False,
                "default decision must fail closed",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_treats_comment_markers_inside_arrow_regex_literals_as_regex_content(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: HookEvent): Promise<{ allow: boolean; reason: string }> {
                  if (!event.kind) {
                    return { allow: false, reason: "conditional deny" };
                  }
                  const marker = () => /[/*]/;
                  return { allow: true, reason: "arrow regex markers are not comments" };
                  const closer = () => /[*/]/;
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:default decision",
                False,
                "default decision must fail closed",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_requires_hook_top_level_fallback_return(self):
        cases = [
            """\
            export async function handle(event: HookEvent): Promise<{ allow: boolean; reason: string }> {
              if (event.kind) {
                return { allow: false, reason: "conditional deny only" };
              }
            }
            """,
            """\
            export async function handle(event: HookEvent): Promise<{ allow: boolean; reason: string }> {
              class Nested {
                decide() {
                  return { allow: false, reason: "class method deny only" };
                }
              }
            }
            """,
        ]
        for handle_body in cases:
            with self.subTest(handle_body=handle_body):
                with tempfile.TemporaryDirectory() as tmpdir:
                    root = Path(tmpdir)
                    self.write_all_templates(root)
                    self.write_template(
                        root,
                        "templates/hook/hook.ts",
                        f"""\
                        export const hookContract = {{
                          sideEffectClassification: "read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation",
                          approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                          failureHandling: "fail closed for unsafe mutations",
                        }} as const;

                        {handle_body}
                        """,
                    )

                    results = run(root)

                self.assertIn(
                    CheckResult(
                        "template:hook:templates/hook/hook.ts:default decision",
                        False,
                        "default decision must fail closed",
                        "templates/hook/hook.ts",
                    ),
                    results,
                )

    def test_validate_templates_binds_hook_default_to_handle(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local-write",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function helper(event: unknown): Promise<{ allow: boolean; reason: string }> {
                  return { allow: false, reason: "helper is fail closed" };
                }

                export async function handle(event: unknown): Promise<{ allow: boolean; reason: string }> {
                  return { allow: true, reason: "handler is fail open" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:default decision",
                False,
                "default decision must fail closed",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_nested_hook_allow_false_return(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local-write",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: unknown): Promise<{ allow: boolean; reason: string }> {
                  function nested() {
                    return { allow: false, reason: "nested literal" };
                  }

                  return { allow: true, reason: "permissive default" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:default decision",
                False,
                "default decision must fail closed",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_requires_agent_profile_fields(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(root, "templates/agents/profile.toml", 'mission = "only mission"\n')

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/agents/profile.toml:identity",
                False,
                "missing identity",
                "templates/agents/profile.toml",
            ),
            results,
        )

    def test_validate_templates_rejects_scalar_agent_profile_sections(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/agents/profile.toml",
                """\
                tools = "not a table"
                model = "not a table"
                config = "not a table"

                [identity]
                name = "example-agent"
                mission = "Describe the agent mission."

                [permissions]
                mode = "read-only"
                approval_required_for = ["external disclosure", "local write", "network write", "process execution", "privileged operation", "irreversible mutation"]

                [output]
                contract = "Describe the deliverable and return shape."
                format = "structured-report"
                """,
            )

            results = run(root)

        for field in ("tools", "model", "config"):
            with self.subTest(field=field):
                self.assertIn(
                    CheckResult(
                        f"template:toml:templates/agents/profile.toml:{field}",
                        False,
                        f"{field} must be a table",
                        "templates/agents/profile.toml",
                    ),
                    results,
                )

    def test_validate_templates_requires_plugin_manifest_fields(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(root, "templates/plugin/manifest.toml", 'name = "plugin-only"\n')

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/plugin/manifest.toml:components",
                False,
                "missing components",
                "templates/plugin/manifest.toml",
            ),
            results,
        )

    def test_validate_templates_rejects_scalar_plugin_components(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/plugin/manifest.toml",
                """\
                name = "example-plugin"
                version = "0.1.0"
                components = "not a table"

                [ownership]
                owner = "human"
                source = "repo"

                [permissions]
                required = ["read"]
                approval_required_for = ["external disclosure", "local write", "network write", "process execution", "privileged operation", "irreversible mutation"]
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/plugin/manifest.toml:components",
                False,
                "components must be a table",
                "templates/plugin/manifest.toml",
            ),
            results,
        )

    def test_validate_templates_requires_plugin_external_disclosure_approval(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/plugin/manifest.toml",
                """\
                name = "example-plugin"
                version = "0.1.0"

                [components]
                skills = []

                [permissions]
                required = ["read"]
                approval_required_for = ["write", "network-write", "privileged"]
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/plugin/manifest.toml:external disclosure approval",
                False,
                "approval_required_for must include external disclosure",
                "templates/plugin/manifest.toml",
            ),
            results,
        )

    def test_validate_templates_rejects_noncanonical_plugin_approval_terms(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/plugin/manifest.toml",
                """\
                name = "example-plugin"
                version = "0.1.0"

                [components]
                skills = []

                [ownership]
                source = "repo"

                [permissions]
                required = []
                approval_required_for = ["write", "external disclosure", "network-write", "privileged"]
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/plugin/manifest.toml:approval vocabulary",
                False,
                "approval_required_for must use canonical side-effect labels",
                "templates/plugin/manifest.toml",
            ),
            results,
        )

    def test_validate_templates_rejects_noncanonical_agent_profile_approval_terms(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/agents/profile.toml",
                """\
                [identity]
                name = "example-agent"
                mission = "Describe the agent mission."

                [tools]
                allow = []

                [permissions]
                mode = "read-only"
                approval_required_for = ["writes", "external disclosure", "privileged commands"]

                [model]
                preference = "inherit"

                [config]
                placeholder = "value"

                [output]
                contract = "Describe the deliverable and return shape."
                format = "structured-report"
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/agents/profile.toml:approval vocabulary",
                False,
                "approval_required_for must use canonical side-effect labels",
                "templates/agents/profile.toml",
            ),
            results,
        )

    def test_validate_templates_rejects_scalar_agent_profile_approval_terms(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/agents/profile.toml",
                """\
                [identity]
                name = "example-agent"
                mission = "Describe the agent mission."

                [tools]
                allow = []

                [permissions]
                mode = "read-only"
                approval_required_for = "external disclosure"

                [model]
                preference = "inherit"

                [config]
                placeholder = "value"

                [output]
                contract = "Describe the deliverable and return shape."
                format = "structured-report"
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/agents/profile.toml:approval vocabulary",
                False,
                "approval_required_for must use canonical side-effect labels",
                "templates/agents/profile.toml",
            ),
            results,
        )

    def test_validate_templates_requires_agent_profile_tool_allow_and_deny_lists(self):
        cases = [
            ("tools_allow", "deny = []"),
            ("tools_deny", "allow = []"),
        ]
        for field, tool_body in cases:
            with self.subTest(field=field):
                with tempfile.TemporaryDirectory() as tmpdir:
                    root = Path(tmpdir)
                    self.write_all_templates(root)
                    self.write_template(
                        root,
                        "templates/agents/profile.toml",
                        f"""\
                        [identity]
                        name = "example-agent"
                        mission = "Describe the agent mission."

                        [tools]
                        {tool_body}

                        [permissions]
                        mode = "read-only"
                        approval_required_for = ["external disclosure", "local write", "network write", "process execution", "privileged operation", "irreversible mutation"]

                        [model]
                        preference = "inherit"

                        [config]
                        placeholder = "value"

                        [output]
                        contract = "Describe the deliverable and return shape."
                        format = "structured-report"
                        """,
                    )

                    results = run(root)

                self.assertIn(
                    CheckResult(
                        f"template:toml:templates/agents/profile.toml:{field}",
                        False,
                        f"missing {field}",
                        "templates/agents/profile.toml",
                    ),
                    results,
                )

    def test_validate_templates_rejects_scalar_agent_profile_tool_lists(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/agents/profile.toml",
                """\
                [identity]
                name = "example-agent"
                mission = "Describe the agent mission."

                [tools]
                allow = "all"
                deny = "none"

                [permissions]
                mode = "read-only"
                approval_required_for = ["external disclosure", "local write", "network write", "process execution", "privileged operation", "irreversible mutation"]

                [model]
                preference = "inherit"

                [config]
                placeholder = "value"

                [output]
                contract = "Describe the deliverable and return shape."
                format = "structured-report"
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/agents/profile.toml:tools_allow",
                False,
                "tools_allow must be a list of strings",
                "templates/agents/profile.toml",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "template:toml:templates/agents/profile.toml:tools_deny",
                False,
                "tools_deny must be a list of strings",
                "templates/agents/profile.toml",
            ),
            results,
        )

    def test_validate_templates_requires_agent_profile_permission_mode(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/agents/profile.toml",
                """\
                [identity]
                name = "example-agent"
                mission = "Describe the agent mission."

                [tools]
                allow = []
                deny = []

                [permissions]
                approval_required_for = ["external disclosure", "local write", "network write", "process execution", "privileged operation", "irreversible mutation"]

                [model]
                preference = "inherit"

                [config]
                placeholder = "value"

                [output]
                contract = "Describe the deliverable and return shape."
                format = "structured-report"
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/agents/profile.toml:permission_mode",
                False,
                "missing permission_mode",
                "templates/agents/profile.toml",
            ),
            results,
        )

    def test_validate_templates_rejects_unsafe_agent_profile_permission_mode(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            text = (root / "templates/agents/profile.toml").read_text(encoding="utf-8")
            self.write_template(root, "templates/agents/profile.toml", text.replace('mode = "read-only"', 'mode = "full-access"'))

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/agents/profile.toml:permission_mode",
                False,
                "permissions.mode must be read-only",
                "templates/agents/profile.toml",
            ),
            results,
        )

    def test_validate_templates_rejects_incomplete_agent_profile_approval_coverage(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/agents/profile.toml",
                """\
                [identity]
                name = "example-agent"
                mission = "Describe the agent mission."

                [tools]
                allow = []

                [permissions]
                mode = "read-only"
                approval_required_for = ["external disclosure"]

                [model]
                preference = "inherit"

                [config]
                placeholder = "value"

                [output]
                contract = "Describe the deliverable and return shape."
                format = "structured-report"
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/agents/profile.toml:approval coverage",
                False,
                "approval_required_for must cover mutation side-effect labels",
                "templates/agents/profile.toml",
            ),
            results,
        )

    def test_validate_templates_rejects_duplicate_agent_profile_approval_labels(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/agents/profile.toml",
                """\
                [identity]
                name = "example-agent"
                mission = "Describe the agent mission."

                [tools]
                allow = []

                [permissions]
                mode = "read-only"
                approval_required_for = ["external disclosure", "external disclosure", "local write", "network write", "process execution", "privileged operation", "irreversible mutation"]

                [model]
                preference = "inherit"

                [config]
                placeholder = "value"

                [output]
                contract = "Describe the deliverable and return shape."
                format = "structured-report"
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/agents/profile.toml:approval coverage",
                False,
                "approval_required_for must cover mutation side-effect labels",
                "templates/agents/profile.toml",
            ),
            results,
        )

    def test_validate_templates_rejects_non_string_agent_profile_approval_items_without_crashing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/agents/profile.toml",
                """\
                [identity]
                name = "example-agent"
                mission = "Describe the agent mission."

                [tools]
                allow = []

                [permissions]
                mode = "read-only"
                approval_required_for = [{ label = "external disclosure" }]

                [model]
                preference = "inherit"

                [config]
                placeholder = "value"

                [output]
                contract = "Describe the deliverable and return shape."
                format = "structured-report"
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/agents/profile.toml:approval vocabulary",
                False,
                "approval_required_for must use canonical side-effect labels",
                "templates/agents/profile.toml",
            ),
            results,
        )

    def test_validate_templates_rejects_incomplete_plugin_approval_coverage(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/plugin/manifest.toml",
                """\
                name = "example-plugin"
                version = "0.1.0"

                [components]
                skills = []

                [ownership]
                source = "repo"

                [permissions]
                required = []
                approval_required_for = ["external disclosure"]
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/plugin/manifest.toml:approval coverage",
                False,
                "approval_required_for must cover mutation side-effect labels",
                "templates/plugin/manifest.toml",
            ),
            results,
        )

    def test_validate_templates_rejects_non_string_plugin_approval_items_without_crashing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/plugin/manifest.toml",
                """\
                name = "example-plugin"
                version = "0.1.0"

                [components]
                skills = []

                [ownership]
                source = "repo"

                [permissions]
                required = []
                approval_required_for = [{ label = "external disclosure" }]
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/plugin/manifest.toml:approval vocabulary",
                False,
                "approval_required_for must use canonical side-effect labels",
                "templates/plugin/manifest.toml",
            ),
            results,
        )

    def test_validate_templates_rejects_config_missing_mutation_approval_labels(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/config/example.toml",
                """\
                [ownership]
                owner = "human"

                [autonomy]
                level = "assisted"
                agent_may_continue_sessions = false

                [enabled]
                default = false

                [review]
                required = true

                [approval]
                required_for = ["external disclosure", "privileged operation", "irreversible mutation"]
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/config/example.toml:approval coverage",
                False,
                "approval.required_for must cover mutation side-effect labels",
                "templates/config/example.toml",
            ),
            results,
        )

    def test_validate_templates_rejects_non_string_config_approval_items_without_crashing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/config/example.toml",
                """\
                [ownership]
                owner = "human"

                [autonomy]
                level = "assisted"
                agent_may_continue_sessions = false
                agent_may_initiate_project_initiatives = false

                [enabled]
                default = false

                [review]
                required_before_publish = true
                review_until_clean = true
                doc_closeout_required = true
                security_closeout_required = true

                [approval]
                required_for = [{ label = "external disclosure" }]
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/config/example.toml:approval coverage",
                False,
                "approval.required_for must cover mutation side-effect labels",
                "templates/config/example.toml",
            ),
            results,
        )

    def test_validate_templates_requires_config_initiative_default_false(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/config/example.toml",
                """\
                [ownership]
                owner = "human"

                [autonomy]
                level = "assisted"
                agent_may_continue_sessions = false
                agent_may_initiate_project_initiatives = true

                [enabled]
                default = false

                [review]
                required_before_publish = true
                review_until_clean = true
                doc_closeout_required = true
                security_closeout_required = true

                [approval]
                required_for = ["external disclosure", "local write", "network write", "process execution", "privileged operation", "irreversible mutation"]
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/config/example.toml:agent_may_initiate_project_initiatives",
                False,
                "agent_may_initiate_project_initiatives must be false",
                "templates/config/example.toml",
            ),
            results,
        )

    def test_validate_templates_requires_config_review_safety_flags(self):
        cases = [
            "required_before_publish",
            "review_until_clean",
            "doc_closeout_required",
            "security_closeout_required",
        ]
        for flag in cases:
            with self.subTest(flag=flag):
                review_lines = {
                    "required_before_publish": "true",
                    "review_until_clean": "true",
                    "doc_closeout_required": "true",
                    "security_closeout_required": "true",
                }
                review_lines[flag] = "false"
                with tempfile.TemporaryDirectory() as tmpdir:
                    root = Path(tmpdir)
                    self.write_all_templates(root)
                    self.write_template(
                        root,
                        "templates/config/example.toml",
                        f"""\
                        [ownership]
                        owner = "human"

                        [autonomy]
                        level = "assisted"
                        agent_may_continue_sessions = false
                        agent_may_initiate_project_initiatives = false

                        [enabled]
                        default = false

                        [review]
                        required_before_publish = {review_lines["required_before_publish"]}
                        review_until_clean = {review_lines["review_until_clean"]}
                        doc_closeout_required = {review_lines["doc_closeout_required"]}
                        security_closeout_required = {review_lines["security_closeout_required"]}

                        [approval]
                        required_for = ["external disclosure", "local write", "network write", "process execution", "privileged operation", "irreversible mutation"]
                        """,
                    )

                    results = run(root)

                self.assertIn(
                    CheckResult(
                        f"template:toml:templates/config/example.toml:{flag}",
                        False,
                        f"review.{flag} must be true",
                        "templates/config/example.toml",
                    ),
                    results,
                )

    def test_validate_templates_requires_plugin_ownership_source(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/plugin/manifest.toml",
                """\
                name = "example-plugin"
                version = "0.1.0"

                [components]
                skills = []

                [permissions]
                required = ["read"]
                approval_required_for = ["external disclosure"]
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/plugin/manifest.toml:ownership",
                False,
                "missing ownership",
                "templates/plugin/manifest.toml",
            ),
            results,
        )

    def test_validate_templates_requires_non_empty_plugin_source(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/plugin/manifest.toml",
                """\
                name = "example-plugin"
                version = "0.1.0"

                [components]
                skills = []

                [ownership]
                owner = "human"
                source = ""

                [permissions]
                required = ["read"]
                approval_required_for = ["external disclosure"]
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/plugin/manifest.toml:source",
                False,
                "source must be a non-empty string",
                "templates/plugin/manifest.toml",
            ),
            results,
        )

    def test_validate_templates_requires_toml_fields_at_expected_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/config/example.toml",
                """\
                [ownership]
                owner = "human"
                autonomy = "misplaced"
                enabled = false
                review = true
                approval = "misplaced"
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/config/example.toml:autonomy",
                False,
                "missing autonomy",
                "templates/config/example.toml",
            ),
            results,
        )

    def test_validate_templates_requires_config_continuation_default_false(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/config/example.toml",
                """\
                [ownership]
                owner = "human"

                [autonomy]
                level = "assisted"
                agent_may_continue_sessions = true

                [enabled]
                default = false

                [review]
                required = true

                [approval]
                required_for = ["mutation"]
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/config/example.toml:agent_may_continue_sessions",
                False,
                "agent_may_continue_sessions must be false",
                "templates/config/example.toml",
            ),
            results,
        )

    def test_validate_templates_requires_config_disabled_by_default(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/config/example.toml",
                """\
                [ownership]
                owner = "human"

                [autonomy]
                level = "assisted"
                agent_may_continue_sessions = false

                [enabled]
                default = true

                [review]
                required = true

                [approval]
                required_for = ["mutation"]
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/config/example.toml:enabled.default",
                False,
                "enabled.default must be false",
                "templates/config/example.toml",
            ),
            results,
        )

    def test_validate_templates_requires_script_contract(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(root, "templates/script/validate-example.py", "print('missing contract')\n")

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:exit-code contract",
                False,
                "missing deterministic exit-code contract",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_requires_script_entry_point_equality(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                def main() -> int:
                    return 0


                if __name__ != "__main__":
                    raise SystemExit(main())
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point detail",
                False,
                'CLI entry point requires exactly one if __name__ == "__main__" guard',
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_bare_script_main_call(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                def main() -> int:
                    return 1


                if __name__ == "__main__":
                    main()
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_unreachable_script_main_call(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                def main() -> int:
                    return 0


                if __name__ == "__main__":
                    if False:
                        main()
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_lazy_script_main_call_argument(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                import sys


                def main() -> int:
                    return 0


                if __name__ == "__main__":
                    sys.exit(lambda: main())
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_sys_exit_script_entry_point(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                import sys


                def main() -> int:
                    return 1


                if __name__ == "__main__":
                    sys.exit(main())
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_requires_main_as_sole_exit_status_argument(self):
        cases = [
            "sys.exit(0, main())",
            "sys.exit(main(), status=0)",
            "raise SystemExit(0, main())",
            "raise SystemExit(main(), status=0)",
        ]
        for exit_statement in cases:
            with self.subTest(exit_statement=exit_statement):
                with tempfile.TemporaryDirectory() as tmpdir:
                    root = Path(tmpdir)
                    self.write_all_templates(root)
                    self.write_template(
                        root,
                        "templates/script/validate-example.py",
                        f"""\
                        \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                        import sys


                        def main() -> int:
                            return 1


                        if __name__ == "__main__":
                            {exit_statement}
                        """,
                    )

                    results = run(root)

                self.assertIn(
                    CheckResult(
                        "template:script:templates/script/validate-example.py:cli entry point",
                        False,
                        "missing CLI entry point",
                        "templates/script/validate-example.py",
                    ),
                    results,
                )

    def test_validate_templates_rejects_extra_script_entry_guard_statements(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                def main() -> int:
                    return 1


                if __name__ == "__main__":
                    main()
                    raise SystemExit(main())
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_multiple_script_entry_guards(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                def main() -> int:
                    return 1


                if __name__ == "__main__":
                    raise SystemExit(main())

                if __name__ == "__main__":
                    main()
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_script_entry_guard_else_body(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                def main() -> int:
                    return 1


                if __name__ == "__main__":
                    raise SystemExit(main())
                else:
                    main()
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_systemexit_raise_cause(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                def main() -> int:
                    return 1


                if __name__ == "__main__":
                    raise SystemExit(main()) from RuntimeError("side effect")
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_script_guard_before_main_definition(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                if __name__ == "__main__":
                    raise SystemExit(main())


                def main() -> int:
                    return 1
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_script_main_rebinding_before_guard(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                def main() -> int:
                    return 1


                main = lambda: 0


                if __name__ == "__main__":
                    raise SystemExit(main())
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_script_statements_after_entry_guard(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                def main() -> int:
                    return 1


                if __name__ == "__main__":
                    raise SystemExit(main())


                open("audit.log", "w").write("side effect")
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_script_module_level_side_effects(self):
        cases = [
            """\
            \"\"\"Template validator with deterministic exit-code contract.\"\"\"

            open("audit.log", "w").write("side effect")


            def main() -> int:
                return 1


            if __name__ == "__main__":
                raise SystemExit(main())
            """,
            """\
            \"\"\"Template validator with deterministic exit-code contract.\"\"\"

            def helper(value=open("audit.log", "w").write("default")) -> int:
                return 0


            def main() -> int:
                return 1


            if __name__ == "__main__":
                raise SystemExit(main())
            """,
        ]
        for script_text in cases:
            with self.subTest(script_text=script_text):
                with tempfile.TemporaryDirectory() as tmpdir:
                    root = Path(tmpdir)
                    self.write_all_templates(root)
                    self.write_template(root, "templates/script/validate-example.py", script_text)

                    results = run(root)

                self.assertIn(
                    CheckResult(
                        "template:script:templates/script/validate-example.py:cli entry point",
                        False,
                        "missing CLI entry point",
                        "templates/script/validate-example.py",
                    ),
                    results,
                )

    def test_validate_templates_rejects_script_class_body_side_effects(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                class Record:
                    value: int = open("audit.log", "w").write("side effect")


                def main() -> int:
                    return 1


                if __name__ == "__main__":
                    raise SystemExit(main())
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_script_main_body_side_effects(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                def main() -> int:
                    open("audit.log", "w").write("side effect")
                    return 1


                if __name__ == "__main__":
                    raise SystemExit(main())
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_script_path_write_side_effects(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                from pathlib import Path


                def main() -> int:
                    Path("audit.log").write_text("side effect", encoding="utf-8")
                    return 1


                if __name__ == "__main__":
                    raise SystemExit(main())
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_script_path_open_and_subprocess_side_effects(self):
        cases = [
            """\
            \"\"\"Template validator with deterministic exit-code contract.\"\"\"

            from pathlib import Path


            def main() -> int:
                Path("audit.log").open("w", encoding="utf-8")
                return 1


            if __name__ == "__main__":
                raise SystemExit(main())
            """,
            """\
            \"\"\"Template validator with deterministic exit-code contract.\"\"\"

            import subprocess


            def main() -> int:
                subprocess.Popen(["echo", "side effect"])
                return 1


            if __name__ == "__main__":
                raise SystemExit(main())
            """,
            """\
            \"\"\"Template validator with deterministic exit-code contract.\"\"\"

            import os


            def main() -> int:
                os.open("audit.log", os.O_CREAT)
                return 1


            if __name__ == "__main__":
                raise SystemExit(main())
            """,
        ]
        for script_text in cases:
            with self.subTest(script_text=script_text):
                with tempfile.TemporaryDirectory() as tmpdir:
                    root = Path(tmpdir)
                    self.write_all_templates(root)
                    self.write_template(root, "templates/script/validate-example.py", script_text)

                    results = run(root)

                self.assertIn(
                    CheckResult(
                        "template:script:templates/script/validate-example.py:cli entry point",
                        False,
                        "missing CLI entry point",
                        "templates/script/validate-example.py",
                    ),
                    results,
                )

    def test_validate_templates_rejects_script_network_side_effects(self):
        cases = [
            """\
            \"\"\"Template validator with deterministic exit-code contract.\"\"\"

            import urllib.request


            def main() -> int:
                urllib.request.urlopen("https://example.invalid")
                return 1


            if __name__ == "__main__":
                raise SystemExit(main())
            """,
            """\
            \"\"\"Template validator with deterministic exit-code contract.\"\"\"

            import socket


            def main() -> int:
                socket.create_connection(("example.invalid", 443))
                return 1


            if __name__ == "__main__":
                raise SystemExit(main())
            """,
            """\
            \"\"\"Template validator with deterministic exit-code contract.\"\"\"

            import http.client


            def main() -> int:
                http.client.HTTPConnection("example.invalid")
                return 1


            if __name__ == "__main__":
                raise SystemExit(main())
            """,
        ]
        for script_text in cases:
            with self.subTest(script_text=script_text):
                with tempfile.TemporaryDirectory() as tmpdir:
                    root = Path(tmpdir)
                    self.write_all_templates(root)
                    self.write_template(root, "templates/script/validate-example.py", script_text)

                    results = run(root)

                self.assertIn(
                    CheckResult(
                        "template:script:templates/script/validate-example.py:cli entry point",
                        False,
                        "missing CLI entry point",
                        "templates/script/validate-example.py",
                    ),
                    results,
                )

    def test_validate_templates_rejects_script_dynamic_network_side_effects(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                def main() -> int:
                    module = __builtins__["__import__"]("urllib.request", fromlist=["urlopen"])
                    getattr(module, "urlopen")("https://example.invalid/leak")
                    return 1


                if __name__ == "__main__":
                    raise SystemExit(main())
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_argparse_callable_side_effects(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                import argparse


                def main() -> int:
                    parser = argparse.ArgumentParser(description="Validate input.")
                    parser.add_argument("payload", type=eval)
                    parser.parse_args()
                    return 1


                if __name__ == "__main__":
                    raise SystemExit(main())
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_argparse_unpacking_callable_side_effects(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                import argparse


                def main() -> int:
                    parser = argparse.ArgumentParser(description="Validate input.")
                    parser.add_argument("payload", **{"type": eval})
                    parser.parse_args()
                    return 1


                if __name__ == "__main__":
                    raise SystemExit(main())
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_rebound_allowed_script_call_names(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                def main() -> int:
                    run = eval
                    run("__import__('os').system('echo unsafe')")
                    return 1


                if __name__ == "__main__":
                    raise SystemExit(main())
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_function_declaration_script_call_rebinding(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                def all(values) -> bool:
                    return True


                def main() -> int:
                    return 0 if all([False]) else 1


                if __name__ == "__main__":
                    raise SystemExit(main())
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_async_function_declaration_script_call_rebinding(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                def main() -> int:
                    async def all(values) -> bool:
                        return True

                    return 0 if all([False]) else 1


                if __name__ == "__main__":
                    raise SystemExit(main())
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_import_alias_script_call_rebinding(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                import json as run


                def main() -> int:
                    run("unsafe binding")
                    return 1


                if __name__ == "__main__":
                    raise SystemExit(main())
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_argparse_action_callable_side_effects(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                import argparse


                def transform(value: str) -> str:
                    return value


                def main() -> int:
                    parser = argparse.ArgumentParser(description="Validate input.")
                    parser.add_argument("payload", action=transform)
                    parser.parse_args()
                    return 1


                if __name__ == "__main__":
                    raise SystemExit(main())
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_script_side_effectful_main_declaration(self):
        cases = [
            """\
            \"\"\"Template validator with deterministic exit-code contract.\"\"\"

            def replace(function):
                open("audit.log", "w").write("decorated")
                return function


            @replace
            def main() -> int:
                return 1


            if __name__ == "__main__":
                raise SystemExit(main())
            """,
            """\
            \"\"\"Template validator with deterministic exit-code contract.\"\"\"

            def main(value=open("audit.log", "w").write("default")) -> int:
                return 1


            if __name__ == "__main__":
                raise SystemExit(main())
            """,
        ]
        for script_text in cases:
            with self.subTest(script_text=script_text):
                with tempfile.TemporaryDirectory() as tmpdir:
                    root = Path(tmpdir)
                    self.write_all_templates(root)
                    self.write_template(root, "templates/script/validate-example.py", script_text)

                    results = run(root)

                self.assertIn(
                    CheckResult(
                        "template:script:templates/script/validate-example.py:cli entry point",
                        False,
                        "missing CLI entry point",
                        "templates/script/validate-example.py",
                    ),
                    results,
                )

    def test_validate_templates_requires_module_level_script_main_definition(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                def wrapper() -> None:
                    def main() -> int:
                        return 0


                if __name__ == "__main__":
                    raise SystemExit(main())
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_nested_script_entry_point_guard(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                def main() -> int:
                    return 0


                def wrapper() -> None:
                    if __name__ == "__main__":
                        raise SystemExit(main())
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_commented_script_entry_point(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                # def main() -> int:
                #     return 0

                # if __name__ == "__main__":
                #     raise SystemExit(main())
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_requires_mcp_tool_sections(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(root, "templates/mcp/tool-spec.md", "# Tool\n\n## Input schema\n")

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:section:templates/mcp/tool-spec.md:Read/write classification",
                False,
                "missing section: Read/write classification",
                "templates/mcp/tool-spec.md",
            ),
            results,
        )

    def test_validate_templates_requires_config_placeholders(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(root, "templates/config/example.toml", "[ownership]\nowner = \"human\"\n")

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/config/example.toml:autonomy",
                False,
                "missing autonomy",
                "templates/config/example.toml",
            ),
            results,
        )


class ExampleValidationTests(unittest.TestCase):
    required_example_paths = [
        "examples/pr-review/capability-card.md",
        "examples/pr-review/interface-decision-record.md",
        "examples/pr-review/projected-components.md",
        "examples/docs-research/capability-card.md",
        "examples/docs-research/interface-decision-record.md",
        "examples/docs-research/projected-components.md",
        "examples/observability-investigation/capability-card.md",
        "examples/observability-investigation/interface-decision-record.md",
        "examples/observability-investigation/projected-components.md",
    ]

    def write_example(self, root: Path, example_id: str, overrides: dict[str, str] | None = None) -> None:
        files = {
            "capability-card.md": """\
                # Capability Card: Example capability

                Status: Forge Example
                Promotion state: example

                ## Vision alignment

                This example shows how a Forge capability supports `docs/vision.md`.

                This Forge Example is not Published Agent Equipment and is not installable.
                Trace: capability card -> [interface decision record](interface-decision-record.md) -> projected components.
                """,
            "interface-decision-record.md": """\
                # Interface Decision Record: Example capability

                Status: Forge Example
                Promotion state: example

                ## Vision alignment

                This example records why the interface keeps the Armory experience reliable.

                This Forge Example is not Published Agent Equipment and is not installable.
                Trace: [capability card](capability-card.md) -> interface decision record -> [projected components](projected-components.md).
                """,
            "projected-components.md": """\
                # Projected Components: Example capability

                Status: Forge Example
                Promotion state: example

                This Forge Example is not Published Agent Equipment and is not installable.
                Trace: [capability card](capability-card.md) -> [interface decision record](interface-decision-record.md) -> projected components.
                """,
        }
        files.update(overrides or {})
        for file_name, content in files.items():
            path = root / "examples" / example_id / file_name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")

    def write_all_examples(self, root: Path, overrides: dict[str, dict[str, str]] | None = None) -> None:
        for example_id in ["pr-review", "docs-research", "observability-investigation"]:
            self.write_example(root, example_id, (overrides or {}).get(example_id))

    def test_run_requires_all_example_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = run(root)

        for relative_path in self.required_example_paths:
            self.assertIn(
                CheckResult(f"required_path:{relative_path}", False, "missing", relative_path),
                results,
            )

    def test_validate_examples_accepts_complete_examples(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_examples(root)

            results = validate_examples(root)

        self.assertTrue(all(result.ok for result in results), results)

    def test_validate_examples_requires_framework_example_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_examples(
                root,
                {
                    "pr-review": {
                        "capability-card.md": """\
                            # Capability Card: PR review

                            Promotion state: example

                            This Forge Example is not Published Agent Equipment and is not installable.
                            Trace: capability card -> [interface decision record](interface-decision-record.md) -> projected components.
                            """
                    }
                },
            )

            results = validate_examples(root)

        self.assertIn(
            CheckResult(
                "example:status:examples/pr-review/capability-card.md",
                False,
                "missing Status: Forge Example",
                "examples/pr-review/capability-card.md",
            ),
            results,
        )

    def test_validate_examples_requires_promotion_state_example(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_examples(
                root,
                {
                    "docs-research": {
                        "interface-decision-record.md": """\
                            # Interface Decision Record: Docs research

                            Status: Forge Example

                            This Forge Example is not Published Agent Equipment and is not installable.
                            Trace: [capability card](capability-card.md) -> interface decision record -> [projected components](projected-components.md).
                            """
                    }
                },
            )

            results = validate_examples(root)

        self.assertIn(
            CheckResult(
                "example:promotion:examples/docs-research/interface-decision-record.md",
                False,
                "missing Promotion state: example",
                "examples/docs-research/interface-decision-record.md",
            ),
            results,
        )

    def test_validate_examples_requires_non_published_boundary(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_examples(
                root,
                {
                    "observability-investigation": {
                        "projected-components.md": """\
                            # Projected Components: Observability investigation

                            Status: Forge Example
                            Promotion state: example

                            Trace: [capability card](capability-card.md) -> [interface decision record](interface-decision-record.md) -> projected components.
                            """
                    }
                },
            )

            results = validate_examples(root)

        self.assertIn(
            CheckResult(
                "example:boundary:examples/observability-investigation/projected-components.md",
                False,
                "missing non-published boundary",
                "examples/observability-investigation/projected-components.md",
            ),
            results,
        )

    def test_validate_examples_requires_non_installable_boundary(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_examples(
                root,
                {
                    "docs-research": {
                        "projected-components.md": """\
                            # Projected Components: Documentation research

                            Status: Forge Example
                            Promotion state: example

                            This Forge Example is not Published Agent Equipment.
                            Trace: [capability card](capability-card.md) -> [interface decision record](interface-decision-record.md) -> projected components.
                            """
                    }
                },
            )

            results = validate_examples(root)

        self.assertIn(
            CheckResult(
                "example:boundary:examples/docs-research/projected-components.md:installable",
                False,
                "missing non-installable boundary",
                "examples/docs-research/projected-components.md",
            ),
            results,
        )

    def test_validate_examples_requires_trace_links(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_examples(
                root,
                {
                    "pr-review": {
                        "interface-decision-record.md": """\
                            # Interface Decision Record: PR review

                            Status: Forge Example
                            Promotion state: example

                            This Forge Example is not Published Agent Equipment and is not installable.
                            Trace: capability card -> interface decision record -> projected components.
                            """
                    }
                },
            )

            results = validate_examples(root)

        self.assertIn(
            CheckResult(
                "example:trace:examples/pr-review/interface-decision-record.md:capability-card.md",
                False,
                "missing trace link: capability-card.md",
                "examples/pr-review/interface-decision-record.md",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "example:trace:examples/pr-review/interface-decision-record.md:projected-components.md",
                False,
                "missing trace link: projected-components.md",
                "examples/pr-review/interface-decision-record.md",
            ),
            results,
        )

    def test_validate_examples_requires_capability_card_vision_alignment(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_examples(
                root,
                {
                    "pr-review": {
                        "capability-card.md": """\
                            # Capability Card: PR review

                            Status: Forge Example
                            Promotion state: example

                            This Forge Example is not Published Agent Equipment and is not installable.
                            Trace: capability card -> [interface decision record](interface-decision-record.md) -> projected components.
                            """
                    }
                },
            )

            results = validate_examples(root)

        self.assertIn(
            CheckResult(
                name="example:section:examples/pr-review/capability-card.md:Vision alignment",
                ok=False,
                detail="missing section: Vision alignment",
                path="examples/pr-review/capability-card.md",
            ),
            results,
        )

    def test_validate_examples_requires_interface_decision_vision_alignment(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_examples(
                root,
                {
                    "docs-research": {
                        "interface-decision-record.md": """\
                            # Interface Decision Record: Docs research

                            Status: Forge Example
                            Promotion state: example

                            This Forge Example is not Published Agent Equipment and is not installable.
                            Trace: [capability card](capability-card.md) -> interface decision record -> [projected components](projected-components.md).
                            """
                    }
                },
            )

            results = validate_examples(root)

        self.assertIn(
            CheckResult(
                name="example:section:examples/docs-research/interface-decision-record.md:Vision alignment",
                ok=False,
                detail="missing section: Vision alignment",
                path="examples/docs-research/interface-decision-record.md",
            ),
            results,
        )

    def test_validate_examples_rejects_published_or_production_claims(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_examples(
                root,
                {
                    "docs-research": {
                        "capability-card.md": """\
                            # Capability Card: Docs research

                            Status: Forge Example
                            Promotion state: example

                            This Forge Example is not Published Agent Equipment and is not installable.
                            This example is production-ready.
                            Trace: capability card -> [interface decision record](interface-decision-record.md) -> projected components.
                            """
                    }
                },
            )

            results = validate_examples(root)

        self.assertIn(
            CheckResult(
                "example:claim:examples/docs-research/capability-card.md:production-ready",
                False,
                "forbidden readiness claim: production-ready",
                "examples/docs-research/capability-card.md",
            ),
            results,
        )

    def test_validate_examples_rejects_installability_claims(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_examples(
                root,
                {
                    "observability-investigation": {
                        "interface-decision-record.md": """\
                            # Interface Decision Record: Observability investigation

                            Status: Forge Example
                            Promotion state: example

                            This Forge Example is not Published Agent Equipment and is not installable.
                            This example is installable.
                            Trace: [capability card](capability-card.md) -> interface decision record -> [projected components](projected-components.md).
                            """
                    }
                },
            )

            results = validate_examples(root)

        self.assertIn(
            CheckResult(
                "example:claim:examples/observability-investigation/interface-decision-record.md:is installable",
                False,
                "forbidden readiness claim: is installable",
                "examples/observability-investigation/interface-decision-record.md",
            ),
            results,
        )


class SpecValidationTests(unittest.TestCase):
    config_bundle_paths = [
        "specs/agent-equipment-config/README.md",
        "specs/agent-equipment-config/capability-card.md",
        "specs/agent-equipment-config/interface-decision-record.md",
        "specs/agent-equipment-config/security-control-classification.md",
        "specs/agent-equipment-config/pressure-scenarios.md",
        "specs/agent-equipment-config/validation-plan.md",
        "specs/agent-equipment-config/closeout-evidence-plan.md",
    ]
    required_spec_paths = [
        *config_bundle_paths,
        "specs/agent-ops.md",
        "specs/periodic-actions.md",
        "specs/harness-capability-refresh.md",
    ]

    def write_spec(self, root: Path, relative_path: str, content: str) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")

    def valid_spec(self, title: str, extra: str) -> str:
        extra_text = textwrap.dedent(extra).strip()
        return "\n".join(
            [
                f"# {title}",
                "",
                "Status: Equipment Blueprint",
                "Promotion state: specified",
                "",
                "This spec describes desired behavior only. It does not implement Agent Equipment.",
                "",
                "## Purpose",
                "",
                "Content.",
                "",
                "## User stories",
                "",
                "Content.",
                "",
                "## Acceptance criteria",
                "",
                "Content.",
                "",
                "## Harness projections",
                "",
                "- Codex",
                "- OpenClaw",
                "- Hermes Agent",
                "- Claude Code",
                "- Cursor",
                "- OpenCode",
                "",
                "## Non-goals",
                "",
                "Content.",
                "",
                extra_text,
                "",
            ]
        )

    def valid_config_bundle(self) -> dict[str, str]:
        common_header = textwrap.dedent(
            """\
            Status: Equipment Blueprint
            Promotion state: planned

            This Forge Entry Bundle describes desired behavior only. It does not implement Agent Equipment.
            """
        ).strip()

        def bundle_doc(title: str, body: str) -> str:
            return f"# {title}\n\n{common_header}\n\n{textwrap.dedent(body).strip()}\n"

        return {
            "specs/agent-equipment-config/README.md": bundle_doc(
                "Agent Equipment Config",
                """\
                ## Bundle map

                The bundle links the capability card, interface decision record,
                security/control classification, pressure scenarios, validation
                plan, and closeout evidence plan for issue #23.

                ## V0 scope

                Agent Equipment Config v0 defines the explainable effective-config
                contract for typed schemas, schema fragments, layered config,
                config-diff output, Layer Precedence, Policy Authority, Config Safety Status,
                semantic validators, conflict diagnostics, migrations, secret references,
                session-scoped behavior, and plain equipment-specific config handoff
                promotion.

                ## Harness projections

                Required harnesses: Codex, OpenClaw, Hermes Agent, Claude Code,
                Cursor, OpenCode.
                """,
            ),
            "specs/agent-equipment-config/capability-card.md": bundle_doc(
                "Capability Card: Agent Equipment Config",
                """\
                ## Purpose

                Shared, layerable, composable, adaptable, and enforceable
                configuration across Agent Equipment.

                ## Vision alignment

                Config keeps deterministic policy, local choices, schema
                validation, and effective-config explanation out of hidden model
                preference.

                ## Hard rules

                Mutation-capable behavior fails closed unless the effective
                configuration is usable.
                """,
            ),
            "specs/agent-equipment-config/interface-decision-record.md": bundle_doc(
                "Interface Decision Record: Agent Equipment Config",
                """\
                ## Requirement

                Agent Equipment Config needs typed schema fragment registration,
                deterministic merge behavior, config-diff output, and
                effective-config output.

                ## Vision alignment

                The equipment projects deterministic configuration concerns into
                typed data, scripts, tools, hooks, approvals, and config rather
                than a single skill.

                ## Decision

                Use TOML for human-authored config and JSON-compatible objects
                for schemas, diagnostics, audit records, and tool output.
                """,
            ),
            "specs/agent-equipment-config/security-control-classification.md": bundle_doc(
                "Security and Control Classification: Agent Equipment Config",
                """\
                ## Scope

                This classification covers the v0 contract, not a runtime engine.

                ## Controls

                Secret references do not store secret values. Non-overridable
                policy, untrusted config, local-only state, and mutation gates
                are represented in structured diagnostics. Policy Authority
                constrains later overrides and lower-authority layers.
                """,
            ),
            "specs/agent-equipment-config/pressure-scenarios.md": bundle_doc(
                "Pressure Scenarios: Agent Equipment Config",
                """\
                ## Issue Tracker Ops effective config

                Issue Tracker Ops is the primary pressure scenario for tracker
                write policy, priority selection, dependency feasibility,
                dry-run versus execute behavior, external disclosure, partial
                onboarding, and stale config.
                """,
            ),
            "specs/agent-equipment-config/validation-plan.md": bundle_doc(
                "Validation Plan: Agent Equipment Config",
                """\
                ## Deterministic checks

                python3.14 -m unittest tests.test_agent_equipment_config
                Validation covers absent config equipment, partial config,
                conflicting layers, semantic validators, schema migration,
                session overrides, local-only overrides, committed config,
                multi-equipment composition, enforcement projection, secret
                references, and handoff ingestion.
                """,
            ),
            "specs/agent-equipment-config/closeout-evidence-plan.md": bundle_doc(
                "Closeout Evidence Plan: Agent Equipment Config",
                """\
                ## Evidence

                Closeout records validator results, config-diff and
                effective-config contract coverage, Issue Tracker Ops pressure
                scenario coverage, child issue projection, and security review
                disposition.
                """,
            ),
        }

    def write_all_specs(self, root: Path, overrides: dict[str, str] | None = None) -> None:
        specs = {
            "specs/agent-ops.md": self.valid_spec(
                "Agent Ops Spec",
                """\
                TOML config stores durable owner and runbook config.
                The config drives Agent behavior, hook behavior, and other configurable aspects.
                Settings use sensibly typed values.
                Autonomy levels: off, advisory, assisted, supervised, autonomous, forbidden.
                Safe defaults require advance approval before automation.
                Policy enforcement blocks violations when the harness supports blocking and otherwise uses advisory fallback.
                """,
            ),
            "specs/periodic-actions.md": self.valid_spec(
                "Periodic Actions Spec",
                """\
                First-session install prompt persists the choice locally.
                List, view, install, uninstall, trigger-now, and edit-period behavior are required.
                Mechanism selection order: native scheduled agent actions, active loop or heartbeat, suitable hook, inference-driven pre/post task check.
                Suggested storage: .agent-ops/.
                """,
            ),
            "specs/harness-capability-refresh.md": self.valid_spec(
                "Harness Capability Refresh Spec",
                """\
                Required harnesses: Codex, OpenClaw, Hermes Agent, Claude Code, Cursor, OpenCode.
                Required tracked fields: current version, checked-at timestamp, source URLs, supported Harness Component types, key affordances, known limitations, scheduling mechanisms, hook/event names, skill discovery paths, plugin interfaces, MCP behavior.
                Change-response issue behavior creates a high-priority issue with current version, previous version, capability affected, source evidence, expected Forge impact, and suggested Smith task.
                Fallback issue candidate path: issues/pending/high/.
                Weekly starting cadence.
                Prioritization order: security-relevant behavior, hook blocking semantics, permissions and sandboxing, scheduling, skill discovery/context behavior, plugin packaging, MCP tool exposure and context bloat.
                """,
            ),
        }
        specs.update(self.valid_config_bundle())
        specs.update(overrides or {})
        for relative_path, content in specs.items():
            self.write_spec(root, relative_path, content)

    def test_run_requires_all_spec_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = run(root)

        for relative_path in self.required_spec_paths:
            self.assertIn(
                CheckResult(f"required_path:{relative_path}", False, "missing", relative_path),
                results,
            )

    def test_validate_specs_accepts_complete_specs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_specs(root)

            results = validate_specs(root)

        self.assertTrue(all(result.ok for result in results), results)

    def test_validate_specs_requires_promotion_state_specified(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_specs(
                root,
                {
                    "specs/agent-ops.md": self.valid_spec(
                        "Agent Ops Spec",
                        "TOML owner runbook autonomy levels safe defaults policy enforcement Codex OpenClaw Hermes Agent Claude Code Cursor OpenCode.",
                    ).replace("Promotion state: specified\n", "")
                },
            )

            results = validate_specs(root)

        self.assertIn(
            CheckResult(
                "spec:promotion:specs/agent-ops.md",
                False,
                "missing Promotion state: specified",
                "specs/agent-ops.md",
            ),
            results,
        )

    def test_validate_specs_requires_sections(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_specs(
                root,
                {
                    "specs/periodic-actions.md": """\
                        # Periodic Actions Spec

                        Status: Equipment Blueprint
                        Promotion state: specified

                        ## Purpose

                        Content.
                        """
                },
            )

            results = validate_specs(root)

        self.assertIn(
            CheckResult(
                "spec:section:specs/periodic-actions.md:Acceptance criteria",
                False,
                "missing section: Acceptance criteria",
                "specs/periodic-actions.md",
            ),
            results,
        )

    def test_validate_specs_requires_agent_ops_content(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_specs(
                root,
                {
                    "specs/agent-ops.md": self.valid_spec(
                        "Agent Ops Spec",
                        "Autonomy levels and safe defaults are required.",
                    )
                },
            )

            results = validate_specs(root)

        self.assertIn(
            CheckResult(
                "spec:text:specs/agent-ops.md:TOML",
                False,
                "missing TOML",
                "specs/agent-ops.md",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "spec:text:specs/agent-ops.md:policy enforcement",
                False,
                "missing policy enforcement",
                "specs/agent-ops.md",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "spec:text:specs/agent-ops.md:hook behavior",
                False,
                "missing hook behavior",
                "specs/agent-ops.md",
            ),
            results,
        )

    def test_validate_specs_requires_each_agent_equipment_config_required_term(self):
        required_terms = [
            "typed schemas",
            "schema fragments",
            "layered config",
            "effective-config",
            "config-diff",
            "Layer Precedence",
            "Policy Authority",
            "later overrides",
            "Config Safety Status",
            "semantic validators",
            "conflict diagnostics",
            "migrations",
            "session-scoped",
            "plain equipment-specific config handoff",
            "secret references",
            "Issue Tracker Ops",
            "python3.14 -m unittest tests.test_agent_equipment_config",
            "policy",
            "Codex",
            "OpenClaw",
            "Hermes Agent",
            "Claude Code",
            "Cursor",
            "OpenCode",
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_specs(root)
            bundle_paths = [root / path for path in self.config_bundle_paths]
            for required_term in required_terms:
                original_texts = {path: path.read_text(encoding="utf-8") for path in bundle_paths}
                for path, original_text in original_texts.items():
                    mutated_text = original_text
                    for variant in {required_term, required_term[:1].upper() + required_term[1:]}:
                        mutated_text = mutated_text.replace(variant, "")
                    if required_term == "secret references":
                        mutated_text = mutated_text.replace("secret reference", "")
                    path.write_text(mutated_text, encoding="utf-8")
                with self.subTest(required_term=required_term):
                    results = validate_specs(root)
                    self.assertIn(
                        CheckResult(
                            name=f"spec:text:specs/agent-equipment-config:{required_term}",
                            ok=False,
                            detail=f"missing {required_term}",
                            path="specs/agent-equipment-config",
                        ),
                        results,
                    )
                for path, original_text in original_texts.items():
                    path.write_text(original_text, encoding="utf-8")

    def test_validate_specs_rejects_config_policy_authority_direction_conflict(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_specs(root)
            security_path = root / "specs/agent-equipment-config/security-control-classification.md"
            security_path.write_text(
                security_path.read_text(encoding="utf-8")
                + "\nPolicy Authority to lower-precedence layers.\n",
                encoding="utf-8",
            )

            results = validate_specs(root)

        self.assertIn(
            CheckResult(
                name="spec:text:specs/agent-equipment-config:forbidden:lower-precedence layers",
                ok=False,
                detail="forbidden lower-precedence layers",
                path="specs/agent-equipment-config",
            ),
            results,
        )

    def test_validate_specs_requires_periodic_actions_content(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_specs(
                root,
                {
                    "specs/periodic-actions.md": self.valid_spec(
                        "Periodic Actions Spec",
                        "First-session install prompt and .agent-ops/ storage are required.",
                    )
                },
            )

            results = validate_specs(root)

        self.assertIn(
            CheckResult(
                "spec:text:specs/periodic-actions.md:trigger-now",
                False,
                "missing trigger-now",
                "specs/periodic-actions.md",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "spec:text:specs/periodic-actions.md:mechanism selection order",
                False,
                "missing mechanism selection order",
                "specs/periodic-actions.md",
            ),
            results,
        )

    def test_validate_specs_requires_harness_refresh_content(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_specs(
                root,
                {
                    "specs/harness-capability-refresh.md": self.valid_spec(
                        "Harness Capability Refresh Spec",
                        "Required harnesses and tracked fields are required.",
                    )
                },
            )

            results = validate_specs(root)

        self.assertIn(
            CheckResult(
                "spec:text:specs/harness-capability-refresh.md:issues/pending/high/",
                False,
                "missing issues/pending/high/",
                "specs/harness-capability-refresh.md",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "spec:text:specs/harness-capability-refresh.md:weekly starting cadence",
                False,
                "missing weekly starting cadence",
                "specs/harness-capability-refresh.md",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "spec:text:specs/harness-capability-refresh.md:key affordances",
                False,
                "missing key affordances",
                "specs/harness-capability-refresh.md",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "spec:text:specs/harness-capability-refresh.md:previous version",
                False,
                "missing previous version",
                "specs/harness-capability-refresh.md",
            ),
            results,
        )

    def test_validate_specs_requires_each_harness_refresh_field(self):
        required_terms = [
            "current version",
            "checked-at timestamp",
            "source URLs",
            "supported Harness Component types",
            "key affordances",
            "known limitations",
            "scheduling mechanisms",
            "hook/event names",
            "skill discovery paths",
            "plugin interfaces",
            "MCP behavior",
            "previous version",
            "capability affected",
            "source evidence",
            "expected Forge impact",
            "suggested Smith task",
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_specs(root)
            path = root / "specs/harness-capability-refresh.md"
            spec_text = path.read_text(encoding="utf-8")
            for required_term in required_terms:
                path.write_text(spec_text.replace(required_term, ""), encoding="utf-8")
                with self.subTest(required_term=required_term):
                    results = validate_specs(root)
                    self.assertIn(
                        CheckResult(
                            f"spec:text:specs/harness-capability-refresh.md:{required_term}",
                            False,
                            f"missing {required_term}",
                            "specs/harness-capability-refresh.md",
                        ),
                        results,
                    )

    def test_validate_specs_requires_non_implementation_boundary(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_specs(
                root,
                {
                    "specs/agent-ops.md": self.valid_spec(
                        "Agent Ops Spec",
                        "TOML owner runbook hook behavior sensibly typed values autonomy levels safe defaults policy enforcement Codex OpenClaw Hermes Agent Claude Code Cursor OpenCode.",
                    ).replace(
                        "This spec describes desired behavior only. It does not implement Agent Equipment.\n",
                        "This spec describes desired behavior only.\n",
                    )
                },
            )

            results = validate_specs(root)

        self.assertIn(
            CheckResult(
                "spec:boundary:specs/agent-ops.md",
                False,
                "missing non-implementation boundary",
                "specs/agent-ops.md",
            ),
            results,
        )

    def test_validate_specs_rejects_readiness_and_installability_claims(self):
        for forbidden_claim in ["production-ready", "is installable"]:
            with tempfile.TemporaryDirectory() as tmpdir:
                root = Path(tmpdir)
                self.write_all_specs(
                    root,
                    {
                        "specs/periodic-actions.md": self.valid_spec(
                            "Periodic Actions Spec",
                            f"""\
                            First-session install prompt persists the choice locally.
                            List, view, install, uninstall, trigger-now, and edit-period behavior are required.
                            Mechanism selection order: native scheduled agent actions, active loop or heartbeat, suitable hook, inference-driven pre/post task check.
                            Suggested storage: .agent-ops/.
                            This spec {forbidden_claim}.
                            """,
                        )
                    },
                )

                results = validate_specs(root)

            with self.subTest(forbidden_claim=forbidden_claim):
                self.assertIn(
                    CheckResult(
                        f"spec:claim:specs/periodic-actions.md:{forbidden_claim}",
                        False,
                        f"forbidden readiness claim: {forbidden_claim}",
                        "specs/periodic-actions.md",
                    ),
                    results,
                )

    def test_validate_specs_accepts_harness_specific_starting_points(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_specs(
                root,
                {
                    "specs/periodic-actions.md": self.valid_spec(
                        "Periodic Actions Spec",
                        """\
                        First-session install prompt persists the choice locally.
                        List, view, install, uninstall, trigger-now, and edit-period behavior are required.
                        Mechanism selection order: native scheduled agent actions, active loop or heartbeat, suitable hook, inference-driven pre/post task check.
                        Suggested storage: .agent-ops/.
                        """,
                    ).replace("## Harness projections", "## Harness-specific starting points")
                },
            )

            results = validate_specs(root)

        self.assertTrue(all(result.ok for result in results), results)


if __name__ == "__main__":
    unittest.main()
