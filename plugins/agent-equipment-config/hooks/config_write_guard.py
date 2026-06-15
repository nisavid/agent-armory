#!/usr/bin/env python3.14
from __future__ import annotations

import json
import re
import sys
from typing import Any


CONFIG_SERVER_NAME = "agent_equipment_config"
WRITE_TOOLS = {"config_apply", "migrate_config_apply"}


def normalized_tool_name(value: str) -> str:
    normalized = re.sub(r"[^0-9A-Za-z]+", "_", value).strip("_").lower()
    return re.sub(r"_+", "_", normalized)


def is_config_local_write_tool(tool_name: str) -> bool:
    parts = tool_name.split("__", 2)
    if len(parts) != 3 or parts[0] != "mcp":
        return False
    server, tool = parts[1], parts[2]
    return normalized_tool_name(server) == CONFIG_SERVER_NAME and normalized_tool_name(tool) in WRITE_TOOLS


def tool_input(payload: dict[str, Any]) -> dict[str, Any]:
    value = payload.get("tool_input")
    if not isinstance(value, dict):
        value = payload.get("arguments")
    if not isinstance(value, dict):
        value = {}
    nested_arguments = value.get("arguments")
    if isinstance(nested_arguments, dict):
        return nested_arguments
    return value


def deny_decision(
    reason: str = 'Agent Equipment Config local-write MCP tools require apply_authority = "operator".',
) -> dict[str, Any]:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }


def evaluate(payload: dict[str, Any]) -> dict[str, Any] | None:
    if payload.get("hook_event_name") not in {None, "PreToolUse"}:
        return None
    tool_name = payload.get("tool_name")
    if not isinstance(tool_name, str) or not is_config_local_write_tool(tool_name):
        return None
    if tool_input(payload).get("apply_authority") == "operator":
        return None
    return deny_decision()


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        print(
            json.dumps(
                deny_decision("Agent Equipment Config guard hook received malformed JSON input."),
                separators=(",", ":"),
                sort_keys=True,
            )
        )
        return 0
    if not isinstance(payload, dict):
        print(
            json.dumps(
                deny_decision("Agent Equipment Config guard hook received non-object JSON input."),
                separators=(",", ":"),
                sort_keys=True,
            )
        )
        return 0
    decision = evaluate(payload)
    if decision is not None:
        print(json.dumps(decision, separators=(",", ":"), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
