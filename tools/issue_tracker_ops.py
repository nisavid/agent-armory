#!/usr/bin/env python3.14
from __future__ import annotations

import argparse
import contextlib
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, TextIO

try:
    from . import agent_equipment_config
except ImportError:
    import agent_equipment_config  # type: ignore[no-redef]


DEFAULT_API_VERSION = "2026-03-10"
DEFAULT_ACCEPT = "application/vnd.github+json"
JSONValue = dict | list | str | int | float | bool | None
MUTATION_OPERATIONS = {"create-issue", "update-issue", "comment", "add-blocked-by", "remove-blocked-by"}
CONFIG_EXECUTE_ALLOWED_STATES = {"allowed", "warning"}
CONFIGURED_EXECUTE_CAPABILITY = "configured_execute_mode"
TRACKER_READ_CAPABILITY = "tracker_read"
TRACKER_WRITE_CAPABILITY = "tracker_write"


@dataclass(frozen=True)
class RequestSpec:
    method: str
    endpoint: str
    body: dict | None = None
    jq: str | None = None
    paginate: bool = False


@dataclass(frozen=True)
class LabelAxis:
    name: str
    labels: tuple[str, ...]
    cardinality: str
    description: str


LABEL_AXES = (
    LabelAxis("category", ("bug", "enhancement"), "exactly_one", "coarse issue category role"),
    LabelAxis(
        "state",
        ("needs-triage", "needs-info", "ready-for-agent", "ready-for-human", "wontfix"),
        "exactly_one",
        "mutually exclusive triage state role",
    ),
    LabelAxis(
        "depth",
        ("depth:L0", "depth:L1", "depth:L2", "depth:L3"),
        "at_most_one",
        "deepest triage evidence boundary reached",
    ),
    LabelAxis(
        "work_kind",
        (
            "kind:research",
            "kind:design",
            "kind:documentation",
            "kind:implementation",
            "kind:epic",
            "kind:cleanup",
            "kind:reflection-finding",
        ),
        "prefer_one",
        "primary kind of work required",
    ),
    LabelAxis(
        "engagement_mode",
        (
            "mode:afk-implementation",
            "mode:agent-led-grill",
            "mode:human-decision",
            "mode:linked-context-triage",
            "mode:deep-session",
        ),
        "at_most_one",
        "next expected handling shape",
    ),
    LabelAxis(
        "brief_status",
        ("brief:not-needed", "brief:needed", "brief:present", "brief:stale"),
        "at_most_one",
        "handoff readiness for delegation",
    ),
    LabelAxis(
        "dependency_disposition",
        ("dependency:unblocked", "dependency:blocked", "dependency:unknown", "dependency:needs-recording"),
        "at_most_one",
        "selection effect of known dependency state",
    ),
)


class UsageError(Exception):
    pass


def parse_repo(repo: str) -> tuple[str, str]:
    parts = repo.split("/")
    if len(parts) != 2 or not all(parts):
        raise UsageError("--repo must use OWNER/REPO format")
    return parts[0], parts[1]


def issue_endpoint(repo: str, suffix: str) -> str:
    owner, name = parse_repo(repo)
    return f"repos/{owner}/{name}/{suffix.lstrip('/')}"


def read_body(args: argparse.Namespace) -> str | None:
    body = getattr(args, "body", None)
    body_file = getattr(args, "body_file", None)
    if body_file:
        try:
            return Path(body_file).read_text(encoding="utf-8")
        except OSError as exc:
            raise UsageError(f"could not read --body-file {body_file!r}: {exc.strerror or exc}") from exc
    return body


def positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{value!r} is not a positive integer") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError(f"{value!r} is not a positive integer")
    return parsed


def compact_request(request: RequestSpec) -> dict:
    return {
        key: value
        for key, value in asdict(request).items()
        if value is not None and value is not False
    }


