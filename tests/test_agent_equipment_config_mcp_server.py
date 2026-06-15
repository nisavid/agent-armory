import json
import select
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).parents[1]
SERVER = ROOT / "tools" / "agent_equipment_config_mcp_server.py"
sys.path.insert(0, str(ROOT))

from tools import agent_equipment_config_mcp_server


class AgentEquipmentConfigMcpServerTests(unittest.TestCase):
    def run_server_raw(self, payload: str) -> tuple[list[dict[str, object]], str, int]:
        process = subprocess.Popen(
            [sys.executable, str(SERVER)],
            cwd=ROOT,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = process.communicate(payload, timeout=10)
        responses = [json.loads(line) for line in stdout.splitlines() if line]
        return responses, stderr, process.returncode

    def run_server(self, messages: list[dict[str, object]]) -> tuple[list[dict[str, object]], str, int]:
        payload = "".join(json.dumps(message, separators=(",", ":")) + "\n" for message in messages)
        return self.run_server_raw(payload)

    def test_server_initializes_and_lists_config_tools(self):
        responses, stderr, returncode = self.run_server(
            [
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2025-11-25",
                        "capabilities": {},
                        "clientInfo": {"name": "agent-armory-test", "version": "0"},
                    },
                },
                {"jsonrpc": "2.0", "method": "notifications/initialized"},
                {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
            ]
        )

        self.assertEqual(returncode, 0, stderr)
        self.assertEqual(len(responses), 2, stderr)
        initialize = responses[0]
        self.assertEqual(initialize["id"], 1)
        self.assertEqual(initialize["result"]["protocolVersion"], "2025-11-25")
        self.assertEqual(initialize["result"]["capabilities"], {"tools": {"listChanged": False}})
        self.assertEqual(initialize["result"]["serverInfo"]["name"], "agent-equipment-config")

        tools = responses[1]
        self.assertEqual(tools["id"], 2)
        self.assertEqual(
            sorted(tool["name"] for tool in tools["result"]["tools"]),
            [
                "config.apply",
                "config.create_layer",
                "config.diff",
                "config.patch",
                "config.propose",
                "config.resolve",
                "config.validate",
                "migrate.config_apply",
                "migrate.config_preview",
                "onboard.config",
            ],
        )
        self.assertEqual(stderr, "")

    @unittest.skipUnless(sys.platform != "win32", "select is not supported on Windows pipes")
    def test_server_writes_responses_before_stdin_eof(self):
        process = subprocess.Popen(
            [sys.executable, str(SERVER)],
            cwd=ROOT,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            assert process.stdin is not None
            assert process.stdout is not None
            process.stdin.write(
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "tools/list",
                        "params": {},
                    },
                    separators=(",", ":"),
                )
                + "\n"
            )
            process.stdin.flush()

            ready, _, _ = select.select([process.stdout], [], [], 1)
            self.assertTrue(ready, "server did not write a response while stdin remained open")
            response = json.loads(process.stdout.readline())
            self.assertEqual(response["id"], 1)
            self.assertIn("tools", response["result"])
        finally:
            process.terminate()
            _, stderr = process.communicate(timeout=10)
        self.assertEqual(stderr, "")

    def test_server_lists_local_write_classification(self):
        responses, stderr, returncode = self.run_server(
            [{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}]
        )

        self.assertEqual(returncode, 0, stderr)
        tools = {tool["name"]: tool for tool in responses[0]["result"]["tools"]}
        self.assertFalse(tools["config.apply"]["annotations"]["readOnlyHint"])
        self.assertTrue(tools["config.apply"]["annotations"]["destructiveHint"])
        self.assertEqual(
            tools["config.apply"]["x-agent-armory"]["approval_requirements"],
            ["explicit operator or host approval before mutation-capable call"],
        )
        self.assertEqual(tools["config.apply"]["x-agent-armory"]["auth_source"], "per-call apply_authority")
        self.assertFalse(tools["migrate.config_apply"]["annotations"]["readOnlyHint"])
        self.assertTrue(tools["migrate.config_apply"]["annotations"]["destructiveHint"])
        self.assertEqual(
            tools["migrate.config_apply"]["x-agent-armory"]["approval_requirements"],
            ["per-call apply_authority"],
        )
        self.assertEqual(stderr, "")

    def test_server_calls_read_only_config_tool(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = root / "repo.toml"
            layer.write_text(
                textwrap.dedent(
                    """
                    [agent_equipment_config.layer]
                    name = "repository policy"
                    category = "committed durable config"

                    [issue_tracker_ops]
                    mode = "dry-run"
                    external_disclosure = "blocked"
                    """
                ).lstrip(),
                encoding="utf-8",
            )

            responses, stderr, returncode = self.run_server(
                [
                    {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "tools/call",
                        "params": {
                            "name": "config.resolve",
                            "arguments": {
                                "layer_paths": [str(layer)],
                                "fragments": ["issue_tracker_ops"],
                                "requested_behavior": "advisory",
                            },
                        },
                    }
                ]
            )

        self.assertEqual(returncode, 0, stderr)
        self.assertEqual(len(responses), 1, stderr)
        response = responses[0]
        self.assertEqual(response["id"], 1)
        result = response["result"]
        self.assertNotIn("isError", result)
        self.assertEqual(result["structuredContent"]["tool"], "config.resolve")
        self.assertEqual(result["structuredContent"]["read_write_classification"], "read-only")
        self.assertEqual(result["structuredContent"]["result"]["safety_status"], "usable")
        self.assertEqual(stderr, "")

    def test_server_returns_result_level_tool_errors(self):
        responses, stderr, returncode = self.run_server(
            [
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {"name": "config.resolve", "arguments": {"fragments": [], "unexpected": True}},
                }
            ]
        )

        self.assertEqual(returncode, 0, stderr)
        response = responses[0]
        self.assertNotIn("error", response)
        result = response["result"]
        self.assertTrue(result["isError"])
        self.assertEqual(result["structuredContent"]["tool"], "config.resolve")
        self.assertEqual(result["structuredContent"]["read_write_classification"], "read-only")
        self.assertIn("unknown argument(s) for config.resolve", result["content"][0]["text"])
        self.assertEqual(stderr, "")

    def test_server_rejects_unsupported_protocol_version(self):
        responses, stderr, returncode = self.run_server(
            [
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {"protocolVersion": "1999-01-01", "capabilities": {}},
                }
            ]
        )

        self.assertEqual(returncode, 0, stderr)
        error = responses[0]["error"]
        self.assertEqual(error["code"], -32602)
        self.assertEqual(error["data"]["requestedProtocolVersion"], "1999-01-01")
        self.assertEqual(error["data"]["supportedProtocolVersions"], ["2025-11-25", "2025-06-18"])
        self.assertEqual(stderr, "")

    def test_server_reports_parse_errors_without_stderr_logs(self):
        responses, stderr, returncode = self.run_server_raw("{not json}\n")

        self.assertEqual(returncode, 0, stderr)
        self.assertEqual(responses[0]["id"], None)
        self.assertEqual(responses[0]["error"]["code"], -32700)
        self.assertEqual(stderr, "")

    def test_server_reports_invalid_request_for_missing_method(self):
        responses, stderr, returncode = self.run_server([{"jsonrpc": "2.0", "id": 1, "params": {}}])

        self.assertEqual(returncode, 0, stderr)
        self.assertEqual(responses[0]["id"], 1)
        self.assertEqual(responses[0]["error"]["code"], -32600)
        self.assertEqual(stderr, "")

    def test_server_ignores_unknown_notifications_without_id(self):
        responses, stderr, returncode = self.run_server_raw(
            '{"jsonrpc":"2.0","method":"notifications/unknown","params":{}}\n'
        )

        self.assertEqual(returncode, 0, stderr)
        self.assertEqual(responses, [])
        self.assertEqual(stderr, "")

    def test_server_ignores_known_notifications_without_id(self):
        responses, stderr, returncode = self.run_server(
            [
                {
                    "jsonrpc": "2.0",
                    "method": "initialize",
                    "params": {"protocolVersion": "2025-11-25", "capabilities": {}},
                },
                {"jsonrpc": "2.0", "method": "tools/list", "params": {}},
                {
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {"name": "config.resolve", "arguments": {}},
                },
            ]
        )

        self.assertEqual(returncode, 0, stderr)
        self.assertEqual(responses, [])
        self.assertEqual(stderr, "")

    def test_server_returns_jsonrpc_error_for_unexpected_tool_exceptions(self):
        with mock.patch.object(
            agent_equipment_config_mcp_server.agent_equipment_config,
            "call_mcp_tool",
            side_effect=RuntimeError("unexpected runtime failure"),
        ):
            response = agent_equipment_config_mcp_server.handle_request(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {"name": "config.resolve", "arguments": {}},
                }
            )

        assert response is not None
        self.assertEqual(response["id"], 1)
        self.assertNotIn("error", response)
        self.assertTrue(response["result"]["isError"])
        self.assertEqual(response["result"]["content"][0]["text"], "internal error while calling Config tool")

    def test_server_returns_jsonrpc_error_for_unexpected_tool_list_exceptions(self):
        with mock.patch.object(
            agent_equipment_config_mcp_server.agent_equipment_config,
            "mcp_tool_definitions",
            side_effect=RuntimeError("unexpected runtime failure"),
        ):
            response = agent_equipment_config_mcp_server.handle_request(
                {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
            )

        assert response is not None
        self.assertEqual(response["id"], 1)
        self.assertEqual(response["error"]["code"], -32603)
        self.assertEqual(response["error"]["message"], "internal error while listing Config tools")
