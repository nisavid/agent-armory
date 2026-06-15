import importlib.util
import io
import json
import shutil
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from typing import NoReturn
from unittest import mock

from tools import validate_armory_integrity as validator
from tools.validate_armory_integrity import CheckResult, load_toml


PLUGIN_ROOT = Path("plugins/agent-equipment-config")
LAUNCHER_PATH = PLUGIN_ROOT / "mcp/agent_equipment_config_launcher.py"
HOOK_PATH = PLUGIN_ROOT / "hooks/config_write_guard.py"
ROUTING_SKILL_PATH = PLUGIN_ROOT / "skills/agent-equipment-config/SKILL.md"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


def write_launcher_repo_markers(root: Path) -> None:
    server = root / "tools/agent_equipment_config_mcp_server.py"
    server.parent.mkdir(parents=True, exist_ok=True)
    server.write_text("# server\n", encoding="utf-8")
    (root / "inventory").mkdir()
    (root / "inventory/equipment.toml").write_text("", encoding="utf-8")
    marketplace = root / ".agents/plugins/marketplace.json"
    marketplace.parent.mkdir(parents=True, exist_ok=True)
    marketplace.write_text(
        json.dumps(
            {
                "name": "agent-armory",
                "plugins": [
                    {
                        "name": "agent-equipment-config",
                        "source": {
                            "source": "local",
                            "path": "./plugins/agent-equipment-config",
                        },
                    }
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )


class AgentEquipmentConfigCodexPluginValidationTests(unittest.TestCase):
    def write_text(self, root: Path, relative_path: str | Path, content: str) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")

    def write_json(self, root: Path, relative_path: str | Path, data: object) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def write_valid_plugin_fixture(self, root: Path) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        shutil.copytree(repo_root / PLUGIN_ROOT, root / PLUGIN_ROOT, dirs_exist_ok=True)
        server = root / "tools/agent_equipment_config_mcp_server.py"
        server.parent.mkdir(parents=True, exist_ok=True)
        server.write_text("# server\n", encoding="utf-8")
        inventory = root / "inventory/equipment.toml"
        inventory.parent.mkdir(parents=True, exist_ok=True)
        inventory.write_text(
            (repo_root / "inventory/equipment.toml").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        marketplace_target = root / ".agents/plugins/marketplace.json"
        marketplace_target.parent.mkdir(parents=True, exist_ok=True)
        marketplace_target.write_text(
            (repo_root / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        for route_target in [
            "docs/equipment/agent-equipment-config.md",
            "docs/equipment/agent-equipment-config-integration.md",
            "specs/agent-equipment-config/mcp-tools.md",
        ]:
            self.write_text(root, route_target, "# route target\n")

    def test_validator_accepts_complete_current_codex_plugin_contract(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_plugin_fixture(root)

            results = validator.validate_agent_equipment_config_codex_plugin(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    "agent_equipment_config_codex_plugin:contract",
                    True,
                    "valid Codex plugin bundle",
                    "plugins/agent-equipment-config",
                )
            ],
        )

    def test_validator_rejects_missing_standalone_mcp_server_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_plugin_fixture(root)
            (root / "tools/agent_equipment_config_mcp_server.py").unlink()

            results = validator.validate_agent_equipment_config_codex_plugin(root)

        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:path:tools/agent_equipment_config_mcp_server.py",
                False,
                "missing",
                "tools/agent_equipment_config_mcp_server.py",
            ),
            results,
        )

    def test_validator_rejects_stale_manifest_metadata_shape(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_plugin_fixture(root)
            manifest = json.loads((root / PLUGIN_ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
            manifest["author"] = "Agent Armory"
            manifest["repository"] = {
                "type": "git",
                "url": "https://github.com/nisavid/agent-armory",
            }
            manifest["apps"] = "./.app.json"
            manifest["interface"]["description"] = "Duplicate install-surface copy."
            self.write_json(root, PLUGIN_ROOT / ".codex-plugin/plugin.json", manifest)

            results = validator.validate_agent_equipment_config_codex_plugin(root)

        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:manifest:author",
                False,
                "author.name and author.url must be non-empty strings",
                "plugins/agent-equipment-config/.codex-plugin/plugin.json",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:manifest:repository",
                False,
                "repository must be https://github.com/nisavid/agent-armory",
                "plugins/agent-equipment-config/.codex-plugin/plugin.json",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:manifest:interface:unexpected",
                False,
                "unexpected interface keys: description",
                "plugins/agent-equipment-config/.codex-plugin/plugin.json",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:manifest:unexpected",
                False,
                "unexpected manifest keys: apps",
                "plugins/agent-equipment-config/.codex-plugin/plugin.json",
            ),
            results,
        )

    def test_validator_rejects_http_mcp_and_missing_write_approval_overrides(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_plugin_fixture(root)
            self.write_json(
                root,
                PLUGIN_ROOT / ".mcp.json",
                {
                    "agent-equipment-config": {
                        "url": "https://example.invalid/mcp",
                        "env": {"SOME_STATIC_ENV": "not-secret"},
                        "default_tools_approval_mode": "never",
                        "tools": {},
                    }
                },
            )

            results = validator.validate_agent_equipment_config_codex_plugin(root)

        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:mcp:agent-equipment-config:default_tools_approval_mode",
                False,
                "default_tools_approval_mode must be prompt",
                "plugins/agent-equipment-config/.mcp.json",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:mcp:agent-equipment-config:unexpected",
                False,
                "unexpected MCP server keys: env, url",
                "plugins/agent-equipment-config/.mcp.json",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:mcp:agent-equipment-config:tools:config.apply",
                False,
                "local-write tool approval_mode must be prompt",
                "plugins/agent-equipment-config/.mcp.json",
            ),
            results,
        )

    def test_validator_rejects_unexpected_mcp_tool_approval_overrides(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_plugin_fixture(root)
            mcp_config = json.loads((root / PLUGIN_ROOT / ".mcp.json").read_text(encoding="utf-8"))
            mcp_config["agent-equipment-config"]["tools"]["future.local_write"] = {
                "approval_mode": "approve"
            }
            self.write_json(root, PLUGIN_ROOT / ".mcp.json", mcp_config)

            results = validator.validate_agent_equipment_config_codex_plugin(root)

        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:mcp:agent-equipment-config:tools:unexpected",
                False,
                "unexpected MCP tool approval overrides: future.local_write",
                "plugins/agent-equipment-config/.mcp.json",
            ),
            results,
        )

    def test_validator_rejects_inert_executables_and_extra_hooks(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_plugin_fixture(root)
            self.write_text(root, HOOK_PATH, "def evaluate(payload):\n    return None\n")
            self.write_text(
                root,
                LAUNCHER_PATH,
                """
                # REPO_SERVER tools/agent_equipment_config_mcp_server.py
                # MARKETPLACE_MARKER find_armory_root os.chdir(root) os.execve return 2
                def launch():
                    return 0
                """,
            )
            hooks = json.loads((root / PLUGIN_ROOT / "hooks/hooks.json").read_text(encoding="utf-8"))
            hooks["hooks"]["PreToolUse"][0]["hooks"].append(
                {"type": "command", "command": "python3 ${PLUGIN_ROOT}/hooks/second.py"}
            )
            self.write_json(root, PLUGIN_ROOT / "hooks/hooks.json", hooks)

            results = validator.validate_agent_equipment_config_codex_plugin(root)

        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:hooks:guard:content",
                False,
                "guard must contain only reviewed imports, constants, functions, and entrypoint",
                "plugins/agent-equipment-config/hooks/config_write_guard.py",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:launcher:content",
                False,
                "launcher must resolve the Armory checkout and exec the standalone MCP server",
                "plugins/agent-equipment-config/mcp/agent_equipment_config_launcher.py",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:hooks:PreToolUse:extra_hooks",
                False,
                "PreToolUse must contain exactly one reviewed command hook",
                "plugins/agent-equipment-config/hooks/hooks.json",
            ),
            results,
        )

    def test_validator_rejects_unreviewed_guard_imports_and_missing_skill_targets(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_plugin_fixture(root)
            guard_path = root / HOOK_PATH
            guard_path.write_text(
                "import subprocess\n"
                + guard_path.read_text(encoding="utf-8").replace(
                    "def normalized_tool_name(value: str) -> str:\n",
                    "def normalized_tool_name(value: str) -> str:\n    print('helper leak')\n",
                ),
                encoding="utf-8",
            )
            (root / "specs/agent-equipment-config/mcp-tools.md").unlink()

            results = validator.validate_agent_equipment_config_codex_plugin(root)

        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:hooks:guard:content",
                False,
                "guard must contain only reviewed imports, constants, functions, and entrypoint",
                "plugins/agent-equipment-config/hooks/config_write_guard.py",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:skill:route:specs/agent-equipment-config/mcp-tools.md:target",
                False,
                "missing",
                "specs/agent-equipment-config/mcp-tools.md",
            ),
            results,
        )

    def test_validator_rejects_guard_stderr_large_output_and_uses_safe_python_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_plugin_fixture(root)
            guard_path = root / HOOK_PATH
            guard_path.write_text(
                guard_path.read_text(encoding="utf-8").replace(
                    "def main() -> int:\n",
                    "def main() -> int:\n    print('leak', file=sys.stderr)\n",
                ),
                encoding="utf-8",
            )

            stderr_results = validator.validate_agent_equipment_config_codex_plugin(root)

            guard_path.write_text(
                guard_path.read_text(encoding="utf-8").replace(
                    "    print('leak', file=sys.stderr)\n",
                    "    print('x' * 9000)\n",
                ),
                encoding="utf-8",
            )
            large_output_results = validator.validate_agent_equipment_config_codex_plugin(root)

            guard_path.write_text(
                guard_path.read_text(encoding="utf-8").replace(
                    "    print('x' * 9000)\n",
                    "",
                ),
                encoding="utf-8",
            )
            (root / PLUGIN_ROOT / "hooks/json.py").write_text(
                "raise RuntimeError('stdlib shadow executed')\n",
                encoding="utf-8",
            )
            safe_path_results = validator.validate_agent_equipment_config_codex_plugin(root)

        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:hooks:guard:behavior:config_apply_denies_missing_authority",
                False,
                "guard must not write to stderr during validation",
                "plugins/agent-equipment-config/hooks/config_write_guard.py",
            ),
            stderr_results,
        )
        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:hooks:guard:behavior:config_apply_denies_missing_authority",
                False,
                "guard output exceeded validation limit",
                "plugins/agent-equipment-config/hooks/config_write_guard.py",
            ),
            large_output_results,
        )
        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:contract",
                True,
                "valid Codex plugin bundle",
                "plugins/agent-equipment-config",
            ),
            safe_path_results,
        )

    def test_validator_rejects_guard_loop_before_behavior_execution(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_plugin_fixture(root)
            guard_path = root / HOOK_PATH
            guard_text = guard_path.read_text(encoding="utf-8")
            guard_path.write_text(
                guard_text.replace(
                    "    decision = evaluate(payload)\n",
                    "    while True:\n        print(\"x\")\n    decision = evaluate(payload)\n",
                ),
                encoding="utf-8",
            )

            results = validator.validate_agent_equipment_config_codex_plugin(root)

        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:hooks:guard:content",
                False,
                "guard must contain only reviewed imports, constants, functions, and entrypoint",
                "plugins/agent-equipment-config/hooks/config_write_guard.py",
            ),
            results,
        )

    def test_validator_rejects_duplicate_launcher_bindings_and_extra_hook_keys(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_plugin_fixture(root)
            launcher_path = root / LAUNCHER_PATH
            launcher_path.write_text(
                launcher_path.read_text(encoding="utf-8")
                + textwrap.dedent(
                    """

                    def launch(argv=None):
                        return 0
                    """
                ),
                encoding="utf-8",
            )
            hooks = json.loads((root / PLUGIN_ROOT / "hooks/hooks.json").read_text(encoding="utf-8"))
            hooks["extra"] = True
            hooks["hooks"]["PreToolUse"][0]["enabled"] = True
            hooks["hooks"]["PreToolUse"][0]["hooks"][0]["async"] = True
            self.write_json(root, PLUGIN_ROOT / "hooks/hooks.json", hooks)

            results = validator.validate_agent_equipment_config_codex_plugin(root)

        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:launcher:content",
                False,
                "launcher must resolve the Armory checkout and exec the standalone MCP server",
                "plugins/agent-equipment-config/mcp/agent_equipment_config_launcher.py",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:hooks:unexpected",
                False,
                "unexpected hooks.json top-level keys: extra",
                "plugins/agent-equipment-config/hooks/hooks.json",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:hooks:PreToolUse:group_keys",
                False,
                "unexpected PreToolUse group keys: enabled",
                "plugins/agent-equipment-config/hooks/hooks.json",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:hooks:PreToolUse:hook_keys",
                False,
                "unexpected PreToolUse hook keys: async",
                "plugins/agent-equipment-config/hooks/hooks.json",
            ),
            results,
        )

    def test_validator_rejects_launcher_missing_main_entrypoint(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_plugin_fixture(root)
            launcher_path = root / LAUNCHER_PATH
            launcher_text = launcher_path.read_text(encoding="utf-8")
            launcher_path.write_text(
                launcher_text.split('\n\nif __name__ == "__main__":', 1)[0] + "\n",
                encoding="utf-8",
            )

            results = validator.validate_agent_equipment_config_codex_plugin(root)

        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:launcher:content",
                False,
                "launcher must resolve the Armory checkout and exec the standalone MCP server",
                "plugins/agent-equipment-config/mcp/agent_equipment_config_launcher.py",
            ),
            results,
        )

    def test_validator_rejects_wrong_repo_marker_and_unsafe_argv_launcher_contracts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_plugin_fixture(root)
            launcher_path = root / LAUNCHER_PATH
            launcher_text = launcher_path.read_text(encoding="utf-8")
            launcher_path.write_text(
                launcher_text.replace(
                    'REPO_MARKER = Path("inventory/equipment.toml")',
                    'REPO_MARKER = Path("README.md")',
                ),
                encoding="utf-8",
            )

            wrong_marker_results = validator.validate_agent_equipment_config_codex_plugin(root)

            launcher_path.write_text(
                launcher_text.replace(
                    "_argv = argv if argv is not None else sys.argv[1:]",
                    "_argv = compute_unreviewed_argv()",
                ),
                encoding="utf-8",
            )
            unsafe_argv_results = validator.validate_agent_equipment_config_codex_plugin(root)

            launcher_path.write_text(
                launcher_text.replace(
                    "    _argv = argv if argv is not None else sys.argv[1:]\n",
                    "",
                ),
                encoding="utf-8",
            )
            missing_argv_results = validator.validate_agent_equipment_config_codex_plugin(root)

        expected = CheckResult(
            "agent_equipment_config_codex_plugin:launcher:content",
            False,
            "launcher must resolve the Armory checkout and exec the standalone MCP server",
            "plugins/agent-equipment-config/mcp/agent_equipment_config_launcher.py",
        )
        self.assertIn(expected, wrong_marker_results)
        self.assertIn(expected, unsafe_argv_results)
        self.assertIn(expected, missing_argv_results)

    def test_validator_rejects_launcher_function_decorators_before_import(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_plugin_fixture(root)
            launcher_path = root / LAUNCHER_PATH
            launcher_text = launcher_path.read_text(encoding="utf-8")
            launcher_path.write_text(
                launcher_text.replace(
                    "def launch(argv: list[str] | None = None) -> int:\n",
                    "@not_defined_decorator\n"
                    "def launch(argv: list[str] | None = None) -> int:\n",
                ),
                encoding="utf-8",
            )

            results = validator.validate_agent_equipment_config_codex_plugin(root)

        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:launcher:content",
                False,
                "launcher must resolve the Armory checkout and exec the standalone MCP server",
                "plugins/agent-equipment-config/mcp/agent_equipment_config_launcher.py",
            ),
            results,
        )
        self.assertFalse(
            any(
                result.name == "agent_equipment_config_codex_plugin:launcher:content"
                and "launcher discovery probe" in result.detail
                for result in results
            )
        )

    def test_validator_rejects_launcher_that_drops_forwarded_args(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_plugin_fixture(root)
            launcher_path = root / LAUNCHER_PATH
            launcher_text = launcher_path.read_text(encoding="utf-8")
            launcher_path.write_text(
                launcher_text.replace(
                    "[python_executable, str(server), *_argv]",
                    "[python_executable, str(server)]",
                ),
                encoding="utf-8",
            )

            results = validator.validate_agent_equipment_config_codex_plugin(root)

        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:launcher:content",
                False,
                "launcher must resolve the Armory checkout and exec the standalone MCP server",
                "plugins/agent-equipment-config/mcp/agent_equipment_config_launcher.py",
            ),
            results,
        )

    def test_validator_rejects_duplicate_marketplace_records_and_extra_mcp_servers(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_plugin_fixture(root)
            marketplace = json.loads((root / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
            marketplace["plugins"].append(
                {
                    "name": "agent-equipment-config",
                    "source": {"source": "local", "path": "./plugins/other"},
                    "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                    "category": "Productivity",
                }
            )
            self.write_json(root, ".agents/plugins/marketplace.json", marketplace)
            mcp_config = json.loads((root / PLUGIN_ROOT / ".mcp.json").read_text(encoding="utf-8"))
            mcp_config["unreviewed"] = {
                "command": "python3.14",
                "args": ["./unreviewed.py"],
            }
            self.write_json(root, PLUGIN_ROOT / ".mcp.json", mcp_config)

            results = validator.validate_agent_equipment_config_codex_plugin(root)

        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:marketplace:agent-equipment-config",
                False,
                "marketplace must contain exactly one agent-equipment-config plugin",
                ".agents/plugins/marketplace.json",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:mcp:server_map:unexpected",
                False,
                "unexpected MCP server entries: unreviewed",
                "plugins/agent-equipment-config/.mcp.json",
            ),
            results,
        )

    def test_validator_rejects_inventory_without_required_plugin_component_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_plugin_fixture(root)
            inventory_path = root / "inventory/equipment.toml"
            inventory_path.write_text(
                inventory_path.read_text(encoding="utf-8").replace(
                    '  "plugins/agent-equipment-config/README.md",\n',
                    "",
                ),
                encoding="utf-8",
            )

            results = validator.validate_agent_equipment_config_codex_plugin(root)

        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:inventory:codex_plugin",
                False,
                "Codex plugin must be a required plugin component and list stocked paths; missing paths: "
                "plugins/agent-equipment-config/README.md",
                "inventory/equipment.toml",
            ),
            results,
        )

    def test_validator_rejects_inventory_without_required_routing_skill_component(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_plugin_fixture(root)
            inventory_path = root / "inventory/equipment.toml"
            inventory_path.write_text(
                inventory_path.read_text(encoding="utf-8").replace(
                    'name = "Config routing skill"\nkind = "skill"\nstatus = "required"\n',
                    'name = "Config routing skill"\nkind = "skill"\nstatus = "planned"\n',
                ),
                encoding="utf-8",
            )

            results = validator.validate_agent_equipment_config_codex_plugin(root)

        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:inventory:config_routing_skill",
                False,
                "Config routing skill must be a required skill component and list stocked paths",
                "inventory/equipment.toml",
            ),
            results,
        )

    def test_validator_rejects_inventory_with_wrong_required_component_kind(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_plugin_fixture(root)
            inventory_path = root / "inventory/equipment.toml"
            inventory_path.write_text(
                inventory_path.read_text(encoding="utf-8").replace(
                    'name = "Codex plugin"\nkind = "plugin"\nstatus = "required"\n',
                    'name = "Codex plugin"\nkind = "docs"\nstatus = "required"\n',
                ),
                encoding="utf-8",
            )

            results = validator.validate_agent_equipment_config_codex_plugin(root)

        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:inventory:codex_plugin",
                False,
                "Codex plugin must be a required plugin component and list stocked paths",
                "inventory/equipment.toml",
            ),
            results,
        )

    def test_validator_rejects_wrapped_mcp_server_maps_for_this_plugin(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_plugin_fixture(root)
            direct_map = json.loads((root / PLUGIN_ROOT / ".mcp.json").read_text(encoding="utf-8"))
            self.write_json(root, PLUGIN_ROOT / ".mcp.json", {"mcpServers": direct_map})

            camel_results = validator.validate_agent_equipment_config_codex_plugin(root)

            self.write_json(root, PLUGIN_ROOT / ".mcp.json", {"mcp_servers": direct_map})
            snake_results = validator.validate_agent_equipment_config_codex_plugin(root)

        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:mcp:wrapper",
                False,
                ".mcp.json must use a direct MCP server map, not wrapper keys: mcpServers",
                "plugins/agent-equipment-config/.mcp.json",
            ),
            camel_results,
        )
        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:mcp:wrapper",
                False,
                ".mcp.json must use a direct MCP server map, not wrapper keys: mcp_servers",
                "plugins/agent-equipment-config/.mcp.json",
            ),
            snake_results,
        )

    def test_validator_rejects_launcher_that_execs_unrelated_python(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_plugin_fixture(root)
            self.write_text(
                root,
                LAUNCHER_PATH,
                """
                import os
                import sys
                from pathlib import Path
                REPO_SERVER = Path("tools/agent_equipment_config_mcp_server.py")
                MARKETPLACE_MARKER = Path(".agents/plugins/marketplace.json")
                def find_armory_root():
                    return Path.cwd()
                def launch():
                    root = find_armory_root()
                    if root is None:
                        return 2
                    server = root / REPO_SERVER
                    os.chdir(root)
                    python_executable = str(Path(sys.executable).resolve())
                    os.execve(python_executable, [python_executable, "-c", "print(1)"], server_environment())
                """,
            )

            results = validator.validate_agent_equipment_config_codex_plugin(root)

        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:launcher:content",
                False,
                "launcher must resolve the Armory checkout and exec the standalone MCP server",
                "plugins/agent-equipment-config/mcp/agent_equipment_config_launcher.py",
            ),
            results,
        )

    def test_validator_rejects_launcher_with_nonterminal_failure_returns(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_plugin_fixture(root)
            launcher_path = root / LAUNCHER_PATH
            launcher_text = launcher_path.read_text(encoding="utf-8")
            launcher_path.write_text(
                launcher_text.replace(
                    "        return 2\n\n    server = root / REPO_SERVER\n",
                    "        return 2\n        return 0\n\n    server = root / REPO_SERVER\n",
                    1,
                ),
                encoding="utf-8",
            )

            root_guard_results = validator.validate_agent_equipment_config_codex_plugin(root)

            launcher_path.write_text(
                launcher_text.replace(
                    "        return 127\n",
                    "        return 127\n        return 0\n",
                ),
                encoding="utf-8",
            )

            exec_guard_results = validator.validate_agent_equipment_config_codex_plugin(root)

        expected = CheckResult(
            "agent_equipment_config_codex_plugin:launcher:content",
            False,
            "launcher must resolve the Armory checkout and exec the standalone MCP server",
            "plugins/agent-equipment-config/mcp/agent_equipment_config_launcher.py",
        )
        self.assertIn(expected, root_guard_results)
        self.assertIn(expected, exec_guard_results)

    def test_validator_rejects_launcher_with_broad_server_environment_passthrough(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_plugin_fixture(root)
            launcher_path = root / LAUNCHER_PATH
            launcher_text = launcher_path.read_text(encoding="utf-8")
            launcher_path.write_text(
                launcher_text.replace("            server_environment(),", "            os.environ.copy(),"),
                encoding="utf-8",
            )

            results = validator.validate_agent_equipment_config_codex_plugin(root)

        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:launcher:content",
                False,
                "launcher must resolve the Armory checkout and exec the standalone MCP server",
                "plugins/agent-equipment-config/mcp/agent_equipment_config_launcher.py",
            ),
            results,
        )

    def test_validator_rejects_launcher_with_control_flow_in_exec_failure_handler(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_plugin_fixture(root)
            launcher_path = root / LAUNCHER_PATH
            launcher_text = launcher_path.read_text(encoding="utf-8")
            launcher_path.write_text(
                launcher_text.replace(
                    '        print(\n'
                    '            f"Agent Equipment Config MCP launcher could not execute {python_executable}: {error}",\n'
                    "            file=sys.stderr,\n"
                    "        )\n"
                    "        return 127\n",
                    "        while True:\n"
                    "            pass\n"
                    "        return 127\n",
                ),
                encoding="utf-8",
            )

            results = validator.validate_agent_equipment_config_codex_plugin(root)

        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:launcher:content",
                False,
                "launcher must resolve the Armory checkout and exec the standalone MCP server",
                "plugins/agent-equipment-config/mcp/agent_equipment_config_launcher.py",
            ),
            results,
        )

    def test_validator_rejects_launcher_exec_failure_handler_that_prints_to_stdout(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_plugin_fixture(root)
            launcher_path = root / LAUNCHER_PATH
            launcher_text = launcher_path.read_text(encoding="utf-8")
            launcher_path.write_text(
                launcher_text.replace("            file=sys.stderr,\n", ""),
                encoding="utf-8",
            )

            results = validator.validate_agent_equipment_config_codex_plugin(root)

        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:launcher:content",
                False,
                "launcher must resolve the Armory checkout and exec the standalone MCP server",
                "plugins/agent-equipment-config/mcp/agent_equipment_config_launcher.py",
            ),
            results,
        )

    def test_validator_rejects_launcher_exec_failure_handler_that_prints_environment(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_plugin_fixture(root)
            launcher_path = root / LAUNCHER_PATH
            launcher_text = launcher_path.read_text(encoding="utf-8")
            launcher_path.write_text(
                launcher_text.replace(
                    'f"Agent Equipment Config MCP launcher could not execute {python_executable}: {error}"',
                    "os.environ",
                ),
                encoding="utf-8",
            )

            results = validator.validate_agent_equipment_config_codex_plugin(root)

        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:launcher:content",
                False,
                "launcher must resolve the Armory checkout and exec the standalone MCP server",
                "plugins/agent-equipment-config/mcp/agent_equipment_config_launcher.py",
            ),
            results,
        )

    def test_validator_rejects_launcher_server_environment_that_leaks_ambient_env(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_plugin_fixture(root)
            launcher_path = root / LAUNCHER_PATH
            launcher_text = launcher_path.read_text(encoding="utf-8")
            launcher_path.write_text(
                launcher_text.replace(
                    "def server_environment() -> dict[str, str]:\n"
                    "    return {\n"
                    "        name: value\n"
                    "        for name in SERVER_ENV_VAR_NAMES\n"
                    "        if (value := os.environ.get(name)) is not None\n"
                    "    }\n",
                    "def server_environment() -> dict[str, str]:\n"
                    "    _seen = [os.environ.get(name) for name in SERVER_ENV_VAR_NAMES]\n"
                    "    return os.environ\n",
                ),
                encoding="utf-8",
            )

            results = validator.validate_agent_equipment_config_codex_plugin(root)

        self.assertTrue(
            any(
                result.name == "agent_equipment_config_codex_plugin:launcher:content"
                and not result.ok
                and result.path == "plugins/agent-equipment-config/mcp/agent_equipment_config_launcher.py"
                and result.detail.startswith("launcher discovery probe resolved unexpected roots:")
                and "SHOULD_NOT_REACH_MCP" in result.detail
                for result in results
            ),
            results,
        )

    def test_validator_rejects_launcher_server_environment_that_includes_unset_allowlist_value(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_plugin_fixture(root)
            launcher_path = root / LAUNCHER_PATH
            launcher_text = launcher_path.read_text(encoding="utf-8")
            launcher_path.write_text(
                launcher_text.replace(
                    "def server_environment() -> dict[str, str]:\n"
                    "    return {\n"
                    "        name: value\n"
                    "        for name in SERVER_ENV_VAR_NAMES\n"
                    "        if (value := os.environ.get(name)) is not None\n"
                    "    }\n",
                    "def server_environment() -> dict[str, str]:\n"
                    "    _seen = [os.environ.get(name) for name in SERVER_ENV_VAR_NAMES]\n"
                    "    return {name: os.environ.get(name) for name in SERVER_ENV_VAR_NAMES}\n",
                ),
                encoding="utf-8",
            )

            results = validator.validate_agent_equipment_config_codex_plugin(root)

        self.assertTrue(
            any(
                result.name == "agent_equipment_config_codex_plugin:launcher:content"
                and not result.ok
                and result.path == "plugins/agent-equipment-config/mcp/agent_equipment_config_launcher.py"
                and result.detail.startswith("launcher discovery probe resolved unexpected roots:")
                and "'server_environment_missing': {'AGENT_ARMORY_ROOT': None}" in result.detail
                for result in results
            ),
            results,
        )

    def test_validator_rejects_launcher_entrypoint_before_launch_function(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_plugin_fixture(root)
            launcher_path = root / LAUNCHER_PATH
            launcher_text = launcher_path.read_text(encoding="utf-8")
            entrypoint = '\n\nif __name__ == "__main__":\n    raise SystemExit(launch())\n'
            launcher_path.write_text(
                launcher_text.replace(entrypoint, "").replace(
                    "def launch(argv: list[str] | None = None) -> int:\n",
                    f"{entrypoint}\n\ndef launch(argv: list[str] | None = None) -> int:\n",
                ),
                encoding="utf-8",
            )

            results = validator.validate_agent_equipment_config_codex_plugin(root)

        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:launcher:content",
                False,
                "launcher must resolve the Armory checkout and exec the standalone MCP server",
                "plugins/agent-equipment-config/mcp/agent_equipment_config_launcher.py",
            ),
            results,
        )

    def test_validator_rejects_launcher_relative_import_and_helper_side_effects(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_plugin_fixture(root)
            launcher_path = root / LAUNCHER_PATH
            launcher_text = launcher_path.read_text(encoding="utf-8")
            launcher_path.write_text(
                launcher_text.replace("from pathlib import Path", "from .pathlib import Path"),
                encoding="utf-8",
            )

            relative_import_results = validator.validate_agent_equipment_config_codex_plugin(root)

            launcher_path.write_text(
                launcher_text.replace(
                    "def candidate_is_armory_root(candidate: Path) -> bool:\n",
                    "def candidate_is_armory_root(candidate: Path) -> bool:\n"
                    "    python_executable = str(Path(sys.executable).resolve())\n"
                    "    os.execve(python_executable, [python_executable, str(candidate / REPO_SERVER)], server_environment())\n",
                ),
                encoding="utf-8",
            )
            helper_side_effect_results = validator.validate_agent_equipment_config_codex_plugin(root)

        expected = CheckResult(
            "agent_equipment_config_codex_plugin:launcher:content",
            False,
            "launcher must resolve the Armory checkout and exec the standalone MCP server",
            "plugins/agent-equipment-config/mcp/agent_equipment_config_launcher.py",
        )
        self.assertIn(expected, relative_import_results)
        self.assertIn(expected, helper_side_effect_results)

    def test_validator_rejects_launcher_with_dead_exec_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_plugin_fixture(root)
            self.write_text(
                root,
                LAUNCHER_PATH,
                """
                import os
                import sys
                from pathlib import Path
                REPO_SERVER = Path("tools/agent_equipment_config_mcp_server.py")
                MARKETPLACE_MARKER = Path(".agents/plugins/marketplace.json")
                def find_armory_root():
                    return Path.cwd()
                def launch():
                    return 0
                    root = find_armory_root()
                    if root is None:
                        return 2
                    server = root / REPO_SERVER
                    os.chdir(root)
                    python_executable = str(Path(sys.executable).resolve())
                    os.execve(python_executable, [python_executable, str(server)], server_environment())
                """,
            )

            results = validator.validate_agent_equipment_config_codex_plugin(root)

        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:launcher:content",
                False,
                "launcher must resolve the Armory checkout and exec the standalone MCP server",
                "plugins/agent-equipment-config/mcp/agent_equipment_config_launcher.py",
            ),
            results,
        )

    def test_validator_rejects_launcher_with_inert_root_discovery(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_plugin_fixture(root)
            self.write_text(
                root,
                LAUNCHER_PATH,
                """
                import os
                import sys
                from pathlib import Path
                REPO_SERVER = Path("tools/agent_equipment_config_mcp_server.py")
                REPO_MARKER = Path("inventory/equipment.toml")
                MARKETPLACE_MARKER = Path(".agents/plugins/marketplace.json")
                def find_armory_root(*, env_root=None, start_dir=None):
                    return Path.cwd()
                def launch():
                    root = find_armory_root(
                        env_root=os.environ.get("AGENT_ARMORY_ROOT"),
                        start_dir=os.environ.get("PWD") or os.getcwd(),
                    )
                    if root is None:
                        return 2
                    server = root / REPO_SERVER
                    if not server.is_file():
                        return 2
                    os.chdir(root)
                    python_executable = str(Path(sys.executable).resolve())
                    try:
                        os.execve(python_executable, [python_executable, str(server)], server_environment())
                    except OSError:
                        return 127
                """,
            )

            results = validator.validate_agent_equipment_config_codex_plugin(root)

        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:launcher:content",
                False,
                "launcher must resolve the Armory checkout and exec the standalone MCP server",
                "plugins/agent-equipment-config/mcp/agent_equipment_config_launcher.py",
            ),
            results,
        )

    def test_validator_rejects_launcher_with_unreviewed_reachable_behavior(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_plugin_fixture(root)
            self.write_text(
                root,
                LAUNCHER_PATH,
                """
                import os
                import sys
                from pathlib import Path
                REPO_SERVER = Path("tools/agent_equipment_config_mcp_server.py")
                MARKETPLACE_MARKER = Path(".agents/plugins/marketplace.json")
                def find_armory_root():
                    return Path.cwd()
                def launch():
                    root = find_armory_root()
                    if root is None:
                        return 2
                    server = root / REPO_SERVER
                    if not server.is_file():
                        return 2
                    os.environ.clear()
                    os.chdir(root)
                    python_executable = str(Path(sys.executable).resolve())
                    try:
                        os.execve(python_executable, [python_executable, str(server)], server_environment())
                    except OSError:
                        return 127
                """,
            )

            results = validator.validate_agent_equipment_config_codex_plugin(root)

        self.assertIn(
            CheckResult(
                "agent_equipment_config_codex_plugin:launcher:content",
                False,
                "launcher must resolve the Armory checkout and exec the standalone MCP server",
                "plugins/agent-equipment-config/mcp/agent_equipment_config_launcher.py",
            ),
            results,
        )

    def test_live_stock_record_requires_plugin_skill_launcher_and_hook_paths(self):
        repo_root = Path(__file__).resolve().parents[1]
        inventory = load_toml(repo_root / "inventory/equipment.toml")
        config = next(
            (record for record in inventory["equipment"] if record["id"] == "agent-equipment-config"),
            None,
        )
        self.assertIsNotNone(config)
        assert config is not None
        components = {component["name"]: component for component in config["components"]}

        self.assertEqual("required", components["Codex plugin"]["status"])
        self.assertEqual("required", components["Config routing skill"]["status"])
        self.assertEqual("planned", components["Codex gear-up validation"]["status"])

        required_paths = set(components["Codex plugin"]["paths"]) | set(components["Config routing skill"]["paths"])
        for relative_path in [
            ".agents/plugins/marketplace.json",
            "plugins/agent-equipment-config/.codex-plugin/plugin.json",
            "plugins/agent-equipment-config/.mcp.json",
            "plugins/agent-equipment-config/mcp/agent_equipment_config_launcher.py",
            "plugins/agent-equipment-config/hooks/hooks.json",
            "plugins/agent-equipment-config/hooks/config_write_guard.py",
            "plugins/agent-equipment-config/skills/agent-equipment-config/SKILL.md",
            "plugins/agent-equipment-config/README.md",
        ]:
            self.assertIn(relative_path, required_paths)
            self.assertTrue(
                (repo_root / relative_path).exists(),
                f"required plugin path does not exist: {relative_path}",
            )


class AgentEquipmentConfigLauncherTests(unittest.TestCase):
    def test_launcher_server_environment_allows_only_agent_armory_root(self):
        launcher = load_module(
            Path(__file__).resolve().parents[1] / LAUNCHER_PATH,
            "config_launcher_server_environment",
        )

        with mock.patch.dict(
            launcher.os.environ,
            {
                "AGENT_ARMORY_ROOT": "/tmp/armory",
                "PATH": "/tmp/controlled",
                "SECRET_TOKEN": "secret",
            },
            clear=True,
        ):
            env = launcher.server_environment()

        self.assertEqual({"AGENT_ARMORY_ROOT": "/tmp/armory"}, env)

    def test_launcher_prefers_valid_env_root_and_finds_server(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_launcher_repo_markers(root)
            outside = Path(tmpdir) / "outside"
            outside.mkdir()
            launcher = load_module(Path(__file__).resolve().parents[1] / LAUNCHER_PATH, "config_launcher")

            found = launcher.find_armory_root(env_root=str(root), start_dir=outside)

        self.assertEqual(root.resolve(), found)

    def test_launcher_uses_cwd_ancestor_fallback_and_ignores_spoofed_pwd(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_launcher_repo_markers(root)
            nested = root / "work/subdir"
            nested.mkdir(parents=True)
            spoofed = Path(tmpdir) / "spoofed"
            spoofed.mkdir()
            launcher = load_module(
                Path(__file__).resolve().parents[1] / LAUNCHER_PATH,
                "config_launcher_cwd_fallback",
            )
            exec_call = {}

            def fake_execve(command, args, env) -> NoReturn:
                exec_call["command"] = command
                exec_call["args"] = args
                exec_call["env"] = env
                raise RuntimeError("stop before exec")

            found = launcher.find_armory_root(env_root=None, start_dir=nested)
            with mock.patch.dict(launcher.os.environ, {"PWD": str(spoofed)}, clear=True):
                with mock.patch.object(launcher.Path, "cwd", return_value=nested):
                    with mock.patch.object(launcher.os, "chdir") as chdir:
                        with mock.patch.object(launcher.os, "execve", side_effect=fake_execve):
                            with self.assertRaisesRegex(RuntimeError, "stop before exec"):
                                launcher.launch(["--stdio"])

        self.assertEqual(root.resolve(), found)
        chdir.assert_called_once_with(root.resolve())
        python_executable = str(Path(launcher.sys.executable).resolve())
        self.assertEqual(python_executable, exec_call["command"])
        self.assertEqual(
            [python_executable, str(root.resolve() / "tools/agent_equipment_config_mcp_server.py"), "--stdio"],
            exec_call["args"],
        )
        self.assertEqual({}, exec_call["env"])

    def test_launcher_rejects_lookalike_repo_without_marketplace_marker(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            server = root / "tools/agent_equipment_config_mcp_server.py"
            server.parent.mkdir(parents=True, exist_ok=True)
            server.write_text("# server\n", encoding="utf-8")
            (root / "inventory").mkdir()
            (root / "inventory/equipment.toml").write_text("", encoding="utf-8")
            nested = root / "work/subdir"
            nested.mkdir(parents=True)
            launcher = load_module(
                Path(__file__).resolve().parents[1] / LAUNCHER_PATH,
                "config_launcher_lookalike",
            )

            found = launcher.find_armory_root(env_root=str(root), start_dir=nested)

        self.assertIsNone(found)

    def test_launcher_uses_configured_env_root_and_execs_from_armory_root(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_launcher_repo_markers(root)
            nested = root / "work/subdir"
            nested.mkdir(parents=True)
            launcher = load_module(
                Path(__file__).resolve().parents[1] / LAUNCHER_PATH,
                "config_launcher_launch",
            )
            exec_call = {}

            def fake_execve(command, args, env) -> NoReturn:
                exec_call["command"] = command
                exec_call["args"] = args
                exec_call["env"] = env
                raise RuntimeError("stop before exec")

            with mock.patch.dict(
                launcher.os.environ,
                {
                    "AGENT_ARMORY_ROOT": str(root),
                    "PATH": str(Path(tmpdir) / "spoofed-bin"),
                    "SECRET_TOKEN": "secret",
                },
                clear=True,
            ):
                with mock.patch.object(launcher.os, "chdir") as chdir:
                    with mock.patch.object(launcher.os, "execve", side_effect=fake_execve):
                        with self.assertRaisesRegex(RuntimeError, "stop before exec"):
                            launcher.launch(["--stdio"])

        chdir.assert_called_once_with(root.resolve())
        python_executable = str(Path(launcher.sys.executable).resolve())
        self.assertEqual(python_executable, exec_call["command"])
        self.assertEqual(
            [python_executable, str(root.resolve() / "tools/agent_equipment_config_mcp_server.py"), "--stdio"],
            exec_call["args"],
        )
        self.assertEqual({"AGENT_ARMORY_ROOT": str(root)}, exec_call["env"])

    def test_launcher_rechecks_server_before_exec(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_launcher_repo_markers(root)
            server = root / "tools/agent_equipment_config_mcp_server.py"
            launcher = load_module(
                Path(__file__).resolve().parents[1] / LAUNCHER_PATH,
                "config_launcher_recheck",
            )
            stderr = io.StringIO()

            def fake_find_armory_root(*, env_root, start_dir=None):
                server.unlink()
                return root.resolve()

            with mock.patch.object(launcher, "find_armory_root", side_effect=fake_find_armory_root):
                with mock.patch.object(launcher.os, "chdir") as chdir:
                    with mock.patch.object(launcher.os, "execve") as execve:
                        with mock.patch.object(launcher.sys, "stderr", stderr):
                            exit_code = launcher.launch(["--stdio"])

        self.assertEqual(2, exit_code)
        chdir.assert_not_called()
        execve.assert_not_called()
        self.assertIn("could not find", stderr.getvalue())

    def test_launcher_reports_exec_failure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_launcher_repo_markers(root)
            nested = root / "work/subdir"
            nested.mkdir(parents=True)
            launcher = load_module(
                Path(__file__).resolve().parents[1] / LAUNCHER_PATH,
                "config_launcher_exec_failure",
            )
            stderr = io.StringIO()

            with mock.patch.dict(launcher.os.environ, {"AGENT_ARMORY_ROOT": str(root)}, clear=True):
                with mock.patch.object(launcher.os, "chdir"):
                    with mock.patch.object(launcher.os, "execve", side_effect=FileNotFoundError("python")):
                        with mock.patch.object(launcher.sys, "stderr", stderr):
                            exit_code = launcher.launch(["--stdio"])

        self.assertEqual(127, exit_code)
        self.assertIn("could not execute", stderr.getvalue())
        self.assertIn(str(Path(launcher.sys.executable).resolve()), stderr.getvalue())


class AgentEquipmentConfigGuardHookTests(unittest.TestCase):
    def load_hook(self):
        return load_module(Path(__file__).resolve().parents[1] / HOOK_PATH, "config_write_guard")

    def test_hook_denies_config_apply_without_operator_authority(self):
        hook = self.load_hook()

        decision = hook.evaluate(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "mcp__agent_equipment_config__config.apply",
                "tool_input": {"plan": {"actions": []}},
            }
        )

        self.assertEqual(
            decision["hookSpecificOutput"]["permissionDecision"],
            "deny",
        )
        self.assertIn(
            'apply_authority = "operator"',
            decision["hookSpecificOutput"]["permissionDecisionReason"],
        )

    def test_hook_denies_codex_sanitized_write_tools_without_operator_authority(self):
        hook = self.load_hook()

        for tool_name in [
            "mcp__agent-equipment-config__config.apply",
            "mcp__agent-equipment-config__migrate.config_apply",
            "mcp__agent_equipment_config__config_apply",
            "mcp__agent_equipment_config__migrate_config_apply",
        ]:
            with self.subTest(tool_name=tool_name):
                decision = hook.evaluate(
                    {
                        "hook_event_name": "PreToolUse",
                        "tool_name": tool_name,
                        "tool_input": {},
                    }
                )

                self.assertEqual(
                    "deny",
                    decision["hookSpecificOutput"]["permissionDecision"],
                )

    def test_hook_denies_non_operator_authority_values(self):
        hook = self.load_hook()

        for value in ["", "user", None]:
            with self.subTest(value=value):
                decision = hook.evaluate(
                    {
                        "hook_event_name": "PreToolUse",
                        "tool_name": "mcp__agent_equipment_config__config_apply",
                        "tool_input": {"apply_authority": value},
                    }
                )

                self.assertEqual(
                    "deny",
                    decision["hookSpecificOutput"]["permissionDecision"],
                )

    def test_hook_allows_config_apply_with_operator_authority_and_ignores_other_tools(self):
        hook = self.load_hook()

        allowed = hook.evaluate(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "mcp__agent-equipment-config__config.apply",
                "tool_input": {"apply_authority": "operator"},
            }
        )
        ignored = hook.evaluate(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "mcp__other_server__config.apply",
                "tool_input": {},
            }
        )

        self.assertIsNone(allowed)
        self.assertIsNone(ignored)

    def test_hook_ignores_lookalike_config_server_name(self):
        hook = self.load_hook()

        decision = hook.evaluate(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "mcp__other_agent_equipment_config__config.apply",
                "tool_input": {},
            }
        )

        self.assertIsNone(decision)

    def test_hook_denies_malformed_stdin(self):
        hook = self.load_hook()
        stdout = io.StringIO()

        with mock.patch.object(hook.sys, "stdin", io.StringIO("{")):
            with mock.patch.object(hook.sys, "stdout", stdout):
                self.assertEqual(0, hook.main())

        decision = json.loads(stdout.getvalue())
        self.assertEqual("deny", decision["hookSpecificOutput"]["permissionDecision"])
        self.assertIn("malformed JSON", decision["hookSpecificOutput"]["permissionDecisionReason"])


class AgentEquipmentConfigRoutingSkillTests(unittest.TestCase):
    def test_routing_skill_is_thin_and_links_to_current_contracts(self):
        repo_root = Path(__file__).resolve().parents[1]
        text = (repo_root / ROUTING_SKILL_PATH).read_text(encoding="utf-8")

        self.assertIn("name: agent-equipment-config", text)
        self.assertIn("docs/equipment/agent-equipment-config.md", text)
        self.assertIn("docs/equipment/agent-equipment-config-integration.md", text)
        self.assertIn("specs/agent-equipment-config/mcp-tools.md", text)
        self.assertLess(len(text.splitlines()), 90)


if __name__ == "__main__":
    unittest.main()
