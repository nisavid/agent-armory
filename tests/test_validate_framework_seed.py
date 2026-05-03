import json
import tempfile
import textwrap
import unittest
from pathlib import Path

from tools.validate_framework_seed import (
    ACCEPTED_SOURCE_REQUIREMENTS,
    CheckResult,
    REQUIRED_HARNESSES,
    find_markdown_links,
    harness_matrix_rows,
    load_toml,
    render_human,
    run,
    validate_canonical_docs,
    validate_framework_routes,
    validate_harness_catalog,
    validate_markdown_links,
    validate_source_handoff_provenance,
    validate_source_projection,
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


class FrameworkRouteTests(unittest.TestCase):
    def test_validate_framework_routes_requires_agent_and_human_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "AGENTS.md").write_text("# AGENTS\n", encoding="utf-8")
            (root / "README.md").write_text("# README\n", encoding="utf-8")

            results = validate_framework_routes(root)

        self.assertIn(
            CheckResult("framework_route:agent", False, "missing Preloaded Framework Path", "AGENTS.md"),
            results,
        )
        self.assertIn(
            CheckResult("framework_route:human", False, "missing Human Framework Entry", "README.md"),
            results,
        )

    def test_validate_framework_routes_requires_all_preloaded_links(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "AGENTS.md").write_text(
                textwrap.dedent(
                    """
                    # AGENTS

                    ## Framework Path

                    - `docs/equipment-framework.md`
                    - `docs/smith-runbook.md`
                    - `docs/harness-capabilities.md`
                    - `templates/`
                    - `specs/`
                    """
                ),
                encoding="utf-8",
            )
            (root / "README.md").write_text(
                "## Framework\n\nStart with [docs/equipment-framework.md](docs/equipment-framework.md).\n",
                encoding="utf-8",
            )

            results = validate_framework_routes(root)

        self.assertIn(
            CheckResult(
                "framework_route:agent:docs/interface-decision-guide.md",
                False,
                "missing required preloaded route",
                "AGENTS.md",
            ),
            results,
        )

    def test_validate_framework_routes_rejects_unresolved_route_targets(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            (root / "templates").mkdir()
            (root / "specs").mkdir()
            for path in [
                "docs/equipment-framework.md",
                "docs/smith-runbook.md",
                "docs/interface-decision-guide.md",
            ]:
                (root / path).write_text("# Fixture\n", encoding="utf-8")
            (root / "AGENTS.md").write_text(
                textwrap.dedent(
                    """
                    # AGENTS

                    ## Framework Path

                    - `docs/equipment-framework.md`
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
                "## Framework\n\nStart with [docs/equipment-framework.md](docs/equipment-framework.md).\n",
                encoding="utf-8",
            )

            results = validate_framework_routes(root)

        self.assertIn(
            CheckResult(
                "framework_route:target:docs/harness-capabilities.md",
                False,
                "route target missing",
                "AGENTS.md",
            ),
            results,
        )

    def test_validate_framework_routes_rejects_wrong_route_target_kind(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs/equipment-framework.md").mkdir(parents=True)
            (root / "docs/smith-runbook.md").write_text("# Fixture\n", encoding="utf-8")
            (root / "docs/interface-decision-guide.md").write_text("# Fixture\n", encoding="utf-8")
            (root / "docs/harness-capabilities.md").write_text("# Fixture\n", encoding="utf-8")
            (root / "templates").write_text("not a directory\n", encoding="utf-8")
            (root / "specs").mkdir()
            (root / "AGENTS.md").write_text(
                textwrap.dedent(
                    """
                    # AGENTS

                    ## Framework Path

                    - `docs/equipment-framework.md`
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
                "## Framework\n\nStart with [docs/equipment-framework.md](docs/equipment-framework.md).\n",
                encoding="utf-8",
            )

            results = validate_framework_routes(root)

        self.assertIn(
            CheckResult(
                "framework_route:target:docs/equipment-framework.md",
                False,
                "route target not a file",
                "AGENTS.md",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "framework_route:target:templates/",
                False,
                "route target not a directory",
                "AGENTS.md",
            ),
            results,
        )


class CanonicalDocTests(unittest.TestCase):
    canonical_docs = {
        "docs/ubiquitous-language.md": ["Language", "Relationships", "Precision rules"],
        "docs/equipment-framework.md": [
            "Purpose",
            "Least cognitive privilege",
            "Component model",
            "Context management",
            "Security",
            "Maintenance",
        ],
        "docs/smith-runbook.md": [
            "Capability card",
            "Interface decision record",
            "Docs/config/scripts/hooks/skills/profiles/plugins",
            "Pressure Scenario Validation",
            "Equipment Promotion Path",
            "Closeout",
        ],
        "docs/metasmith-runbook.md": [
            "Source handoff preservation",
            "decision projection",
            "Review Until Clean",
            "Harness Fact Refresh",
            "Change set closeout",
            "Issue Projection",
            "downstream Smith specs",
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
    }

    def write_canonical_doc(self, root: Path, relative_path: str, sections: list[str] | None = None) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        section_markdown = "\n".join(f"## {section}\n\nContent.\n" for section in (sections or self.canonical_docs[relative_path]))
        path.write_text(f"# {path.stem}\n\nStatus: Framework Seed\n\n{section_markdown}", encoding="utf-8")

    def write_all_canonical_docs(self, root: Path) -> None:
        for relative_path in self.canonical_docs:
            self.write_canonical_doc(root, relative_path)

    def test_validate_canonical_docs_reports_missing_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = validate_canonical_docs(root)

        self.assertIn(
            CheckResult(
                "canonical_doc:docs/equipment-framework.md",
                False,
                "missing",
                "docs/equipment-framework.md",
            ),
            results,
        )

    def test_validate_canonical_docs_requires_framework_seed_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_canonical_docs(root)
            (root / "docs/equipment-framework.md").write_text(
                "# Equipment Framework\n\n## Purpose\n\nContent.\n",
                encoding="utf-8",
            )

            results = validate_canonical_docs(root)

        self.assertIn(
            CheckResult(
                "canonical_doc:status:docs/equipment-framework.md",
                False,
                "missing Status: Framework Seed",
                "docs/equipment-framework.md",
            ),
            results,
        )

    def test_validate_canonical_docs_ignores_status_in_fenced_code(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_canonical_docs(root)
            fence = "`" * 3
            (root / "docs/equipment-framework.md").write_text(
                f"# Equipment Framework\n\n{fence}\nStatus: Framework Seed\n{fence}\n\n## Purpose\n\nContent.\n",
                encoding="utf-8",
            )

            results = validate_canonical_docs(root)

        self.assertIn(
            CheckResult(
                "canonical_doc:status:docs/equipment-framework.md",
                False,
                "missing Status: Framework Seed",
                "docs/equipment-framework.md",
            ),
            results,
        )

    def test_validate_canonical_docs_requires_sections(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_canonical_docs(root)
            self.write_canonical_doc(root, "docs/equipment-framework.md", sections=["Purpose"])

            results = validate_canonical_docs(root)

        self.assertIn(
            CheckResult(
                "canonical_doc:section:docs/equipment-framework.md:Maintenance",
                False,
                "missing section: Maintenance",
                "docs/equipment-framework.md",
            ),
            results,
        )

    def test_validate_canonical_docs_ignores_sections_in_indented_code(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_canonical_docs(root)
            (root / "docs/equipment-framework.md").write_text(
                textwrap.dedent(
                    """
                    # Equipment Framework

                    Status: Framework Seed

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
                "canonical_doc:section:docs/equipment-framework.md:Maintenance",
                False,
                "missing section: Maintenance",
                "docs/equipment-framework.md",
            ),
            results,
        )

    def test_run_reports_missing_canonical_docs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = run(root)

        self.assertIn(
            CheckResult(
                "required_path:docs/equipment-framework.md",
                False,
                "missing",
                "docs/equipment-framework.md",
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
            (root / "docs/equipment-framework.md").write_text(
                "# Equipment Framework\n\n## Purpose\n\nContent.\n",
                encoding="utf-8",
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "canonical_doc:status:docs/equipment-framework.md",
                False,
                "missing Status: Framework Seed",
                "docs/equipment-framework.md",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "canonical_doc:section:docs/equipment-framework.md:Maintenance",
                False,
                "missing section: Maintenance",
                "docs/equipment-framework.md",
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


if __name__ == "__main__":
    unittest.main()
