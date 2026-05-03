import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "render-prompt-context-report.py"
)


def load_renderer_module():
    spec = importlib.util.spec_from_file_location(
        "render_prompt_context_report", SCRIPT_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load render-prompt-context-report module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class RenderPromptContextReportTests(unittest.TestCase):
    def run_renderer(self, payload: dict) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH)],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=False,
        )

    def sample_payload(self) -> dict:
        return {
            "token_method": "o200k_base",
            "approximate": False,
            "rules": {
                "source": "manifest_spec",
                "section_totals": [
                    {
                        "section": "always_applied_workspace_rules",
                        "tokens": 200,
                        "count": 2,
                        "groups": [
                            {"group": "AGENTS.md", "tokens": 120, "count": 1},
                            {"group": ".cursor/rules", "tokens": 80, "count": 1},
                        ],
                    },
                    {
                        "section": "user_rules",
                        "tokens": 100,
                        "count": 2,
                        "groups": [
                            {"group": "user_rule", "tokens": 100, "count": 2},
                        ],
                    },
                ],
            },
            "skills": {
                "source": "prompt_text",
                "location_totals": [
                    {
                        "location": "plugin",
                        "tokens": 1000,
                        "count": 4,
                        "groups": [
                            {"group": "figma", "tokens": 600, "count": 2},
                            {"group": "superpowers", "tokens": 400, "count": 2},
                        ],
                    },
                    {
                        "location": "repo_local",
                        "tokens": 500,
                        "count": 2,
                        "groups": [
                            {"group": "developing", "tokens": 300, "count": 1},
                            {"group": "others", "tokens": 200, "count": 1},
                        ],
                    },
                ],
            },
            "mcps": {
                "source": "manifest_spec",
                "location_totals": [
                    {
                        "location": "core",
                        "tokens": 300,
                        "count": 1,
                        "groups": [
                            {"group": "browser", "tokens": 300, "count": 1},
                        ],
                    },
                    {
                        "location": "plugin",
                        "tokens": 150,
                        "count": 2,
                        "groups": [
                            {"group": "context7", "tokens": 100, "count": 1},
                            {"group": "tldraw", "tokens": 50, "count": 1},
                        ],
                    },
                ],
            },
            "known_total": {
                "components": {
                    "rules_catalog": 300,
                    "skills_catalog": 1500,
                    "mcp_catalog": 450,
                },
                "tokens": 2250,
            },
            "excluded": [
                "hidden_system_layers",
                "hidden_developer_layers",
                "opaque_transport_or_wrapper_overhead",
            ],
        }

    def test_renders_decorated_header_and_tree(self) -> None:
        completed_process = self.run_renderer(self.sample_payload())

        self.assertEqual(completed_process.returncode, 0, completed_process.stderr)
        rendered = completed_process.stdout
        self.assertIn("╔", rendered)
        self.assertIn("PRE-PROMPT CONTEXT REPORT", rendered)
        self.assertIn("├──", rendered)
        self.assertIn("└──", rendered)
        self.assertIn("│  ├──", rendered)

    def test_renders_bars_for_all_quantified_rows_with_alignment(self) -> None:
        completed_process = self.run_renderer(self.sample_payload())

        self.assertEqual(completed_process.returncode, 0, completed_process.stderr)
        rendered_lines = completed_process.stdout.splitlines()

        high_level_lines = [
            line
            for line in rendered_lines
            if "rules_catalog" in line
            or "skills_catalog" in line
            or "mcp_catalog" in line
            or "known_total" in line
        ]
        self.assertTrue(high_level_lines)
        self.assertTrue(all("[" in line and "]" in line for line in high_level_lines))
        self.assertEqual(len({line.index("[") for line in high_level_lines}), 1)

        skills_start = rendered_lines.index("Skills by location") + 1
        mcps_start = rendered_lines.index("MCPs by location")
        skills_lines = rendered_lines[skills_start:mcps_start]
        quantified_skill_lines = [
            line for line in skills_lines if "[" in line and "]" in line
        ]
        self.assertTrue(quantified_skill_lines)
        self.assertEqual(len({line.index("[") for line in quantified_skill_lines}), 1)

    def test_child_bars_are_relative_to_parent(self) -> None:
        completed_process = self.run_renderer(self.sample_payload())

        self.assertEqual(completed_process.returncode, 0, completed_process.stderr)
        rendered = completed_process.stdout
        self.assertIn("├── plugin", rendered)
        self.assertIn("│  ├── figma", rendered)
        self.assertIn("│  └── superpowers", rendered)
        self.assertIn("[████████████████████]", rendered)
        self.assertRegex(rendered, r"superpowers.*\[[^\n]*░")

    def test_renders_duplicate_entries_after_mcp_section_with_boxed_legend(
        self,
    ) -> None:
        payload = self.sample_payload()
        payload["skills"].update(
            {
                "duplicate_target_count": 1,
                "duplicate_target_entry_count": 2,
                "duplicate_target_excess_count": 1,
                "duplicate_target_excess_tokens": 120,
                "duplicate_targets": [
                    {
                        "skill": "repo-skill",
                        "target": "/tmp/workspace/.agents/skills/repo-skill/SKILL.md",
                        "count": 2,
                        "excess_tokens": 120,
                        "path_counts": [
                            {
                                "path": "/tmp/workspace/.agents/skills/repo-skill/SKILL.md",
                                "count": 1,
                            },
                            {
                                "path": "/tmp/workspace/.claude/skills/repo-skill/SKILL.md",
                                "count": 1,
                            },
                        ],
                    }
                ],
            }
        )
        payload["mcps"].update(
            {
                "duplicate_server_count": 1,
                "duplicate_server_entry_count": 2,
                "duplicate_server_excess_count": 1,
                "duplicate_server_excess_tokens": 55,
                "duplicate_servers": [
                    {
                        "name": "cursor-ide-browser",
                        "count": 2,
                        "excess_count": 1,
                        "excess_tokens": 55,
                    }
                ],
            }
        )

        completed_process = self.run_renderer(payload)

        self.assertEqual(completed_process.returncode, 0, completed_process.stderr)
        self.assertLess(
            completed_process.stdout.index("MCPs by location"),
            completed_process.stdout.index("Duplicate entries"),
        )
        self.assertIn("├── skills", completed_process.stdout)
        self.assertIn("repo-skill [◆ ●]", completed_process.stdout)
        self.assertIn("└── mcps", completed_process.stdout)
        self.assertIn("cursor-ide-browser", completed_process.stdout)
        self.assertIn("DUPLICATE MARKER LEGEND", completed_process.stdout)
        self.assertIn("╔", completed_process.stdout)
        self.assertIn("│", completed_process.stdout)
        rendered_lines = completed_process.stdout.splitlines()
        legend_start = next(
            index
            for index, line in enumerate(rendered_lines)
            if "DUPLICATE MARKER LEGEND" in line
        )
        self.assertTrue(rendered_lines[legend_start].startswith("╔"))
        legend_lines = rendered_lines[legend_start:]
        boxed_lines = [
            line for line in legend_lines if line.startswith(("╔", "║", "╚"))
        ]
        self.assertEqual(len({len(line) for line in boxed_lines}), 1)
        self.assertIn("◆ │ /tmp/workspace/.agents/skills", completed_process.stdout)
        self.assertIn("● │ /tmp/workspace/.claude/skills", completed_process.stdout)
        leading_lines = completed_process.stdout.split("Duplicate entries", 1)[
            0
        ].splitlines()
        expected_width = max(len(line) for line in leading_lines)
        self.assertEqual(len(boxed_lines[0]), expected_width)

    def test_duplicate_marker_palette_excludes_known_wide_glyphs(self) -> None:
        module = load_renderer_module()

        known_wide_glyphs = {"⬟", "⬠", "⬢", "⬡", "⬣", "⬨", "⬤", "⬯"}

        self.assertTrue(known_wide_glyphs.isdisjoint(module.DUPLICATE_MARKERS))

    def test_renders_exact_path_repetition_with_marker_count(self) -> None:
        payload = self.sample_payload()
        payload["skills"].update(
            {
                "duplicate_target_count": 1,
                "duplicate_target_entry_count": 2,
                "duplicate_target_excess_count": 1,
                "duplicate_target_excess_tokens": 90,
                "duplicate_targets": [
                    {
                        "target": "/tmp/home/.agents/skills/repeated-skill/SKILL.md",
                        "count": 2,
                        "excess_tokens": 90,
                        "path_counts": [
                            {
                                "path": "/tmp/home/.agents/skills/repeated-skill/SKILL.md",
                                "count": 2,
                            }
                        ],
                    }
                ],
            }
        )

        completed_process = self.run_renderer(payload)

        self.assertEqual(completed_process.returncode, 0, completed_process.stderr)
        self.assertIn(
            "repeated-skill [◆×2]",
            completed_process.stdout,
        )

    def test_renders_omitted_duplicate_paths_when_marker_pool_is_exhausted(
        self,
    ) -> None:
        module = load_renderer_module()
        payload = self.sample_payload()
        marker_count = len(module.DUPLICATE_MARKERS)
        path_counts = [
            {
                "path": f"/tmp/home/collection-{index}/skills/overflow-skill/SKILL.md",
                "count": 1,
            }
            for index in range(marker_count + 1)
        ]
        payload["skills"].update(
            {
                "duplicate_target_count": 1,
                "duplicate_target_entry_count": len(path_counts),
                "duplicate_target_excess_count": len(path_counts) - 1,
                "duplicate_target_excess_tokens": 90,
                "duplicate_targets": [
                    {
                        "skill": "overflow-skill",
                        "target": "/tmp/home/.agents/skills/overflow-skill/SKILL.md",
                        "count": len(path_counts),
                        "excess_tokens": 90,
                        "path_counts": path_counts,
                    }
                ],
            }
        )

        completed_process = self.run_renderer(payload)

        self.assertEqual(completed_process.returncode, 0, completed_process.stderr)
        self.assertIn("+1 collections", completed_process.stdout)

    def test_reuses_same_marker_for_collection_across_duplicate_rows(self) -> None:
        payload = self.sample_payload()
        payload["skills"].update(
            {
                "duplicate_target_count": 2,
                "duplicate_target_entry_count": 4,
                "duplicate_target_excess_count": 2,
                "duplicate_target_excess_tokens": 180,
                "duplicate_targets": [
                    {
                        "skill": "alpha-skill",
                        "target": "alpha-skill",
                        "count": 2,
                        "excess_tokens": 100,
                        "path_counts": [
                            {
                                "path": "/tmp/repo/.agents/skills/alpha-skill/SKILL.md",
                                "count": 1,
                            },
                            {
                                "path": "/tmp/plugin/skills/alpha-skill/SKILL.md",
                                "count": 1,
                            },
                        ],
                    },
                    {
                        "skill": "beta-skill",
                        "target": "beta-skill",
                        "count": 2,
                        "excess_tokens": 80,
                        "path_counts": [
                            {
                                "path": "/tmp/repo/.agents/skills/beta-skill/SKILL.md",
                                "count": 1,
                            },
                            {
                                "path": "/tmp/plugin/skills/beta-skill/SKILL.md",
                                "count": 1,
                            },
                        ],
                    },
                ],
            }
        )

        completed_process = self.run_renderer(payload)

        self.assertEqual(completed_process.returncode, 0, completed_process.stderr)
        self.assertIn("alpha-skill [◆ ●]", completed_process.stdout)
        self.assertIn("beta-skill [◆ ●]", completed_process.stdout)
        self.assertEqual(
            completed_process.stdout.count("◆ │ /tmp/repo/.agents/skills"), 1
        )
        self.assertEqual(completed_process.stdout.count("● │ /tmp/plugin/skills"), 1)

    def test_priority_elides_collection_roots_to_report_width(self) -> None:
        module = load_renderer_module()
        home_path = str(Path.home())
        path = (
            f"{home_path}/.cursor/plugins/cache/cursor-public/figma/"
            "3590366424deba5651026319b71b291d10004f1f9ea58dae5e5/skills"
        )

        label = module.priority_elide_path(path, 72)

        self.assertLessEqual(len(label), 72)
        self.assertTrue(label.startswith("~/"))
        self.assertIn("cursor-public/figma", label)
        self.assertTrue(label.endswith("/skills"))
        self.assertIn("…", label)

        short_label = module.priority_elide_path(f"{home_path}/.agents/skills", 72)

        self.assertEqual(short_label, "~/.agents/skills")


if __name__ == "__main__":
    unittest.main()
