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
    validate_examples,
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
            "Docs/config/scripts/hooks/skills/agents/plugins",
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
    canonical_doc_required_text = {
        "docs/smith-runbook.md": [
            "docs, config, scripts, hooks, skills, Agent Profiles, plugins, and templates are discoverable from the Framework path",
        ],
    }

    def write_canonical_doc(self, root: Path, relative_path: str, sections: list[str] | None = None) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        section_markdown = "\n".join(f"## {section}\n\nContent.\n" for section in (sections or self.canonical_docs[relative_path]))
        required_text = "\n".join(self.canonical_doc_required_text.get(relative_path, []))
        path.write_text(f"# {path.stem}\n\nStatus: Framework Seed\n\n{section_markdown}\n{required_text}\n", encoding="utf-8")

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
             * Side-effect classification: read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation.
             * Approval behavior: require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation.
             * Failure handling: fail closed for unsafe mutations.
             */
            export const hookContract = {
              sideEffectClassification: "read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation",
              approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
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

    def test_validate_templates_requires_hook_external_disclosure_classification(self):
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
                "template:hook:templates/hook/hook.ts:external disclosure classification",
                False,
                "side-effect classification must include external disclosure",
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

                Status: Framework Example
                Promotion state: example

                This Framework Example is not Published Agent Equipment and is not installable.
                Trace: capability card -> [interface decision record](interface-decision-record.md) -> projected components.
                """,
            "interface-decision-record.md": """\
                # Interface Decision Record: Example capability

                Status: Framework Example
                Promotion state: example

                This Framework Example is not Published Agent Equipment and is not installable.
                Trace: [capability card](capability-card.md) -> interface decision record -> [projected components](projected-components.md).
                """,
            "projected-components.md": """\
                # Projected Components: Example capability

                Status: Framework Example
                Promotion state: example

                This Framework Example is not Published Agent Equipment and is not installable.
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

                            This Framework Example is not Published Agent Equipment and is not installable.
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
                "missing Status: Framework Example",
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

                            Status: Framework Example

                            This Framework Example is not Published Agent Equipment and is not installable.
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

                            Status: Framework Example
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

                            Status: Framework Example
                            Promotion state: example

                            This Framework Example is not Published Agent Equipment.
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

                            Status: Framework Example
                            Promotion state: example

                            This Framework Example is not Published Agent Equipment and is not installable.
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

    def test_validate_examples_rejects_published_or_production_claims(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_examples(
                root,
                {
                    "docs-research": {
                        "capability-card.md": """\
                            # Capability Card: Docs research

                            Status: Framework Example
                            Promotion state: example

                            This Framework Example is not Published Agent Equipment and is not installable.
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

                            Status: Framework Example
                            Promotion state: example

                            This Framework Example is not Published Agent Equipment and is not installable.
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


if __name__ == "__main__":
    unittest.main()
