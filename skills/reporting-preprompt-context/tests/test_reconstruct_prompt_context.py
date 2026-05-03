import importlib.util
import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "reconstruct-prompt-context.py"
)
WORKSPACE_ROOT = Path(__file__).resolve().parents[4]
HOME_DIR = Path.home()


def load_module():
    spec = importlib.util.spec_from_file_location(
        "reconstruct_prompt_context", SCRIPT_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load reconstruct-prompt-context module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ReconstructPromptContextTests(unittest.TestCase):
    def run_process(
        self,
        *args: str,
        input_text: str | None = None,
        workspace_root: Path | None = None,
        home_dir: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "--workspace-root",
                str(workspace_root or WORKSPACE_ROOT),
                "--home-dir",
                str(home_dir or HOME_DIR),
                "--allow-proxy",
                "--proxy-after-tiktoken-failure",
                *args,
            ],
            check=False,
            capture_output=True,
            input=input_text,
            text=True,
        )

    def run_script(self, prompt_text: str) -> dict:
        with tempfile.TemporaryDirectory() as temporary_directory:
            prompt_path = Path(temporary_directory) / "prompt.txt"
            prompt_path.write_text(textwrap.dedent(prompt_text).strip() + "\n")

            completed_process = self.run_process("--prompt-text-file", str(prompt_path))
            completed_process.check_returncode()

        return json.loads(completed_process.stdout)

    def run_manifest_spec(
        self,
        manifest_spec: dict,
        *,
        workspace_root: Path | None = None,
        home_dir: Path | None = None,
    ) -> dict:
        with tempfile.TemporaryDirectory() as temporary_directory:
            spec_path = Path(temporary_directory) / "manifest-spec.json"
            spec_path.write_text(json.dumps(manifest_spec))

            completed_process = self.run_process(
                "--manifest-spec-file",
                str(spec_path),
                workspace_root=workspace_root,
                home_dir=home_dir,
            )
            completed_process.check_returncode()

        return json.loads(completed_process.stdout)

    def run_manifest_spec_process(
        self,
        manifest_spec: dict,
        *,
        workspace_root: Path | None = None,
        home_dir: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temporary_directory:
            spec_path = Path(temporary_directory) / "manifest-spec.json"
            spec_path.write_text(json.dumps(manifest_spec))

            return self.run_process(
                "--manifest-spec-file",
                str(spec_path),
                workspace_root=workspace_root,
                home_dir=home_dir,
            )

    def write_skill(self, skill_path: Path, description: str) -> None:
        skill_path.parent.mkdir(parents=True, exist_ok=True)
        skill_path.write_text(
            textwrap.dedent(
                f"""\
                ---
                name: {skill_path.parent.name}
                description: {description}
                ---

                # {skill_path.parent.name}
                """
            )
        )

    def write_mcp_server(
        self, server_path: Path, server_name: str, instructions: str | None = None
    ) -> None:
        server_path.mkdir(parents=True, exist_ok=True)
        (server_path / "SERVER_METADATA.json").write_text(
            json.dumps(
                {"serverIdentifier": server_name, "serverName": server_name}, indent=2
            )
        )
        if instructions is not None:
            (server_path / "INSTRUCTIONS.md").write_text(instructions)

    def write_rule(self, rule_path: Path, content: str) -> None:
        rule_path.parent.mkdir(parents=True, exist_ok=True)
        rule_path.write_text(content)

    def test_requires_prompt_snapshot_by_default(self) -> None:
        completed_process = self.run_process()

        self.assertNotEqual(completed_process.returncode, 0)
        error_payload = json.loads(completed_process.stderr)
        self.assertEqual(error_payload["error"], "prompt_snapshot_required")

    def test_rejects_eager_proxy_mode_without_acknowledged_tiktoken_failure(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            prompt_path = Path(temporary_directory) / "prompt.txt"
            prompt_path.write_text("<agent_skills></agent_skills>\n")

            completed_process = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "--workspace-root",
                    str(WORKSPACE_ROOT),
                    "--home-dir",
                    str(HOME_DIR),
                    "--prompt-text-file",
                    str(prompt_path),
                    "--allow-proxy",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(completed_process.returncode, 0)
        error_payload = json.loads(completed_process.stderr)
        self.assertEqual(error_payload["error"], "proxy_acknowledgement_required")

    def test_rejects_multiple_prompt_snapshot_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            spec_path = Path(temporary_directory) / "manifest-spec.json"
            spec_path.write_text(json.dumps({"skills": []}))

            completed_process = self.run_process(
                "--prompt-text-stdin",
                "--manifest-spec-file",
                str(spec_path),
                input_text="<agent_skills></agent_skills>",
            )

        self.assertNotEqual(completed_process.returncode, 0)
        error_payload = json.loads(completed_process.stderr)
        self.assertEqual(error_payload["error"], "multiple_prompt_snapshot_sources")

    def test_rejects_malformed_skill_entries_instead_of_undercounting(self) -> None:
        prompt_text = """
        <agent_skills>
        <available_skills description="Skills the agent can use.">
        <agent_skill>missing fullPath</agent_skill>
        </available_skills>
        </agent_skills>
        """

        completed_process = self.run_process(
            "--prompt-text-stdin",
            input_text=textwrap.dedent(prompt_text),
        )

        self.assertNotEqual(completed_process.returncode, 0)
        error_payload = json.loads(completed_process.stderr)
        self.assertEqual(error_payload["error"], "prompt_context_reconstruction_failed")
        self.assertIn("missing `fullPath`", error_payload["message"])

    def test_rejects_malformed_mcp_entries_instead_of_undercounting(self) -> None:
        prompt_text = """
        <mcp_file_system>
        <mcp_file_system_servers>
        <mcp_file_system_server folderPath="/tmp/browser">cursor-ide-browser</mcp_file_system_server>
        </mcp_file_system_servers>
        </mcp_file_system>
        """

        completed_process = self.run_process(
            "--prompt-text-stdin",
            input_text=textwrap.dedent(prompt_text),
        )

        self.assertNotEqual(completed_process.returncode, 0)
        error_payload = json.loads(completed_process.stderr)
        self.assertEqual(error_payload["error"], "prompt_context_reconstruction_failed")
        self.assertIn("missing `name`", error_payload["message"])

    def test_requestable_rule_manifest_entries_require_descriptions(self) -> None:
        module = load_module()
        valid_prompt_text = module.build_rules_prompt_text_from_manifest_spec(
            {
                "rules": {
                    "agent_requestable_workspace_rules": [
                        {
                            "path": "/absolute/path/to/rule.mdc",
                            "description": "A visible description",
                        }
                    ]
                }
            }
        )

        self.assertIn('fullPath="/absolute/path/to/rule.mdc"', valid_prompt_text)
        self.assertIn(">A visible description<", valid_prompt_text)

        with self.assertRaisesRegex(ValueError, "path and description fields"):
            module.build_rules_prompt_text_from_manifest_spec(
                {
                    "rules": {
                        "agent_requestable_workspace_rules": [
                            "/absolute/path/to/rule.mdc"
                        ]
                    }
                }
            )

        with self.assertRaisesRegex(ValueError, "Manifest entry must provide one of"):
            module.build_rules_prompt_text_from_manifest_spec(
                {
                    "rules": {
                        "agent_requestable_workspace_rules": [
                            {"path": "/absolute/path/to/rule.mdc"}
                        ]
                    }
                }
            )

    def test_user_rule_manifest_entries_are_bare_strings(self) -> None:
        completed_process = self.run_manifest_spec_process(
            {"rules": {"user_rules": [{"text": "Do the thing."}]}}
        )

        self.assertNotEqual(completed_process.returncode, 0)
        error_payload = json.loads(completed_process.stderr)
        self.assertEqual(error_payload["error"], "prompt_context_reconstruction_failed")
        self.assertIn(
            "User rule manifest entries must be strings", error_payload["message"]
        )

    def test_allows_explicit_filesystem_fallback(self) -> None:
        completed_process = self.run_process("--allow-filesystem-fallback")
        completed_process.check_returncode()

        report = json.loads(completed_process.stdout)
        self.assertEqual(report["skills"]["source"], "filesystem")
        self.assertEqual(report["mcps"]["source"], "filesystem")
        self.assertEqual(report["rules"]["source"], "filesystem")

    def test_accepts_prompt_snapshot_via_stdin(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            workspace_root = temporary_root / "workspace"
            home_dir = temporary_root / "home"
            workspace_root.mkdir(parents=True)
            resolved_workspace_root = workspace_root.resolve()
            prompt_text = f"""
            <agent_skills>
            <available_skills description="Skills the agent can use.">
            <agent_skill fullPath="{resolved_workspace_root}/.agents/skills/repo-skill/SKILL.md">repo skill</agent_skill>
            </available_skills>
            </agent_skills>
            """

            completed_process = self.run_process(
                "--prompt-text-stdin",
                input_text=textwrap.dedent(prompt_text),
                workspace_root=workspace_root,
                home_dir=home_dir,
            )
            completed_process.check_returncode()

            report = json.loads(completed_process.stdout)
        self.assertEqual(report["skills"]["source"], "prompt_text")
        self.assertEqual(
            report["skills"]["location_totals"][0]["location"], "repo_local"
        )
        self.assertEqual(report["skills"]["location_totals"][0]["count"], 1)

    def test_manifest_spec_preserves_repeated_occurrences(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            workspace_root = temporary_root / "workspace"
            home_dir = temporary_root / "home"
            workspace_root.mkdir(parents=True)
            resolved_workspace_root = workspace_root.resolve()
            self.write_rule(workspace_root / "AGENTS.md", "# Agents\n")
            self.write_skill(
                workspace_root / ".agents" / "skills" / "repo-skill" / "SKILL.md",
                "Repo skill",
            )
            slug = workspace_root.resolve().as_posix().lstrip("/").replace("/", "-")
            mcp_root = home_dir / ".cursor" / "projects" / slug / "mcps"
            self.write_mcp_server(mcp_root / "cursor-ide-browser", "cursor-ide-browser")

            manifest_spec = {
                "rules": {
                    "always_applied_workspace_rules": [
                        str(resolved_workspace_root / "AGENTS.md"),
                        str(resolved_workspace_root / "AGENTS.md"),
                    ],
                    "user_rules": [
                        "Do the thing.",
                    ],
                },
                "skills": [
                    str(resolved_workspace_root / ".agents/skills/repo-skill/SKILL.md"),
                    str(resolved_workspace_root / ".agents/skills/repo-skill/SKILL.md"),
                ],
                "mcps": [
                    {"name": "cursor-ide-browser"},
                    {"name": "cursor-ide-browser"},
                ],
            }

            report = self.run_manifest_spec(
                manifest_spec,
                workspace_root=workspace_root,
                home_dir=home_dir,
            )

        self.assertEqual(report["rules"]["source"], "manifest_spec")
        rules_by_section = {
            item["section"]: item for item in report["rules"]["section_totals"]
        }
        self.assertEqual(rules_by_section["always_applied_workspace_rules"]["count"], 2)

        self.assertEqual(report["skills"]["source"], "manifest_spec")
        self.assertEqual(
            report["skills"]["multiplicity_model"], "explicit_occurrence_spec"
        )
        self.assertEqual(report["skills"]["entry_occurrence_count"], 2)
        self.assertEqual(report["skills"]["unique_key_count"], 1)
        self.assertEqual(report["skills"]["duplicate_occurrence_excess"], 1)
        self.assertEqual(report["skills"]["duplicate_target_count"], 1)
        self.assertEqual(report["skills"]["duplicate_target_entry_count"], 2)
        self.assertEqual(report["skills"]["duplicate_target_excess_count"], 1)
        self.assertGreater(report["skills"]["duplicate_target_excess_tokens"], 0)
        self.assertEqual(
            report["skills"]["duplicate_targets"][0]["duplicate_kind"], "same_target"
        )
        self.assertEqual(
            report["skills"]["location_totals"][0]["location"], "repo_local"
        )
        self.assertEqual(report["skills"]["location_totals"][0]["count"], 2)

        self.assertEqual(report["mcps"]["source"], "manifest_spec")
        self.assertEqual(
            report["mcps"]["multiplicity_model"], "explicit_occurrence_spec"
        )
        self.assertEqual(report["mcps"]["entry_occurrence_count"], 2)
        self.assertEqual(report["mcps"]["unique_key_count"], 1)
        self.assertEqual(report["mcps"]["duplicate_occurrence_excess"], 1)
        self.assertEqual(report["mcps"]["duplicate_server_count"], 1)
        self.assertEqual(report["mcps"]["duplicate_server_entry_count"], 2)
        self.assertEqual(report["mcps"]["duplicate_server_excess_count"], 1)
        self.assertGreater(report["mcps"]["duplicate_server_excess_tokens"], 0)
        self.assertEqual(
            report["mcps"]["duplicate_servers"][0]["name"], "cursor-ide-browser"
        )
        self.assertEqual(report["mcps"]["location_totals"][0]["location"], "core")
        self.assertEqual(report["mcps"]["location_totals"][0]["count"], 2)

    def test_manifest_spec_resolves_mcp_names_from_live_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            workspace_root = temporary_root / "workspace"
            home_dir = temporary_root / "home"
            workspace_root.mkdir(parents=True)
            slug = workspace_root.resolve().as_posix().lstrip("/").replace("/", "-")
            mcp_root = home_dir / ".cursor" / "projects" / slug / "mcps"
            self.write_mcp_server(
                mcp_root / "plugin-custom-foo",
                "plugin-custom-foo",
                'Use "quoted" custom MCP guidance.',
            )

            report = self.run_manifest_spec(
                {"mcps": [{"name": "plugin-custom-foo"}]},
                workspace_root=workspace_root,
                home_dir=home_dir,
            )

        self.assertEqual(report["mcps"]["source"], "manifest_spec")
        self.assertEqual(report["mcps"]["entry_occurrence_count"], 1)
        self.assertEqual(report["mcps"]["location_totals"][0]["location"], "plugin")
        self.assertEqual(
            report["mcps"]["location_totals"][0]["groups"][0]["group"], "custom"
        )

    def test_prompt_text_counts_only_injected_skills_and_preserves_duplicates(
        self,
    ) -> None:
        prompt_text = f"""
        <agent_skills>
        <available_skills description="Skills the agent can use.">
        <agent_skill fullPath="{WORKSPACE_ROOT}/.agents/skills/reporting-preprompt-context/SKILL.md">repo skill</agent_skill>
        <agent_skill fullPath="{HOME_DIR}/.cursor/plugins/cache/cursor-public/superpowers/example/skills/test-driven-development/SKILL.md">plugin skill</agent_skill>
        <agent_skill fullPath="{HOME_DIR}/.cursor/plugins/cache/cursor-public/superpowers/example/skills/test-driven-development/SKILL.md">plugin skill</agent_skill>
        </available_skills>
        </agent_skills>
        """

        report = self.run_script(prompt_text)

        self.assertEqual(report["skills"]["source"], "prompt_text")
        self.assertEqual(report["skills"]["multiplicity_model"], "prompt_occurrences")
        self.assertEqual(report["skills"]["entry_occurrence_count"], 3)
        self.assertEqual(report["skills"]["unique_key_count"], 2)
        self.assertEqual(report["skills"]["duplicate_occurrence_excess"], 1)
        self.assertEqual(report["skills"]["duplicate_target_count"], 1)
        self.assertEqual(report["skills"]["duplicate_target_entry_count"], 2)
        self.assertEqual(report["skills"]["duplicate_target_excess_count"], 1)
        self.assertEqual(
            report["skills"]["duplicate_targets"][0]["duplicate_kind"], "same_target"
        )
        self.assertEqual(
            report["skills"]["location_totals"],
            [
                {
                    "location": "plugin",
                    "tokens": report["skills"]["location_totals"][0]["tokens"],
                    "count": 2,
                    "groups": [
                        {
                            "group": "superpowers",
                            "tokens": report["skills"]["location_totals"][0]["groups"][
                                0
                            ]["tokens"],
                            "count": 2,
                        }
                    ],
                },
                {
                    "location": "repo_local",
                    "tokens": report["skills"]["location_totals"][1]["tokens"],
                    "count": 1,
                    "groups": [
                        {
                            "group": "others",
                            "tokens": report["skills"]["location_totals"][1]["groups"][
                                0
                            ]["tokens"],
                            "count": 1,
                        }
                    ],
                },
            ],
        )

    def test_prompt_text_counts_only_injected_mcps_and_preserves_duplicates(
        self,
    ) -> None:
        prompt_text = """
        <mcp_file_system>
        <mcp_file_system_servers>
        <mcp_file_system_server name="cursor-ide-browser" folderPath="/tmp/browser">cursor-ide-browser</mcp_file_system_server>
        <mcp_file_system_server name="plugin-context7-plugin-context7" folderPath="/tmp/context7">plugin-context7-plugin-context7</mcp_file_system_server>
        <mcp_file_system_server name="plugin-context7-plugin-context7" folderPath="/tmp/context7">plugin-context7-plugin-context7</mcp_file_system_server>
        </mcp_file_system_servers>
        </mcp_file_system>
        """

        report = self.run_script(prompt_text)

        self.assertEqual(report["mcps"]["source"], "prompt_text")
        self.assertEqual(report["mcps"]["multiplicity_model"], "prompt_occurrences")
        self.assertEqual(report["mcps"]["entry_occurrence_count"], 3)
        self.assertEqual(report["mcps"]["unique_key_count"], 2)
        self.assertEqual(report["mcps"]["duplicate_occurrence_excess"], 1)
        location_totals = {
            item["location"]: item for item in report["mcps"]["location_totals"]
        }
        self.assertEqual(location_totals["core"]["count"], 1)
        self.assertEqual(location_totals["core"]["groups"][0]["group"], "browser")
        self.assertEqual(location_totals["plugin"]["count"], 2)
        self.assertEqual(location_totals["plugin"]["groups"][0]["group"], "context7")
        self.assertEqual(location_totals["plugin"]["groups"][0]["count"], 2)

    def test_mcp_grouping_collapses_repeated_adjacent_plugin_segments(self) -> None:
        prompt_text = """
        <mcp_file_system>
        <mcp_file_system_servers>
        <mcp_file_system_server name="plugin-cloudflare-cloudflare-docs" folderPath="/tmp/docs">plugin-cloudflare-cloudflare-docs</mcp_file_system_server>
        <mcp_file_system_server name="plugin-cloudflare-cloudflare-bindings" folderPath="/tmp/bindings">plugin-cloudflare-cloudflare-bindings</mcp_file_system_server>
        </mcp_file_system_servers>
        </mcp_file_system>
        """

        report = self.run_script(prompt_text)

        plugin_location = report["mcps"]["location_totals"][0]
        self.assertEqual(plugin_location["location"], "plugin")
        self.assertEqual(plugin_location["groups"][0]["group"], "cloudflare")

    def test_prompt_text_counts_visible_rules_instead_of_only_agents_md(self) -> None:
        prompt_text = f"""
        <always_applied_workspace_rules>
        <always_applied_workspace_rule name="{WORKSPACE_ROOT}/CLAUDE.md">claude rule</always_applied_workspace_rule>
        <always_applied_workspace_rule name="{WORKSPACE_ROOT}/AGENTS.md">agents rule</always_applied_workspace_rule>
        </always_applied_workspace_rules>
        <agent_requestable_workspace_rules description="These are workspace-level rules that the agent should follow.">
        <agent_requestable_workspace_rule fullPath="{WORKSPACE_ROOT}/.cursor/rules/example.mdc">Example requestable rule</agent_requestable_workspace_rule>
        </agent_requestable_workspace_rules>
        <user_rules description="These are rules set by the user that you should follow if appropriate.">
        <user_rule>Do the thing.</user_rule>
        </user_rules>
        """

        report = self.run_script(prompt_text)

        self.assertEqual(report["rules"]["source"], "prompt_text")
        section_totals = {
            item["section"]: item for item in report["rules"]["section_totals"]
        }
        self.assertEqual(section_totals["always_applied_workspace_rules"]["count"], 2)
        self.assertEqual(
            section_totals["agent_requestable_workspace_rules"]["count"], 1
        )
        self.assertEqual(section_totals["user_rules"]["count"], 1)
        self.assertIn("rules_catalog", report["known_total"]["components"])
        self.assertNotIn("agents_md", report["known_total"]["components"])

    def test_filesystem_fallback_discovers_skills_and_mcps_dynamically(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            workspace_root = temporary_root / "workspace"
            home_dir = temporary_root / "home"
            workspace_root.mkdir(parents=True)

            self.write_skill(
                workspace_root / ".agents" / "skills" / "repo-skill" / "SKILL.md",
                "Repo-local skill",
            )
            self.write_skill(
                home_dir / ".cursor" / "skills-cursor" / "cursor-skill" / "SKILL.md",
                "Cursor skill",
            )
            self.write_skill(
                home_dir
                / ".cursor"
                / "plugins"
                / "cache"
                / "cursor-public"
                / "example-plugin"
                / "1.0.0"
                / "skills"
                / "dynamic-plugin-skill"
                / "SKILL.md",
                "Cursor plugin skill",
            )
            self.write_skill(
                home_dir
                / ".claude"
                / "plugins"
                / "cache"
                / "sample"
                / "plugin"
                / "1.0.0"
                / ".claude"
                / "skills"
                / "claude-plugin-skill"
                / "SKILL.md",
                "Claude plugin skill",
            )
            self.write_skill(
                home_dir
                / ".claude"
                / "plugins"
                / "cache"
                / "sample"
                / "plugin"
                / "1.0.0"
                / ".pi"
                / "skills"
                / "ignored-plugin-skill"
                / "SKILL.md",
                "Ignored plugin skill",
            )

            slug = workspace_root.resolve().as_posix().lstrip("/").replace("/", "-")
            mcp_root = home_dir / ".cursor" / "projects" / slug / "mcps"
            self.write_mcp_server(
                mcp_root / "plugin-example-server", "plugin-example-server"
            )

            completed_process = self.run_process(
                "--allow-filesystem-fallback",
                workspace_root=workspace_root,
                home_dir=home_dir,
            )
            completed_process.check_returncode()
            report = json.loads(completed_process.stdout)

        self.assertEqual(report["skills"]["source"], "filesystem")
        skill_locations = {
            item["location"]: item for item in report["skills"]["location_totals"]
        }
        self.assertEqual(skill_locations["repo_local"]["count"], 1)
        self.assertEqual(skill_locations["cursor"]["count"], 1)
        self.assertEqual(skill_locations["plugin"]["count"], 2)
        plugin_groups = {
            item["group"]: item for item in skill_locations["plugin"]["groups"]
        }
        self.assertEqual(plugin_groups["example-plugin"]["count"], 1)
        self.assertEqual(plugin_groups["sample"]["count"], 1)

        self.assertEqual(report["mcps"]["source"], "filesystem")
        self.assertEqual(report["mcps"]["entry_occurrence_count"], 1)
        self.assertEqual(report["mcps"]["location_totals"][0]["location"], "plugin")
        self.assertEqual(
            report["mcps"]["location_totals"][0]["groups"][0]["group"], "example"
        )
        self.assertNotIn("workspace_root", report)
        self.assertNotIn("home_dir", report)

    def test_filesystem_fallback_counts_and_reports_symlinked_skill_duplicates(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            workspace_root = temporary_root / "workspace"
            home_dir = temporary_root / "home"
            workspace_root.mkdir(parents=True)

            canonical_skill_path = (
                workspace_root / ".agents" / "skills" / "repo-skill" / "SKILL.md"
            )
            self.write_skill(canonical_skill_path, "Repo-local skill")

            claude_skill_root = workspace_root / ".claude" / "skills"
            claude_skill_root.mkdir(parents=True)
            try:
                (claude_skill_root / "repo-skill").symlink_to(
                    "../../.agents/skills/repo-skill",
                    target_is_directory=True,
                )
            except OSError as error:
                self.skipTest(f"Unable to create symlink: {error}")

            completed_process = self.run_process(
                "--allow-filesystem-fallback",
                workspace_root=workspace_root,
                home_dir=home_dir,
            )
            completed_process.check_returncode()
            report = json.loads(completed_process.stdout)

        skill_locations = {
            item["location"]: item for item in report["skills"]["location_totals"]
        }
        self.assertEqual(skill_locations["repo_local"]["count"], 2)
        self.assertEqual(report["skills"]["entry_occurrence_count"], 2)
        self.assertEqual(report["skills"]["unique_key_count"], 2)
        self.assertEqual(report["skills"]["duplicate_occurrence_excess"], 0)
        self.assertEqual(report["skills"]["duplicate_target_count"], 1)
        self.assertEqual(report["skills"]["duplicate_target_entry_count"], 2)
        self.assertEqual(report["skills"]["duplicate_target_excess_count"], 1)
        self.assertGreater(report["skills"]["duplicate_target_excess_tokens"], 0)
        self.assertEqual(
            report["skills"]["duplicate_targets"][0]["unique_path_count"],
            2,
        )
        self.assertEqual(
            report["skills"]["duplicate_targets"][0]["resolved_target_count"],
            1,
        )
        self.assertEqual(
            report["skills"]["duplicate_targets"][0]["skill"], "repo-skill"
        )
        self.assertEqual(
            sorted(
                path_count["count"]
                for path_count in report["skills"]["duplicate_targets"][0][
                    "path_counts"
                ]
            ),
            [1, 1],
        )

    def test_manifest_spec_reports_same_name_duplicate_skills_across_distinct_roots(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            workspace_root = temporary_root / "workspace"
            home_dir = temporary_root / "home"
            workspace_root.mkdir(parents=True)

            claude_skill_path = (
                home_dir / ".claude" / "skills" / "shared-skill" / "SKILL.md"
            )
            agents_skill_path = (
                home_dir / ".agents" / "skills" / "shared-skill" / "SKILL.md"
            )
            self.write_skill(claude_skill_path, "Shared skill from Claude root")
            self.write_skill(agents_skill_path, "Shared skill from agent root")

            report = self.run_manifest_spec(
                {"skills": [str(claude_skill_path), str(agents_skill_path)]},
                workspace_root=workspace_root,
                home_dir=home_dir,
            )

        self.assertEqual(report["skills"]["duplicate_target_count"], 1)
        self.assertEqual(report["skills"]["duplicate_target_entry_count"], 2)
        self.assertEqual(
            report["skills"]["duplicate_targets"][0]["skill"], "shared-skill"
        )
        self.assertEqual(
            report["skills"]["duplicate_targets"][0]["duplicate_kind"], "same_name"
        )
        self.assertEqual(
            report["skills"]["duplicate_targets"][0]["resolved_target_count"],
            2,
        )


if __name__ == "__main__":
    unittest.main()