def gh_api_args(request: RequestSpec, *, api_version: str) -> list[str]:
    args = [
        "gh",
        "api",
        "-X",
        request.method,
        request.endpoint,
        "-H",
        f"Accept: {DEFAULT_ACCEPT}",
        "-H",
        f"X-GitHub-Api-Version: {api_version}",
    ]
    if request.body is not None:
        args.extend(["--input", "-"])
    if request.jq is not None:
        args.extend(["--jq", request.jq])
    if request.paginate:
        args.extend(["--paginate", "--slurp"])
    return args


def default_gh(args: list[str], *, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(args, input=input_text, text=True, capture_output=True, check=False)
    except OSError as exc:
        raise UsageError(f"could not run gh: {exc.strerror or exc}") from exc


def call_gh(
    gh: Callable[..., subprocess.CompletedProcess[str]],
    request: RequestSpec,
    *,
    api_version: str,
) -> subprocess.CompletedProcess[str]:
    input_text = json.dumps(request.body, sort_keys=True) if request.body is not None else None
    return gh(gh_api_args(request, api_version=api_version), input_text=input_text)


def parse_json_output(completed: subprocess.CompletedProcess[str]) -> JSONValue:
    output = completed.stdout.strip()
    if not output:
        return None
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return output


def summarize_result(result: JSONValue) -> JSONValue:
    if isinstance(result, list):
        return [summarize_result(item) for item in result]
    if not isinstance(result, dict):
        return result
    keep_keys = [
        "id",
        "node_id",
        "number",
        "html_url",
        "title",
        "state",
        "state_reason",
        "parent_issue_url",
        "issue_dependencies_summary",
        "sub_issues_summary",
    ]
    summary = {key: result[key] for key in keep_keys if key in result}
    return summary or result


def combine_paginated_result(result: JSONValue) -> JSONValue:
    if not isinstance(result, list) or not all(isinstance(page, list) for page in result):
        return result
    combined = []
    for page in result:
        combined.extend(page)
    return combined


def write_json(stdout: TextIO, payload: dict) -> None:
    stdout.write(json.dumps(payload, indent=2, sort_keys=True))
    stdout.write("\n")


def create_issue_request(args: argparse.Namespace) -> RequestSpec:
    body: dict[str, object] = {"title": args.title}
    issue_body = read_body(args)
    if issue_body is not None:
        body["body"] = issue_body
    if args.label:
        body["labels"] = args.label
    if args.assignee:
        body["assignees"] = args.assignee
    return RequestSpec("POST", issue_endpoint(args.repo, "issues"), body)


def update_issue_request(args: argparse.Namespace) -> RequestSpec:
    if args.state_reason is not None and args.state is None:
        raise UsageError("`--state-reason` requires `--state`")
    body: dict[str, object] = {}
    if args.title is not None:
        body["title"] = args.title
    issue_body = read_body(args)
    if issue_body is not None:
        body["body"] = issue_body
    if args.state is not None:
        body["state"] = args.state
    if args.state_reason is not None:
        body["state_reason"] = args.state_reason
    if args.label:
        body["labels"] = args.label
    if args.assignee:
        body["assignees"] = args.assignee
    if not body:
        raise UsageError("update-issue requires at least one field to update")
    return RequestSpec("PATCH", issue_endpoint(args.repo, f"issues/{args.issue_number}"), body)


def comment_request(args: argparse.Namespace) -> RequestSpec:
    body = read_body(args)
    if body is None:
        raise UsageError("comment requires --body or --body-file")
    return RequestSpec("POST", issue_endpoint(args.repo, f"issues/{args.issue_number}/comments"), {"body": body})


def blocking_issue_id_request(args: argparse.Namespace) -> RequestSpec | None:
    if args.blocking_issue_id is not None:
        return None
    return RequestSpec("GET", issue_endpoint(args.repo, f"issues/{args.blocking_issue_number}"), jq=".id")


def add_blocked_by_request(args: argparse.Namespace, issue_id: int | str) -> RequestSpec:
    return RequestSpec(
        "POST",
        issue_endpoint(args.repo, f"issues/{args.issue_number}/dependencies/blocked_by"),
        {"issue_id": int(issue_id)},
    )


def remove_blocked_by_request(args: argparse.Namespace, issue_id: int | str) -> RequestSpec:
    return RequestSpec(
        "DELETE",
        issue_endpoint(args.repo, f"issues/{args.issue_number}/dependencies/blocked_by/{int(issue_id)}"),
    )


def list_dependencies_request(args: argparse.Namespace, relation: str) -> RequestSpec:
    return RequestSpec(
        "GET",
        issue_endpoint(args.repo, f"issues/{args.issue_number}/dependencies/{relation}"),
        paginate=args.paginate,
    )


def audit_labels_request(args: argparse.Namespace) -> RequestSpec:
    return RequestSpec("GET", issue_endpoint(args.repo, f"issues?state={args.issue_state}&per_page=100"), paginate=True)


def label_axes_payload() -> dict[str, dict[str, object]]:
    return {
        axis.name: {
            "labels": list(axis.labels),
            "cardinality": axis.cardinality,
            "description": axis.description,
        }
        for axis in LABEL_AXES
    }


def issue_label_names(issue: dict) -> list[str]:
    label_names: list[str] = []
    labels = issue.get("labels", [])
    if not isinstance(labels, list):
        return label_names
    for label in labels:
        if isinstance(label, dict):
            name = label.get("name")
            if isinstance(name, str):
                label_names.append(name)
        elif isinstance(label, str):
            label_names.append(label)
    return sorted(dict.fromkeys(label_names))


def audit_label_findings(label_names: list[str]) -> list[dict[str, str]]:
    label_set = set(label_names)
    findings: list[dict[str, str]] = []
    for axis in LABEL_AXES:
        matches = [label for label in axis.labels if label in label_set]
        if axis.cardinality == "exactly_one":
            if not matches:
                findings.append(
                    {
                        "severity": "error",
                        "axis": axis.name,
                        "code": "missing",
                        "message": f"Expected exactly one {axis.name} label.",
                    }
                )
            elif len(matches) > 1:
                findings.append(
                    {
                        "severity": "error",
                        "axis": axis.name,
                        "code": "conflict",
                        "message": f"Expected exactly one {axis.name} label; found {', '.join(matches)}.",
                    }
                )
        elif axis.cardinality == "at_most_one" and len(matches) > 1:
            findings.append(
                {
                    "severity": "error",
                    "axis": axis.name,
                    "code": "conflict",
                    "message": f"Expected at most one {axis.name} label; found {', '.join(matches)}.",
                }
            )
        elif axis.cardinality == "prefer_one" and len(matches) > 1:
            findings.append(
                {
                    "severity": "warning",
                    "axis": axis.name,
                    "code": "multi_primary",
                    "message": f"Prefer one primary {axis.name} label; found {', '.join(matches)}.",
                }
            )
    return findings


def audit_issue_labels(issues: JSONValue) -> dict[str, object]:
    if not isinstance(issues, list):
        issues = []
    checked_issues = 0
    errors = 0
    warnings = 0
    issue_findings: list[dict[str, object]] = []
    for issue in issues:
        if not isinstance(issue, dict) or "pull_request" in issue:
            continue
        checked_issues += 1
        label_names = issue_label_names(issue)
        findings = audit_label_findings(label_names)
        if not findings:
            continue
        errors += sum(1 for finding in findings if finding["severity"] == "error")
        warnings += sum(1 for finding in findings if finding["severity"] == "warning")
        issue_findings.append(
            {
                "number": issue.get("number"),
                "html_url": issue.get("html_url"),
                "title": issue.get("title"),
                "labels": label_names,
                "findings": findings,
            }
        )
    return {
        "summary": {
            "checked_issues": checked_issues,
            "issues_with_findings": len(issue_findings),
            "errors": errors,
            "warnings": warnings,
        },
        "issues": issue_findings,
    }


def dry_run_payload(
    operation: str,
    request: RequestSpec,
    *,
    resolved: dict | None = None,
    config: dict | None = None,
) -> dict:
    payload = {
        "mode": "dry-run",
        "operation": operation,
        "policy": {
            "network_requires_execute": True,
            "auth_source": "gh CLI authenticated account",
            "transport": "gh api",
        },
        "request": compact_request(request),
    }
    if resolved is not None:
        payload["resolved"] = resolved
    if config is not None:
        payload["config"] = config
    return payload


def dry_run_audit_labels_payload(args: argparse.Namespace, *, config: dict | None = None) -> dict:
    payload = dry_run_payload(args.operation, audit_labels_request(args), config=config)
    payload["label_axes"] = label_axes_payload()
    return payload


def dry_run_dependency_payload(args: argparse.Namespace, *, config: dict | None = None) -> dict:
    if args.blocking_issue_id is not None:
        request = (
            add_blocked_by_request(args, args.blocking_issue_id)
            if args.operation == "add-blocked-by"
            else remove_blocked_by_request(args, args.blocking_issue_id)
        )
        return dry_run_payload(args.operation, request, config=config)

    resolve_request = blocking_issue_id_request(args)
    if resolve_request is None:
        raise UsageError("dependency operation requires a blocking issue id or number")
    placeholder = f"<resolved from issue #{args.blocking_issue_number}>"
    mutation_request = (
        RequestSpec(
            "POST",
            issue_endpoint(args.repo, f"issues/{args.issue_number}/dependencies/blocked_by"),
            {"issue_id": placeholder},
        )
        if args.operation == "add-blocked-by"
        else RequestSpec(
            "DELETE",
            issue_endpoint(args.repo, f"issues/{args.issue_number}/dependencies/blocked_by/{placeholder}"),
        )
    )
    payload = dry_run_payload(args.operation, mutation_request, config=config)
    payload["steps"] = [compact_request(resolve_request), compact_request(mutation_request)]
    return payload


def config_inputs(args: argparse.Namespace) -> tuple[list[Path], list[Path]]:
    return (
        [Path(path) for path in getattr(args, "config_layer", [])],
        [Path(path) for path in getattr(args, "config_plain_handoff", [])],
    )


def requested_config_behavior(args: argparse.Namespace) -> str:
    if args.operation in MUTATION_OPERATIONS and args.execute:
        return "mutation"
    return "advisory"


def string_decision_state(decision: dict) -> str | None:
    state = decision.get("state")
    return state if isinstance(state, str) else None


def effective_issue_tracker_ops_value(config_result: dict, field_name: str) -> JSONValue:
    effective_config = config_result.get("effective_config", {})
    if not isinstance(effective_config, dict):
        return None
    effective = effective_config.get("effective", {})
    if not isinstance(effective, dict):
        return None
    section = effective.get("issue_tracker_ops", {})
    if not isinstance(section, dict):
        return None
    wrapped = section.get(field_name, {})
    if not isinstance(wrapped, dict):
        return None
    return wrapped.get("value")


def diagnostic_kinds(effective_config: dict) -> list[str]:
    diagnostics = effective_config.get("diagnostics", [])
    if not isinstance(diagnostics, list):
        return []
    kinds = {
        item.get("kind")
        for item in diagnostics
        if isinstance(item, dict) and isinstance(item.get("kind"), str)
    }
    return sorted(kinds)


def issue_tracker_ops_enforcement_projection(args: argparse.Namespace, config_result: dict) -> dict:
    effective_config = config_result.get("effective_config", {})
    if not isinstance(effective_config, dict):
        effective_config = {}
    projection = effective_config.get("enforcement_projection", {})
    if not isinstance(projection, dict):
        projection = {}
    decision = config_result.get("consumer_action_decision", {})
    if not isinstance(decision, dict):
        decision = {}
    decision_state = string_decision_state(decision)
    mutation_requested = args.operation in MUTATION_OPERATIONS and args.execute
    if mutation_requested:
        adapter_action = "allow" if decision_state in CONFIG_EXECUTE_ALLOWED_STATES else "block"
    else:
        adapter_action = "advise"
    return {
        "surface": "issue_tracker_ops.github_api_mutation_preflight",
        "operation": args.operation,
        "requested_behavior": requested_config_behavior(args),
        "mutation_requested": mutation_requested,
        "adapter_action": adapter_action,
        "decision_state": decision_state or "unknown",
        "approval_behavior": "not_supported",
        "owner": "issue_tracker_ops_adapter",
        "fallback": decision.get("fallback", "none"),
        "effective_config": {
            "safety_status": effective_config.get("safety_status"),
            "projection_classification": projection.get("classification"),
            "diagnostic_kinds": diagnostic_kinds(effective_config),
        },
    }


def evaluate_issue_tracker_ops_config(args: argparse.Namespace) -> dict | None:
    layer_paths, plain_handoff_paths = config_inputs(args)
    if not layer_paths and not plain_handoff_paths:
        return None
    requested_behavior = requested_config_behavior(args)
    required_capabilities = [TRACKER_WRITE_CAPABILITY] if requested_behavior == "mutation" else []
    supported_capabilities = [TRACKER_READ_CAPABILITY, TRACKER_WRITE_CAPABILITY]
    try:
        config_result = agent_equipment_config.evaluate_consumer_config(
            layer_paths,
            [agent_equipment_config.issue_tracker_ops_fragment()],
            equipment="issue_tracker_ops",
            requested_behavior=requested_behavior,
            plain_handoff_paths=plain_handoff_paths,
            required_capabilities=required_capabilities,
            supported_capabilities=supported_capabilities,
        )
    except (OSError, agent_equipment_config.ConfigError) as exc:
        raise UsageError(f"could not evaluate Issue Tracker Ops Config: {exc}") from exc

    configured_mode = effective_issue_tracker_ops_value(config_result, "mode")
    config_result["consumer_semantics"] = {
        "configured_mode": configured_mode,
        "execute_requires_mode": "execute",
        "live_write_capability": TRACKER_WRITE_CAPABILITY,
    }
    decision = config_result.get("consumer_action_decision", {})
    decision_state = decision.get("state") if isinstance(decision, dict) else None
    if requested_behavior == "mutation" and configured_mode != "execute" and decision_state not in {"blocking"}:
        config_result["consumer_action_decision"] = agent_equipment_config.consumer_action_decision(
            config_result["effective_config"],
            equipment="issue_tracker_ops",
            requested_behavior=requested_behavior,
            required_capabilities=[CONFIGURED_EXECUTE_CAPABILITY, TRACKER_WRITE_CAPABILITY],
            supported_capabilities=[TRACKER_READ_CAPABILITY, TRACKER_WRITE_CAPABILITY],
        )
    config_result["consumer_enforcement_projection"] = issue_tracker_ops_enforcement_projection(args, config_result)
    return agent_equipment_config.redact_for_cli(config_result)


def config_refuses_execute(config: dict | None, args: argparse.Namespace) -> bool:
    if config is None or args.operation not in MUTATION_OPERATIONS or not args.execute:
        return False
    return config_execute_refusal(config) is not None


def config_execute_refusal(config: dict) -> tuple[str, str] | None:
    projection = config.get("consumer_enforcement_projection")
    if not isinstance(projection, dict):
        return "unknown", "missing or malformed consumer_enforcement_projection"
    decision = config.get("consumer_action_decision")
    if not isinstance(decision, dict):
        return "unknown", "missing or malformed consumer action decision"

    state = string_decision_state(decision)
    adapter_action = projection.get("adapter_action")
    if adapter_action != "allow":
        action = adapter_action if isinstance(adapter_action, str) and adapter_action else "missing"
        return state or "unknown", f"adapter projection action was {action}"
    if state not in CONFIG_EXECUTE_ALLOWED_STATES:
        reason = decision.get("reason")
        if not isinstance(reason, str) or not reason:
            reason = "consumer action decision did not authorize execute"
        return state or "unknown", reason
    return None


def config_refusal_payload(operation: str, request: RequestSpec | dict, config: dict) -> dict:
    refusal = config_execute_refusal(config)
    state, reason = (
        refusal
        if refusal is not None
        else ("unknown", "consumer action decision did not authorize execute")
    )
    request_payload = compact_request(request) if isinstance(request, RequestSpec) else request
    return {
        "mode": "execute",
        "operation": operation,
        "request": request_payload,
        "config": config,
        "error": {
            "code": "config_refused",
            "state": state,
            "message": f"Issue Tracker Ops Config did not authorize execute: {reason}",
        },
    }


def execute_audit_labels(
    args: argparse.Namespace,
    *,
    gh: Callable[..., subprocess.CompletedProcess[str]],
    stdout: TextIO,
    stderr: TextIO,
    config: dict | None = None,
) -> int:
    request = audit_labels_request(args)
    completed = call_gh(gh, request, api_version=args.api_version)
    if completed.returncode != 0:
        payload = {
            "mode": "execute",
            "operation": args.operation,
            "request": compact_request(request),
            "error": {
                "returncode": completed.returncode,
                "stderr": completed.stderr.strip(),
            },
        }
        if config is not None:
            payload["config"] = config
        write_json(stdout, payload)
        return completed.returncode
    result = parse_json_output(completed)
    result = combine_paginated_result(result)
    if not isinstance(result, list) or not all(isinstance(item, dict) for item in result):
        error = {
            "returncode": 1,
            "stderr": "unexpected GitHub issue list response",
        }
        if completed.stderr:
            error["gh_stderr"] = completed.stderr.strip()
        payload = {
            "mode": "execute",
            "operation": args.operation,
            "request": compact_request(request),
            "error": error,
        }
        if config is not None:
            payload["config"] = config
        write_json(stdout, payload)
        if completed.stderr:
            stderr.write(completed.stderr)
        return 1
    payload = {
        "mode": "execute",
        "operation": args.operation,
        "request": compact_request(request),
        "result": audit_issue_labels(result),
    }
    if config is not None:
        payload["config"] = config
    write_json(stdout, payload)
    if completed.stderr:
        stderr.write(completed.stderr)
    return 0


def execute_request(
    operation: str,
    request: RequestSpec,
    *,
    args: argparse.Namespace,
    gh: Callable[..., subprocess.CompletedProcess[str]],
    stdout: TextIO,
    stderr: TextIO,
    resolved: dict | None = None,
    config: dict | None = None,
) -> int:
    completed = call_gh(gh, request, api_version=args.api_version)
    if completed.returncode != 0:
        payload = {
            "mode": "execute",
            "operation": operation,
            "request": compact_request(request),
            "error": {
                "returncode": completed.returncode,
                "stderr": completed.stderr.strip(),
            },
        }
        if resolved is not None:
            payload["resolved"] = resolved
        if config is not None:
            payload["config"] = config
        write_json(stdout, payload)
        return completed.returncode
    result = parse_json_output(completed)
    if request.paginate:
        result = combine_paginated_result(result)
    payload = {
        "mode": "execute",
        "operation": operation,
        "request": compact_request(request),
        "result": summarize_result(result),
    }
    if resolved is not None:
        payload["resolved"] = resolved
    if config is not None:
        payload["config"] = config
    write_json(stdout, payload)
    if completed.stderr:
        stderr.write(completed.stderr)
    return 0


def resolve_blocking_issue_id(
    args: argparse.Namespace,
    *,
    gh: Callable[..., subprocess.CompletedProcess[str]],
    stdout: TextIO,
) -> tuple[int | None, int]:
    if args.blocking_issue_id is not None:
        return args.blocking_issue_id, 0
    request = blocking_issue_id_request(args)
    if request is None:
        raise UsageError("dependency operation requires a blocking issue id or number")
    completed = call_gh(gh, request, api_version=args.api_version)
    if completed.returncode != 0:
        write_json(
            stdout,
            {
                "mode": "execute",
                "operation": "resolve-blocking-issue",
                "request": compact_request(request),
                "error": {
                    "returncode": completed.returncode,
                    "stderr": completed.stderr.strip(),
                },
            },
        )
        return None, completed.returncode
    resolved = parse_json_output(completed)
    if isinstance(resolved, dict) and "id" in resolved:
        resolved = resolved["id"]
    if not isinstance(resolved, int):
        try:
            resolved = int(str(resolved).strip())
        except ValueError as exc:
            raise UsageError("could not resolve blocking issue id from GitHub response") from exc
    return resolved, 0


def add_common_flags(parser: argparse.ArgumentParser, *, mutation: bool = True) -> None:
    parser.add_argument("--repo", required=True, help="Repository in OWNER/REPO format.")
    parser.add_argument(
        "--api-version",
        default=DEFAULT_API_VERSION,
        help=f"GitHub REST API version header. Default: {DEFAULT_API_VERSION}.",
    )
    if mutation:
        parser.add_argument(
            "--execute",
            action="store_true",
            help="Perform the GitHub API mutation. Without this flag, the command emits a dry run.",
        )
    else:
        parser.add_argument(
            "--execute",
            action="store_true",
            help="Perform the GitHub API read. Without this flag, the command emits a dry run.",
        )
    parser.add_argument(
        "--config-layer",
        action="append",
        default=[],
        help="Agent Equipment Config TOML layer to evaluate for this Issue Tracker Ops command.",
    )
    parser.add_argument(
        "--config-plain-handoff",
        action="append",
        default=[],
        help="Plain Issue Tracker Ops handoff TOML file to promote as session Config.",
    )


def add_body_flags(parser: argparse.ArgumentParser, *, required: bool = False) -> None:
    group = parser.add_mutually_exclusive_group(required=required)
    group.add_argument("--body", help="Markdown body text.")
    group.add_argument("--body-file", help="Path to a UTF-8 Markdown body file.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="issue_tracker_ops",
        description="GitHub Issues adapter MVP for Issue Tracker Ops Equipment.",
    )
    subparsers = parser.add_subparsers(dest="operation", required=True)

    create = subparsers.add_parser("create-issue", help="Create an issue.")
    add_common_flags(create)
    create.add_argument("--title", required=True)
    add_body_flags(create)
    create.add_argument("--label", action="append", default=[])
    create.add_argument("--assignee", action="append", default=[])

    update = subparsers.add_parser("update-issue", help="Update an issue.")
    add_common_flags(update)
    update.add_argument("--issue-number", required=True, type=positive_int)
    update.add_argument("--title")
    add_body_flags(update)
    update.add_argument("--state", choices=["open", "closed"])
    update.add_argument("--state-reason", choices=["completed", "not_planned", "duplicate", "reopened"])
    update.add_argument("--label", action="append", default=[])
    update.add_argument("--assignee", action="append", default=[])

    comment = subparsers.add_parser("comment", help="Add an issue comment.")
    add_common_flags(comment)
    comment.add_argument("--issue-number", required=True, type=positive_int)
    add_body_flags(comment, required=True)

    add_dep = subparsers.add_parser("add-blocked-by", help="Mark an issue as blocked by another issue.")
    add_common_flags(add_dep)
    add_dep.add_argument("--issue-number", required=True, type=positive_int)
    blocker = add_dep.add_mutually_exclusive_group(required=True)
    blocker.add_argument("--blocking-issue-id", type=positive_int)
    blocker.add_argument("--blocking-issue-number", type=positive_int)

    remove_dep = subparsers.add_parser("remove-blocked-by", help="Remove a blocked-by relationship.")
    add_common_flags(remove_dep)
    remove_dep.add_argument("--issue-number", required=True, type=positive_int)
    remove_blocker = remove_dep.add_mutually_exclusive_group(required=True)
    remove_blocker.add_argument("--blocking-issue-id", type=positive_int)
    remove_blocker.add_argument("--blocking-issue-number", type=positive_int)

    list_blocked_by = subparsers.add_parser("list-blocked-by", help="List issues that block an issue.")
    add_common_flags(list_blocked_by, mutation=False)
    list_blocked_by.add_argument("--issue-number", required=True, type=positive_int)
    list_blocked_by.add_argument("--paginate", action="store_true")

    list_blocking = subparsers.add_parser("list-blocking", help="List issues blocked by an issue.")
    add_common_flags(list_blocking, mutation=False)
    list_blocking.add_argument("--issue-number", required=True, type=positive_int)
    list_blocking.add_argument("--paginate", action="store_true")

    audit_labels = subparsers.add_parser("audit-labels", help="Audit issue labels against baseline axes.")
    add_common_flags(audit_labels, mutation=False)
    audit_labels.add_argument("--issue-state", choices=["open", "closed", "all"], default="open")

    return parser


def build_primary_request(args: argparse.Namespace) -> RequestSpec:
    if args.operation == "create-issue":
        return create_issue_request(args)
    if args.operation == "update-issue":
        return update_issue_request(args)
    if args.operation == "comment":
        return comment_request(args)
    if args.operation == "list-blocked-by":
        return list_dependencies_request(args, "blocked_by")
    if args.operation == "list-blocking":
        return list_dependencies_request(args, "blocking")
    raise UsageError(f"{args.operation} requires dependency resolution")


def run(
    argv: list[str] | None = None,
    *,
    gh: Callable[..., subprocess.CompletedProcess[str]] = default_gh,
    stdout: TextIO = sys.stdout,
    stderr: TextIO = sys.stderr,
) -> int:
    parser = build_parser()
    try:
        try:
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                args = parser.parse_args(argv)
        except SystemExit as exc:
            return exc.code if isinstance(exc.code, int) else 1
        config = evaluate_issue_tracker_ops_config(args)
        if args.operation in {"add-blocked-by", "remove-blocked-by"}:
            if not args.execute:
                write_json(stdout, dry_run_dependency_payload(args, config=config))
                return 0
            if config_refuses_execute(config, args):
                write_json(stdout, config_refusal_payload(args.operation, dry_run_dependency_payload(args)["request"], config))
                return 1
            blocking_issue_id, exit_code = resolve_blocking_issue_id(args, gh=gh, stdout=stdout)
            if exit_code != 0 or blocking_issue_id is None:
                return exit_code
            request = (
                add_blocked_by_request(args, blocking_issue_id)
                if args.operation == "add-blocked-by"
                else remove_blocked_by_request(args, blocking_issue_id)
            )
            return execute_request(
                args.operation,
                request,
                args=args,
                gh=gh,
                stdout=stdout,
                stderr=stderr,
                resolved={"blocking_issue_id": blocking_issue_id},
                config=config,
            )

        if args.operation == "audit-labels":
            if not args.execute:
                write_json(stdout, dry_run_audit_labels_payload(args, config=config))
                return 0
            return execute_audit_labels(args, gh=gh, stdout=stdout, stderr=stderr, config=config)

        request = build_primary_request(args)
        if not args.execute:
            write_json(stdout, dry_run_payload(args.operation, request, config=config))
            return 0
        if config_refuses_execute(config, args):
            write_json(stdout, config_refusal_payload(args.operation, request, config))
            return 1
        return execute_request(args.operation, request, args=args, gh=gh, stdout=stdout, stderr=stderr, config=config)
    except UsageError as exc:
        stderr.write(f"{exc}\n")
        return 2


def main() -> int:
    return run()


if __name__ == "__main__":
    sys.exit(main())
