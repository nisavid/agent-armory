#!/usr/bin/env python3
"""Stdio MCP server wrapper for Agent Equipment Config."""

from __future__ import annotations

import json
import sys
from json import JSONDecodeError
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import agent_equipment_config


SERVER_NAME = "agent-equipment-config"
SERVER_VERSION = "0.1.0"
SUPPORTED_PROTOCOL_VERSIONS = ("2025-11-25", "2025-06-18")


def jsonrpc_result(request_id: object, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def jsonrpc_error(request_id: object, code: int, message: str, data: object | None = None) -> dict[str, Any]:
    error: dict[str, Any] = {"code": code, "message": message}
    if data is not None:
        error["data"] = data
    return {"jsonrpc": "2.0", "id": request_id, "error": error}


def initialize_result(protocol_version: str) -> dict[str, Any]:
    return {
        "protocolVersion": protocol_version,
        "capabilities": {"tools": {"listChanged": False}},
        "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
    }


def handle_request(message: dict[str, Any]) -> dict[str, Any] | None:
    is_notification = "id" not in message
    request_id = message.get("id")
    method = message.get("method")
    params = message.get("params", {})

    if not isinstance(method, str):
        if is_notification:
            return None
        return jsonrpc_error(request_id, -32600, "JSON-RPC method must be a string")
    if method == "notifications/initialized":
        return None
    if method == "initialize":
        if not isinstance(params, dict):
            return jsonrpc_error(request_id, -32602, "initialize params must be an object")
        protocol_version = params.get("protocolVersion")
        if protocol_version not in SUPPORTED_PROTOCOL_VERSIONS:
            return jsonrpc_error(
                request_id,
                -32602,
                "unsupported MCP protocol version",
                {
                    "requestedProtocolVersion": protocol_version,
                    "supportedProtocolVersions": list(SUPPORTED_PROTOCOL_VERSIONS),
                },
            )
        return jsonrpc_result(request_id, initialize_result(str(protocol_version)))
    if method == "tools/list":
        return jsonrpc_result(request_id, {"tools": agent_equipment_config.mcp_tool_definitions()})
    if method == "tools/call":
        if not isinstance(params, dict):
            return jsonrpc_error(request_id, -32602, "tools/call params must be an object")
        name = params.get("name")
        if not isinstance(name, str):
            return jsonrpc_error(request_id, -32602, "tools/call params.name must be a string")
        arguments = params.get("arguments", {})
        try:
            return jsonrpc_result(request_id, agent_equipment_config.call_mcp_tool(name, arguments))
        except Exception:
            return jsonrpc_result(
                request_id,
                {
                    "content": [{"type": "text", "text": "internal error while calling Config tool"}],
                    "isError": True,
                    "structuredContent": {"tool": name, "error": "internal error while calling Config tool"},
                },
            )

    if is_notification:
        return None
    return jsonrpc_error(request_id, -32601, f"unknown method {method!r}")


def response_for_line(line: str) -> dict[str, Any] | None:
    if not line.strip():
        return None
    try:
        message = json.loads(line)
    except JSONDecodeError as exc:
        return jsonrpc_error(None, -32700, f"parse error: {exc.msg}")
    if not isinstance(message, dict):
        return jsonrpc_error(None, -32600, "JSON-RPC message must be an object")
    return handle_request(message)


def serve_stdio(stdin: Any = sys.stdin, stdout: Any = sys.stdout) -> int:
    for line in stdin:
        response = response_for_line(line)
        if response is not None:
            # lgtm[py/clear-text-logging-sensitive-data] stdout is the MCP protocol channel; Config redacts tool results before this wrapper serializes them.
            stdout.write(json.dumps(response, separators=(",", ":")) + "\n")
            stdout.flush()
    return 0


def main() -> int:
    return serve_stdio()


if __name__ == "__main__":
    raise SystemExit(main())
