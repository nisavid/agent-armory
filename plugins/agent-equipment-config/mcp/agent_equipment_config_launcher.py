#!/usr/bin/env python3.14
from __future__ import annotations

import json
import os
import sys
from pathlib import Path


REPO_SERVER = Path("tools/agent_equipment_config_mcp_server.py")
REPO_MARKER = Path("inventory/equipment.toml")
MARKETPLACE_MARKER = Path(".agents/plugins/marketplace.json")


def has_armory_marketplace(candidate: Path) -> bool:
    try:
        data = json.loads((candidate / MARKETPLACE_MARKER).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False
    if not isinstance(data, dict) or data.get("name") != "agent-armory":
        return False
    plugins = data.get("plugins")
    if not isinstance(plugins, list):
        return False
    return any(
        isinstance(plugin, dict)
        and plugin.get("name") == "agent-equipment-config"
        and isinstance(plugin.get("source"), dict)
        and plugin["source"].get("source") == "local"
        and plugin["source"].get("path") == "./plugins/agent-equipment-config"
        for plugin in plugins
    )


def candidate_is_armory_root(candidate: Path) -> bool:
    return (
        (candidate / REPO_SERVER).is_file()
        and (candidate / REPO_MARKER).is_file()
        and has_armory_marketplace(candidate)
    )


def find_armory_root(*, env_root: str | None = None, start_dir: Path | None = None) -> Path | None:
    if env_root:
        env_candidate = Path(env_root).expanduser()
        if candidate_is_armory_root(env_candidate):
            return env_candidate.resolve()
    current = (start_dir if start_dir is not None else Path.cwd()).expanduser().resolve()
    if candidate_is_armory_root(current):
        return current
    for candidate in current.parents:
        if candidate_is_armory_root(candidate):
            return candidate.resolve()
    return None


def launch(argv: list[str] | None = None) -> int:
    _argv = argv if argv is not None else sys.argv[1:]
    root = find_armory_root(
        env_root=os.environ.get("AGENT_ARMORY_ROOT"),
    )
    if root is None:
        print(
            "Agent Equipment Config MCP launcher could not find an Agent Armory "
            "checkout. Set AGENT_ARMORY_ROOT to the checkout containing "
            "tools/agent_equipment_config_mcp_server.py.",
            file=sys.stderr,
        )
        return 2

    server = root / REPO_SERVER
    if not server.is_file():
        print(
            "Agent Equipment Config MCP launcher could not find "
            f"{REPO_SERVER} in the resolved Agent Armory checkout.",
            file=sys.stderr,
        )
        return 2

    os.chdir(root)
    python_executable = str(Path(sys.executable).resolve())
    try:
        os.execve(
            python_executable,
            [python_executable, str(server), *_argv],
            os.environ.copy(),
        )
    except OSError as error:
        print(
            f"Agent Equipment Config MCP launcher could not execute {python_executable}: {error}",
            file=sys.stderr,
        )
        return 127
    return 127


if __name__ == "__main__":
    raise SystemExit(launch())
