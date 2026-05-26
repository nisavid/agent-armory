#!/usr/bin/env python3.14
from __future__ import annotations

import argparse
import contextlib
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Iterable, TextIO
from urllib.parse import urlencode

try:
    from . import agent_equipment_config, issue_tracker_core, issue_tracker_safety
except ImportError:
    import agent_equipment_config  # type: ignore[no-redef]
    import issue_tracker_core  # type: ignore[no-redef]
    import issue_tracker_safety  # type: ignore[no-redef]


DEFAULT_API_VERSION = "2026-03-10"
DEFAULT_ACCEPT = "application/vnd.github+json"
JSONValue = dict | list | str | int | float | bool | None
MUTATION_OPERATIONS = {
    "create-issue",
    "update-issue",
    "comment",
    "add-blocked-by",
    "remove-blocked-by",
    "add-sub-issue",
    "remove-sub-issue",
    "reprioritize-sub-issue",
}
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


def query_suffix(base: str, params: dict[str, object]) -> str:
    filtered = {key: value for key, value in params.items() if value not in (None, "", [], ())}
    if not filtered:
        return base
    return f"{base}?{urlencode(filtered)}"


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


def summarize_user(user: object) -> dict | object:
    if isinstance(user, dict) and isinstance(user.get("login"), str):
        return {"login": user["login"]}
    return user


def summarize_milestone(milestone: object) -> dict | object:
    if not isinstance(milestone, dict):
        return milestone
    keep_keys = ["id", "number", "html_url", "title", "state", "due_on"]
    return {key: milestone[key] for key in keep_keys if key in milestone}


def summarize_result(result: JSONValue, *, include_body: bool = False) -> JSONValue:
    if isinstance(result, list):
        return [summarize_result(item, include_body=include_body) for item in result]
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
        "comments",
        "created_at",
        "updated_at",
        "closed_at",
        "locked",
        "active_lock_reason",
        "author_association",
        "parent_issue_url",
        "issue_dependencies_summary",
        "sub_issues_summary",
    ]
    summary = {key: result[key] for key in keep_keys if key in result}
    if include_body and "body" in result:
        summary["body"] = result["body"]
    if "labels" in result:
        summary["labels"] = issue_tracker_safety.issue_labels(result)
    if "assignees" in result:
        summary["assignees"] = issue_tracker_safety.issue_assignees(result)
    if "milestone" in result:
        summary["milestone"] = summarize_milestone(result["milestone"])
    if "user" in result:
        summary["user"] = summarize_user(result["user"])
    if "closed_by" in result:
        summary["closed_by"] = summarize_user(result["closed_by"])
    return summary or result


def combine_paginated_result(result: JSONValue) -> JSONValue:
    if not isinstance(result, list) or not all(isinstance(page, list) for page in result):
        return result
    combined = []
    for page in result:
        combined.extend(page)
    return combined


def parse_request_output(completed: subprocess.CompletedProcess[str], request: RequestSpec) -> JSONValue:
    result = parse_json_output(completed)
    if request.paginate:
        return combine_paginated_result(result)
    return result


def postprocess_result(operation: str, args: argparse.Namespace, result: JSONValue) -> JSONValue:
    if operation == "list-issues" and isinstance(result, list) and not args.include_pull_requests:
        return [item for item in result if not (isinstance(item, dict) and "pull_request" in item)]
    return result


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


def comment_preflight_request(args: argparse.Namespace) -> RequestSpec:
    return RequestSpec("GET", issue_endpoint(args.repo, f"issues/{args.issue_number}/comments?per_page=100"), paginate=True)


def create_issue_preflight_request(args: argparse.Namespace) -> RequestSpec:
    return RequestSpec("GET", issue_endpoint(args.repo, f"issues?state={args.duplicate_scope}&per_page=100"), paginate=True)


def issue_read_preflight_request(args: argparse.Namespace) -> RequestSpec:
    return RequestSpec("GET", issue_endpoint(args.repo, f"issues/{args.issue_number}"))


def read_issue_request(args: argparse.Namespace) -> RequestSpec:
    return RequestSpec("GET", issue_endpoint(args.repo, f"issues/{args.issue_number}"))


def list_issues_request(args: argparse.Namespace) -> RequestSpec:
    return RequestSpec(
        "GET",
        issue_endpoint(
            args.repo,
            query_suffix(
                "issues",
                {
                    "state": args.issue_state,
                    "per_page": args.per_page,
                    "labels": ",".join(args.label) if args.label else None,
                    "assignee": args.assignee,
                    "milestone": args.milestone,
                    "sort": args.sort,
                    "direction": args.direction,
                    "since": args.since,
                },
            ),
        ),
        paginate=args.paginate,
    )


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
        paginate=getattr(args, "paginate", False),
    )


def parent_issue_request(args: argparse.Namespace) -> RequestSpec:
    return RequestSpec("GET", issue_endpoint(args.repo, f"issues/{args.issue_number}/parent"))


def list_sub_issues_request(args: argparse.Namespace) -> RequestSpec:
    return RequestSpec(
        "GET",
        issue_endpoint(args.repo, f"issues/{args.issue_number}/sub_issues"),
        paginate=getattr(args, "paginate", False),
    )


def sub_issue_preflight_request(args: argparse.Namespace) -> RequestSpec:
    return RequestSpec("GET", issue_endpoint(args.repo, f"issues/{args.issue_number}/sub_issues"), paginate=True)


def sub_issue_id_request(args: argparse.Namespace, number: int) -> RequestSpec:
    return RequestSpec("GET", issue_endpoint(args.repo, f"issues/{number}"), jq=".id")


def add_sub_issue_request(args: argparse.Namespace, sub_issue_id: int | str) -> RequestSpec:
    body: dict[str, object] = {"sub_issue_id": int(sub_issue_id)}
    if getattr(args, "replace_parent", False):
        body["replace_parent"] = True
    return RequestSpec("POST", issue_endpoint(args.repo, f"issues/{args.issue_number}/sub_issues"), body)


def remove_sub_issue_request(args: argparse.Namespace, sub_issue_id: int | str) -> RequestSpec:
    return RequestSpec(
        "DELETE",
        issue_endpoint(args.repo, f"issues/{args.issue_number}/sub_issue"),
        {"sub_issue_id": int(sub_issue_id)},
    )


def reprioritize_sub_issue_request(args: argparse.Namespace, sub_issue_id: int | str, position: dict[str, int]) -> RequestSpec:
    body = {"sub_issue_id": int(sub_issue_id), **position}
    return RequestSpec("PATCH", issue_endpoint(args.repo, f"issues/{args.issue_number}/sub_issues/priority"), body)


def dependency_preflight_request(args: argparse.Namespace) -> RequestSpec:
    return RequestSpec(
        "GET",
        issue_endpoint(args.repo, f"issues/{args.issue_number}/dependencies/blocked_by"),
        paginate=True,
    )


def audit_labels_request(args: argparse.Namespace) -> RequestSpec:
    return RequestSpec("GET", issue_endpoint(args.repo, f"issues?state={args.issue_state}&per_page=100"), paginate=True)


def fallback_projection_request(record: dict, repo: str) -> RequestSpec:
    request = record.get("request", {})
    if not isinstance(request, dict):
        raise UsageError("fallback record request must be an object")
    endpoint = request.get("endpoint")
    if not isinstance(endpoint, str):
        raise UsageError("fallback record request endpoint must be a string")
    owner, name = parse_repo(repo)
    prefix = f"repos/{owner}/{name}/"
    if not endpoint.startswith(prefix):
        raise UsageError("fallback record endpoint does not match --repo")
    if endpoint.endswith("/comments"):
        return RequestSpec("GET", f"{endpoint}?per_page=100", paginate=True)
    if endpoint.endswith("/sub_issue") or endpoint.endswith("/sub_issues") or endpoint.endswith("/sub_issues/priority"):
        issue_path = endpoint.rsplit("/", 1)[0]
        if issue_path.endswith("/sub_issues"):
            issue_path = issue_path.rsplit("/", 1)[0]
        return RequestSpec("GET", f"{issue_path}/sub_issues", paginate=True)
    if "/dependencies/blocked_by" in endpoint:
        issue_path = endpoint.split("/dependencies/blocked_by", 1)[0]
        return RequestSpec("GET", f"{issue_path}/dependencies/blocked_by", paginate=True)
    if endpoint.endswith("/issues"):
        return RequestSpec("GET", issue_endpoint(repo, "issues?state=all&per_page=100"), paginate=True)
    return RequestSpec("GET", endpoint)


def label_axes_payload(axes: Iterable[LabelAxis] = LABEL_AXES) -> dict[str, dict[str, object]]:
    return {
        axis.name: {
            "labels": list(axis.labels),
            "cardinality": axis.cardinality,
            "description": axis.description,
        }
        for axis in axes
    }


def configured_label_axes(config: dict | None) -> tuple[LabelAxis, ...]:
    if not isinstance(config, dict):
        return LABEL_AXES
    effective_config = config.get("effective_config")
    if not isinstance(effective_config, dict) or effective_config.get("safety_status") != "usable":
        return LABEL_AXES
    issue_ops = effective_config.get("effective", {}).get("issue_tracker_ops")
    if not isinstance(issue_ops, dict):
        return LABEL_AXES
    label_axes = issue_ops.get("label_axes")
    if not isinstance(label_axes, dict):
        return LABEL_AXES
    value = label_axes.get("value")
    if not isinstance(value, list) or not value:
        return LABEL_AXES
    axes: list[LabelAxis] = []
    for item in value:
        if not isinstance(item, dict):
            return LABEL_AXES
        name = item.get("name")
        labels = item.get("labels")
        cardinality = item.get("cardinality")
        description = item.get("description", "")
        if (
            not isinstance(name, str)
            or not isinstance(labels, list)
            or not all(isinstance(label, str) for label in labels)
            or not isinstance(cardinality, str)
            or not isinstance(description, str)
        ):
            return LABEL_AXES
        axes.append(LabelAxis(name, tuple(labels), cardinality, description))
    return tuple(axes)


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


def audit_label_findings(label_names: list[str], axes: Iterable[LabelAxis] = LABEL_AXES) -> list[dict[str, str]]:
    label_set = set(label_names)
    findings: list[dict[str, str]] = []
    for axis in axes:
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


def audit_issue_labels(issues: JSONValue, axes: Iterable[LabelAxis] = LABEL_AXES) -> dict[str, object]:
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
        findings = audit_label_findings(label_names, axes)
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
    args: argparse.Namespace | None = None,
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
    if args is not None and operation in MUTATION_OPERATIONS:
        payload["mutation_policy"] = issue_tracker_safety.mutation_policy(args, config)
        if getattr(args, "idempotency_key", None):
            payload["idempotency_key"] = args.idempotency_key
        payload["planned_safety_preflight"] = planned_safety_preflight(args)
    return payload


def planned_safety_preflight(args: argparse.Namespace) -> list[dict]:
    if args.operation == "create-issue":
        return [compact_request(create_issue_preflight_request(args))]
    if args.operation == "comment":
        return [compact_request(comment_preflight_request(args))]
    if args.operation == "update-issue":
        return [compact_request(issue_read_preflight_request(args))]
    if args.operation in {"add-blocked-by", "remove-blocked-by"}:
        return [compact_request(dependency_preflight_request(args))]
    if args.operation in {"add-sub-issue", "remove-sub-issue", "reprioritize-sub-issue"}:
        return [compact_request(sub_issue_preflight_request(args))]
    return []


def dry_run_audit_labels_payload(args: argparse.Namespace, *, config: dict | None = None) -> dict:
    payload = dry_run_payload(args.operation, audit_labels_request(args), config=config)
    payload["label_axes"] = label_axes_payload(configured_label_axes(config))
    return payload


def dry_run_reconcile_fallback_payload(args: argparse.Namespace, record: dict, *, config: dict | None = None) -> dict:
    payload = dry_run_payload(args.operation, fallback_projection_request(record, args.repo), config=config)
    payload["fallback_record"] = {
        "file": args.fallback_record_file,
        "schema": record.get("schema"),
        "status": record.get("status"),
        "operation": record.get("operation"),
    }
    return payload


def dry_run_dependency_payload(args: argparse.Namespace, *, config: dict | None = None) -> dict:
    if args.blocking_issue_id is not None:
        request = (
            add_blocked_by_request(args, args.blocking_issue_id)
            if args.operation == "add-blocked-by"
            else remove_blocked_by_request(args, args.blocking_issue_id)
        )
        return dry_run_payload(args.operation, request, config=config, args=args)

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
    payload = dry_run_payload(args.operation, mutation_request, config=config, args=args)
    payload["steps"] = [compact_request(resolve_request), compact_request(mutation_request)]
    return payload


def sub_issue_id_placeholder(args: argparse.Namespace) -> int | str:
    if getattr(args, "sub_issue_id", None) is not None:
        return args.sub_issue_id
    return f"<resolved from issue #{args.sub_issue_number}>"


def reprioritize_position_placeholder(args: argparse.Namespace) -> dict[str, int | str]:
    if getattr(args, "after_id", None) is not None:
        return {"after_id": args.after_id}
    if getattr(args, "before_id", None) is not None:
        return {"before_id": args.before_id}
    if getattr(args, "after_issue_number", None) is not None:
        return {"after_id": f"<resolved from issue #{args.after_issue_number}>"}
    return {"before_id": f"<resolved from issue #{args.before_issue_number}>"}


def add_sub_issue_dry_run_body(args: argparse.Namespace, sub_issue_id: int | str) -> dict[str, object]:
    body: dict[str, object] = {"sub_issue_id": sub_issue_id}
    if getattr(args, "replace_parent", False):
        body["replace_parent"] = True
    return body


def dry_run_sub_issue_payload(args: argparse.Namespace, *, config: dict | None = None) -> dict:
    sub_issue_id = sub_issue_id_placeholder(args)
    if args.operation == "add-sub-issue":
        request = (
            add_sub_issue_request(args, sub_issue_id)
            if isinstance(sub_issue_id, int)
            else RequestSpec(
                "POST",
                issue_endpoint(args.repo, f"issues/{args.issue_number}/sub_issues"),
                add_sub_issue_dry_run_body(args, sub_issue_id),
            )
        )
    elif args.operation == "remove-sub-issue":
        request = (
            remove_sub_issue_request(args, sub_issue_id)
            if isinstance(sub_issue_id, int)
            else RequestSpec(
                "DELETE",
                issue_endpoint(args.repo, f"issues/{args.issue_number}/sub_issue"),
                {"sub_issue_id": sub_issue_id},
            )
        )
    else:
        position = reprioritize_position_placeholder(args)
        request = RequestSpec(
            "PATCH",
            issue_endpoint(args.repo, f"issues/{args.issue_number}/sub_issues/priority"),
            {"sub_issue_id": sub_issue_id, **position},
        )
    payload = dry_run_payload(args.operation, request, config=config, args=args)
    steps = []
    if getattr(args, "sub_issue_number", None) is not None:
        steps.append(compact_request(sub_issue_id_request(args, args.sub_issue_number)))
    for number_attr in ("after_issue_number", "before_issue_number"):
        number = getattr(args, number_attr, None)
        if number is not None:
            steps.append(compact_request(sub_issue_id_request(args, number)))
    if steps:
        steps.append(compact_request(request))
        payload["steps"] = steps
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


def mutation_policy_missing(args: argparse.Namespace, config: dict | None) -> bool:
    if args.operation not in MUTATION_OPERATIONS or not args.execute:
        return False
    if config is not None:
        return False
    return not bool(getattr(args, "mutation_policy_ref", None))


def mutation_policy_refusal_payload(operation: str, request: RequestSpec | dict) -> dict:
    request_payload = compact_request(request) if isinstance(request, RequestSpec) else request
    return {
        "mode": "execute",
        "operation": operation,
        "request": request_payload,
        "error": {
            "code": "mutation_policy_required",
            "message": "Issue Tracker Ops mutation execute requires Config authorization or --mutation-policy-ref.",
        },
    }


def include_idempotency_key(payload: dict, args: argparse.Namespace) -> None:
    if getattr(args, "idempotency_key", None):
        payload["idempotency_key"] = args.idempotency_key


def duplicate_refusal_payload(
    args: argparse.Namespace,
    request: RequestSpec,
    preflight_request: RequestSpec,
    existing: dict,
    *,
    config: dict | None = None,
) -> dict:
    payload = {
        "mode": "execute",
        "operation": args.operation,
        "request": compact_request(request),
        "mutation_policy": issue_tracker_safety.mutation_policy(args, config),
        "preflight": {
            "request": compact_request(preflight_request),
        },
        "duplicate_decision": issue_tracker_safety.duplicate_decision(args, existing),
        "error": {
            "code": "duplicate_detected",
            "message": "Issue Tracker Ops duplicate preflight blocked this mutation.",
        },
    }
    include_idempotency_key(payload, args)
    if config is not None:
        payload["config"] = config
    return payload


def duplicate_return_existing_payload(
    args: argparse.Namespace,
    request: RequestSpec,
    preflight_request: RequestSpec,
    existing: dict,
    *,
    config: dict | None = None,
) -> dict:
    payload = {
        "mode": "execute",
        "operation": args.operation,
        "request": compact_request(request),
        "mutation_policy": issue_tracker_safety.mutation_policy(args, config),
        "preflight": {
            "request": compact_request(preflight_request),
        },
        "duplicate_decision": issue_tracker_safety.duplicate_decision(args, existing),
        "result": {
            "status": "duplicate_returned",
            "existing": existing,
        },
    }
    include_idempotency_key(payload, args)
    if config is not None:
        payload["config"] = config
    return payload


def idempotent_skip_payload(
    args: argparse.Namespace,
    request: RequestSpec,
    preflight_request: RequestSpec,
    reason: str,
    *,
    existing: dict | None = None,
    config: dict | None = None,
) -> dict:
    payload = {
        "mode": "execute",
        "operation": args.operation,
        "request": compact_request(request),
        "mutation_policy": issue_tracker_safety.mutation_policy(args, config),
        "preflight": {
            "request": compact_request(preflight_request),
        },
        "result": {
            "status": "idempotent_skip",
            "reason": reason,
        },
    }
    if existing is not None:
        payload["result"]["existing"] = existing
    include_idempotency_key(payload, args)
    if config is not None:
        payload["config"] = config
    return payload


def preflight_response_invalid_payload(
    args: argparse.Namespace,
    request: RequestSpec,
    preflight_request: RequestSpec,
    message: str,
    *,
    resolved: dict | None = None,
    config: dict | None = None,
) -> dict:
    payload = {
        "mode": "execute",
        "operation": args.operation,
        "request": compact_request(request),
        "mutation_policy": issue_tracker_safety.mutation_policy(args, config),
        "preflight": {
            "request": compact_request(preflight_request),
        },
        "error": {
            "code": "preflight_response_invalid",
            "message": message,
        },
    }
    if resolved is not None:
        payload["resolved"] = resolved
    include_idempotency_key(payload, args)
    if config is not None:
        payload["config"] = config
    return payload


def safety_failure_payload(
    args: argparse.Namespace,
    request: RequestSpec | dict,
    failure: dict,
    *,
    config: dict | None = None,
) -> dict:
    request_payload = compact_request(request) if isinstance(request, RequestSpec) else request
    mutation_policy = issue_tracker_safety.mutation_policy(args, config)
    fallback = None
    fallback_write_error = None
    fallback_path = getattr(args, "fallback_record_file", None)
    if fallback_path:
        fallback = issue_tracker_safety.fallback_record(
            operation=args.operation,
            repo=args.repo,
            request=request_payload,
            failure=failure,
            mutation_policy=mutation_policy,
            idempotency_key=getattr(args, "idempotency_key", None),
        )
        try:
            issue_tracker_safety.write_fallback_record(fallback_path, fallback)
        except OSError as exc:
            fallback_write_error = {
                "code": "fallback_record_write_failed",
                "message": str(exc),
            }
    payload = {
        "mode": "execute",
        "operation": args.operation,
        "request": request_payload,
        "mutation_policy": mutation_policy,
        "failure": failure,
        "retry_condition": issue_tracker_safety.retry_condition(failure),
        "compensation_guidance": issue_tracker_safety.compensation_guidance(args.operation, failure),
        "error": {
            "returncode": failure["returncode"],
            "stderr": failure["stderr"],
            "class": failure["class"],
        },
    }
    if getattr(args, "idempotency_key", None):
        payload["idempotency_key"] = args.idempotency_key
    duplicate_decision = getattr(args, "_issue_tracker_duplicate_decision", None)
    if duplicate_decision is not None:
        payload["duplicate_decision"] = duplicate_decision
    if fallback is not None:
        payload["fallback_record"] = fallback
        payload["fallback_record_file"] = fallback_path
    if fallback_write_error is not None:
        payload["fallback_record_error"] = fallback_write_error
    if config is not None:
        payload["config"] = config
    return payload


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
    if (
        projection.get("surface") != "issue_tracker_ops.github_api_mutation_preflight"
        or projection.get("mutation_requested") is not True
    ):
        return state or "unknown", "consumer_enforcement_projection did not identify live mutation preflight"
    effective_config = config.get("effective_config")
    projection_effective_config = projection.get("effective_config")
    if (
        not isinstance(effective_config, dict)
        or effective_config.get("safety_status") != "usable"
        or not isinstance(projection_effective_config, dict)
        or projection_effective_config.get("safety_status") != "usable"
    ):
        return state or "unknown", "effective Config safety status did not authorize execute"
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
        "result": audit_issue_labels(result, configured_label_axes(config)),
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
        failure = issue_tracker_safety.classify_failure(
            completed.returncode,
            completed.stderr.strip(),
            completed.stdout.strip(),
        )
        payload = safety_failure_payload(args, request, failure, config=config)
        if resolved is not None:
            payload["resolved"] = resolved
        write_json(stdout, payload)
        return completed.returncode
    result = postprocess_result(operation, args, parse_request_output(completed, request))
    payload = {
        "mode": "execute",
        "operation": operation,
        "request": compact_request(request),
        "result": summarize_result(result, include_body=operation == "read-issue"),
    }
    if resolved is not None:
        payload["resolved"] = resolved
    if config is not None:
        payload["config"] = config
    if operation in MUTATION_OPERATIONS:
        payload["mutation_policy"] = issue_tracker_safety.mutation_policy(args, config)
        if getattr(args, "idempotency_key", None):
            payload["idempotency_key"] = args.idempotency_key
        duplicate_decision = getattr(args, "_issue_tracker_duplicate_decision", None)
        if duplicate_decision is not None:
            payload["duplicate_decision"] = duplicate_decision
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


def resolve_issue_id(
    args: argparse.Namespace,
    issue_number: int,
    *,
    gh: Callable[..., subprocess.CompletedProcess[str]],
    stdout: TextIO,
    operation: str = "resolve-issue",
) -> tuple[int | None, int]:
    request = sub_issue_id_request(args, issue_number)
    completed = call_gh(gh, request, api_version=args.api_version)
    if completed.returncode != 0:
        write_json(
            stdout,
            {
                "mode": "execute",
                "operation": operation,
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
    try:
        return int(str(resolved).strip()), 0
    except (TypeError, ValueError) as exc:
        raise UsageError("could not resolve issue id from GitHub response") from exc


def resolve_sub_issue_inputs(
    args: argparse.Namespace,
    *,
    gh: Callable[..., subprocess.CompletedProcess[str]],
    stdout: TextIO,
) -> tuple[dict | None, int]:
    resolved: dict[str, int] = {}
    if getattr(args, "sub_issue_id", None) is not None:
        resolved["sub_issue_id"] = args.sub_issue_id
    else:
        issue_id, exit_code = resolve_issue_id(args, args.sub_issue_number, gh=gh, stdout=stdout)
        if exit_code != 0 or issue_id is None:
            return None, exit_code
        resolved["sub_issue_id"] = issue_id

    if getattr(args, "after_id", None) is not None:
        resolved["after_id"] = args.after_id
    elif getattr(args, "after_issue_number", None) is not None:
        issue_id, exit_code = resolve_issue_id(args, args.after_issue_number, gh=gh, stdout=stdout)
        if exit_code != 0 or issue_id is None:
            return None, exit_code
        resolved["after_id"] = issue_id

    if getattr(args, "before_id", None) is not None:
        resolved["before_id"] = args.before_id
    elif getattr(args, "before_issue_number", None) is not None:
        issue_id, exit_code = resolve_issue_id(args, args.before_issue_number, gh=gh, stdout=stdout)
        if exit_code != 0 or issue_id is None:
            return None, exit_code
        resolved["before_id"] = issue_id
    return resolved, 0


def sub_issue_mutation_request(args: argparse.Namespace, resolved: dict[str, int]) -> RequestSpec:
    if args.operation == "add-sub-issue":
        return add_sub_issue_request(args, resolved["sub_issue_id"])
    if args.operation == "remove-sub-issue":
        return remove_sub_issue_request(args, resolved["sub_issue_id"])
    position = {
        key: resolved[key]
        for key in ("after_id", "before_id")
        if key in resolved
    }
    return reprioritize_sub_issue_request(args, resolved["sub_issue_id"], position)


def preflight_sub_issue_mutation(
    args: argparse.Namespace,
    request: RequestSpec,
    resolved: dict[str, int],
    *,
    gh: Callable[..., subprocess.CompletedProcess[str]],
    config: dict | None,
) -> tuple[int, dict] | None:
    preflight_request = sub_issue_preflight_request(args)
    completed = call_gh(gh, preflight_request, api_version=args.api_version)
    if completed.returncode != 0:
        failure = issue_tracker_safety.classify_failure(
            completed.returncode,
            completed.stderr.strip(),
            completed.stdout.strip(),
        )
        return completed.returncode, safety_failure_payload(args, request, failure, config=config)
    result = parse_request_output(completed, preflight_request)
    if not isinstance(result, list):
        return 1, preflight_response_invalid_payload(
            args,
            request,
            preflight_request,
            "sub-issue preflight expected a list response",
            resolved=resolved,
            config=config,
        )
    existing = issue_tracker_safety.find_issue_by_id(result, resolved["sub_issue_id"])
    if args.operation == "add-sub-issue" and existing is not None:
        return 0, idempotent_skip_payload(
            args,
            request,
            preflight_request,
            "sub-issue relation already exists",
            existing=existing,
            config=config,
        )
    if args.operation == "remove-sub-issue" and existing is None:
        return 0, idempotent_skip_payload(
            args,
            request,
            preflight_request,
            "sub-issue relation is already absent",
            config=config,
        )
    if args.operation == "reprioritize-sub-issue" and existing is None:
        return 1, preflight_response_invalid_payload(
            args,
            request,
            preflight_request,
            "sub-issue relation must exist before reprioritization",
            resolved=resolved,
            config=config,
        )
    return None


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
        parser.add_argument(
            "--mutation-policy-ref",
            help="Policy, approval, issue, PR, or session reference authorizing this live tracker mutation.",
        )
        parser.add_argument("--duplicate-scope", choices=["open", "all"], default="open")
        parser.add_argument(
            "--if-duplicate",
            choices=["block", "return-existing", "allow-with-reason"],
            default="block",
        )
        parser.add_argument("--duplicate-override-reason")
        parser.add_argument("--idempotency-key")
        parser.add_argument("--fallback-record-file")
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

    read_issue = subparsers.add_parser("read-issue", help="Read one issue.")
    add_common_flags(read_issue, mutation=False)
    read_issue.add_argument("--issue-number", required=True, type=positive_int)

    list_issues = subparsers.add_parser("list-issues", help="List repository issues.")
    add_common_flags(list_issues, mutation=False)
    list_issues.add_argument("--issue-state", choices=["open", "closed", "all"], default="open")
    list_issues.add_argument("--label", action="append", default=[])
    list_issues.add_argument("--assignee")
    list_issues.add_argument("--milestone")
    list_issues.add_argument("--sort", choices=["created", "updated", "comments"])
    list_issues.add_argument("--direction", choices=["asc", "desc"])
    list_issues.add_argument("--since")
    list_issues.add_argument("--per-page", type=positive_int, default=100)
    list_issues.add_argument("--paginate", action="store_true")
    list_issues.add_argument("--include-pull-requests", action="store_true")

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

    parent = subparsers.add_parser("get-parent-issue", help="Get the parent issue for an issue.")
    add_common_flags(parent, mutation=False)
    parent.add_argument("--issue-number", required=True, type=positive_int)

    list_sub_issues = subparsers.add_parser("list-sub-issues", help="List sub-issues for an issue.")
    add_common_flags(list_sub_issues, mutation=False)
    list_sub_issues.add_argument("--issue-number", required=True, type=positive_int)
    list_sub_issues.add_argument("--paginate", action="store_true")

    add_sub_issue = subparsers.add_parser("add-sub-issue", help="Attach a sub-issue to a parent issue.")
    add_common_flags(add_sub_issue)
    add_sub_issue.add_argument("--issue-number", required=True, type=positive_int)
    add_sub_issue_target = add_sub_issue.add_mutually_exclusive_group(required=True)
    add_sub_issue_target.add_argument("--sub-issue-id", type=positive_int)
    add_sub_issue_target.add_argument("--sub-issue-number", type=positive_int)
    add_sub_issue.add_argument("--replace-parent", action="store_true")

    remove_sub_issue = subparsers.add_parser("remove-sub-issue", help="Remove a sub-issue from a parent issue.")
    add_common_flags(remove_sub_issue)
    remove_sub_issue.add_argument("--issue-number", required=True, type=positive_int)
    remove_sub_issue_target = remove_sub_issue.add_mutually_exclusive_group(required=True)
    remove_sub_issue_target.add_argument("--sub-issue-id", type=positive_int)
    remove_sub_issue_target.add_argument("--sub-issue-number", type=positive_int)

    reprioritize = subparsers.add_parser("reprioritize-sub-issue", help="Move a sub-issue in parent issue order.")
    add_common_flags(reprioritize)
    reprioritize.add_argument("--issue-number", required=True, type=positive_int)
    reprioritize_target = reprioritize.add_mutually_exclusive_group(required=True)
    reprioritize_target.add_argument("--sub-issue-id", type=positive_int)
    reprioritize_target.add_argument("--sub-issue-number", type=positive_int)
    reprioritize_position = reprioritize.add_mutually_exclusive_group(required=True)
    reprioritize_position.add_argument("--after-id", type=positive_int)
    reprioritize_position.add_argument("--after-issue-number", type=positive_int)
    reprioritize_position.add_argument("--before-id", type=positive_int)
    reprioritize_position.add_argument("--before-issue-number", type=positive_int)

    audit_labels = subparsers.add_parser("audit-labels", help="Audit issue labels against baseline axes.")
    add_common_flags(audit_labels, mutation=False)
    audit_labels.add_argument("--issue-state", choices=["open", "closed", "all"], default="open")

    reconcile = subparsers.add_parser("reconcile-fallback", help="Inspect and optionally retire an Issue Ops fallback record.")
    add_common_flags(reconcile, mutation=False)
    reconcile.add_argument("--fallback-record-file", required=True)
    reconcile.add_argument("--retire-record", action="store_true")
    reconcile.add_argument("--retirement-note", help="Note explaining why the fallback record is being retired.")

    subparsers.add_parser("describe-core", help="Describe the tracker-neutral Issue Tracker Ops core contract.")

    describe_adapter = subparsers.add_parser("describe-adapter", help="Describe an Issue Tracker Ops adapter contract.")
    describe_adapter.add_argument("--adapter", required=True, choices=sorted(issue_tracker_core.ADAPTERS))

    plan_operation = subparsers.add_parser("plan-operation", help="Plan one tracker-neutral operation for an adapter.")
    plan_operation.add_argument("--adapter", required=True, choices=sorted(issue_tracker_core.ADAPTERS))
    plan_operation.add_argument("--operation", dest="operation_id", required=True, choices=sorted(issue_tracker_core.core_operations_by_id()))

    return parser


def build_primary_request(args: argparse.Namespace) -> RequestSpec:
    if args.operation == "read-issue":
        return read_issue_request(args)
    if args.operation == "list-issues":
        return list_issues_request(args)
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
    if args.operation == "get-parent-issue":
        return parent_issue_request(args)
    if args.operation == "list-sub-issues":
        return list_sub_issues_request(args)
    raise UsageError(f"{args.operation} requires dependency resolution")


def preflight_mutation(
    args: argparse.Namespace,
    request: RequestSpec,
    *,
    gh: Callable[..., subprocess.CompletedProcess[str]],
    config: dict | None,
) -> tuple[int, dict] | None:
    if args.operation == "create-issue":
        title = request.body.get("title") if isinstance(request.body, dict) else None
        if not isinstance(title, str):
            return None
        preflight_request = create_issue_preflight_request(args)
        completed = call_gh(gh, preflight_request, api_version=args.api_version)
        if completed.returncode != 0:
            failure = issue_tracker_safety.classify_failure(
                completed.returncode,
                completed.stderr.strip(),
                completed.stdout.strip(),
            )
            return completed.returncode, safety_failure_payload(args, request, failure, config=config)
        result = parse_request_output(completed, preflight_request)
        if not isinstance(result, list):
            return 1, preflight_response_invalid_payload(
                args,
                request,
                preflight_request,
                "issue duplicate preflight expected a list response",
                config=config,
            )
        existing = issue_tracker_safety.find_duplicate_issue(result, title)
        if existing is None:
            return None
        if args.if_duplicate == "allow-with-reason":
            setattr(args, "_issue_tracker_duplicate_decision", issue_tracker_safety.duplicate_decision(args, existing))
            return None
        if args.if_duplicate == "return-existing":
            return 0, duplicate_return_existing_payload(args, request, preflight_request, existing, config=config)
        return 1, duplicate_refusal_payload(args, request, preflight_request, existing, config=config)

    if args.operation == "comment":
        body = request.body.get("body") if isinstance(request.body, dict) else None
        if not isinstance(body, str):
            return None
        preflight_request = comment_preflight_request(args)
        completed = call_gh(gh, preflight_request, api_version=args.api_version)
        if completed.returncode != 0:
            failure = issue_tracker_safety.classify_failure(
                completed.returncode,
                completed.stderr.strip(),
                completed.stdout.strip(),
            )
            return completed.returncode, safety_failure_payload(args, request, failure, config=config)
        result = parse_request_output(completed, preflight_request)
        if not isinstance(result, list):
            return 1, preflight_response_invalid_payload(
                args,
                request,
                preflight_request,
                "comment duplicate preflight expected a list response",
                config=config,
            )
        existing = issue_tracker_safety.find_duplicate_comment(result, body)
        if existing is None:
            return None
        if args.if_duplicate == "allow-with-reason":
            setattr(args, "_issue_tracker_duplicate_decision", issue_tracker_safety.duplicate_decision(args, existing))
            return None
        if args.if_duplicate == "return-existing":
            return 0, duplicate_return_existing_payload(args, request, preflight_request, existing, config=config)
        return 1, duplicate_refusal_payload(args, request, preflight_request, existing, config=config)

    if args.operation == "update-issue":
        body = request.body if isinstance(request.body, dict) else None
        if not body:
            return None
        preflight_request = issue_read_preflight_request(args)
        completed = call_gh(gh, preflight_request, api_version=args.api_version)
        if completed.returncode != 0:
            failure = issue_tracker_safety.classify_failure(
                completed.returncode,
                completed.stderr.strip(),
                completed.stdout.strip(),
            )
            return completed.returncode, safety_failure_payload(args, request, failure, config=config)
        existing_issue = parse_request_output(completed, preflight_request)
        if not isinstance(existing_issue, dict):
            return 1, preflight_response_invalid_payload(
                args,
                request,
                preflight_request,
                "issue update preflight expected an object response",
                config=config,
            )
        if issue_tracker_safety.issue_matches_update(existing_issue, body):
            existing = issue_tracker_safety.summarize_issue(existing_issue)
            return 0, idempotent_skip_payload(
                args,
                request,
                preflight_request,
                "issue already matches requested fields",
                existing=existing,
                config=config,
            )
    return None


def preflight_dependency_mutation(
    args: argparse.Namespace,
    request: RequestSpec,
    blocking_issue_id: int,
    *,
    gh: Callable[..., subprocess.CompletedProcess[str]],
    config: dict | None,
) -> tuple[int, dict] | None:
    preflight_request = dependency_preflight_request(args)
    completed = call_gh(gh, preflight_request, api_version=args.api_version)
    if completed.returncode != 0:
        failure = issue_tracker_safety.classify_failure(
            completed.returncode,
            completed.stderr.strip(),
            completed.stdout.strip(),
        )
        return completed.returncode, safety_failure_payload(args, request, failure, config=config)
    result = parse_request_output(completed, preflight_request)
    if not isinstance(result, list):
        return 1, preflight_response_invalid_payload(
            args,
            request,
            preflight_request,
            "dependency preflight expected a list response",
            resolved={"blocking_issue_id": blocking_issue_id},
            config=config,
        )
    existing = issue_tracker_safety.find_dependency_relation(result, blocking_issue_id)
    if args.operation == "add-blocked-by" and existing is not None:
        return 0, idempotent_skip_payload(
            args,
            request,
            preflight_request,
            "blocked-by relation already exists",
            existing=existing,
            config=config,
        )
    if args.operation == "remove-blocked-by" and existing is None:
        return 0, idempotent_skip_payload(
            args,
            request,
            preflight_request,
            "blocked-by relation is already absent",
            config=config,
        )
    return None


def fallback_projection_status(record: dict, result: JSONValue) -> tuple[str, dict | None]:
    request = record.get("request", {})
    if not isinstance(request, dict):
        return "unknown", None
    operation = record.get("operation")
    if operation == "comment":
        body = request.get("body", {})
        comment_body = body.get("body") if isinstance(body, dict) else None
        if isinstance(comment_body, str):
            existing = issue_tracker_safety.find_duplicate_comment(result, comment_body)
            if existing is not None:
                return "projected", existing
            return "not_projected", None
    if operation == "create-issue":
        body = request.get("body", {})
        title = body.get("title") if isinstance(body, dict) else None
        if isinstance(title, str):
            existing = issue_tracker_safety.find_duplicate_issue(result, title)
            if existing is not None:
                return "projected", existing
            return "not_projected", None
    if operation == "update-issue":
        body = request.get("body", {})
        if isinstance(body, dict):
            if issue_tracker_safety.issue_matches_update(result, body):
                projected = issue_tracker_safety.summarize_issue(result) if isinstance(result, dict) else None
                return "projected", projected
            return "not_projected", None
    if operation == "add-blocked-by":
        if not isinstance(result, list):
            return "unknown", None
        body = request.get("body", {})
        issue_id = body.get("issue_id") if isinstance(body, dict) else None
        try:
            existing = issue_tracker_safety.find_dependency_relation(result, int(str(issue_id)))
        except (TypeError, ValueError):
            return "unknown", None
        if existing is not None:
            return "projected", existing
        return "not_projected", None
    if operation == "remove-blocked-by":
        if not isinstance(result, list):
            return "unknown", None
        endpoint = request.get("endpoint")
        if not isinstance(endpoint, str):
            return "unknown", None
        try:
            issue_id = int(endpoint.rsplit("/", 1)[1])
        except (IndexError, ValueError):
            return "unknown", None
        existing = issue_tracker_safety.find_dependency_relation(result, issue_id)
        if existing is None:
            return "projected", {"issue_id": issue_id, "relation": "absent"}
        return "not_projected", existing
    if operation == "add-sub-issue":
        if not isinstance(result, list):
            return "unknown", None
        body = request.get("body", {})
        issue_id = body.get("sub_issue_id") if isinstance(body, dict) else None
        try:
            existing = issue_tracker_safety.find_issue_by_id(result, int(str(issue_id)))
        except (TypeError, ValueError):
            return "unknown", None
        if existing is not None:
            return "projected", existing
        return "not_projected", None
    if operation == "remove-sub-issue":
        if not isinstance(result, list):
            return "unknown", None
        body = request.get("body", {})
        issue_id = body.get("sub_issue_id") if isinstance(body, dict) else None
        try:
            issue_id_int = int(str(issue_id))
        except (TypeError, ValueError):
            return "unknown", None
        existing = issue_tracker_safety.find_issue_by_id(result, issue_id_int)
        if existing is None:
            return "projected", {"issue_id": issue_id_int, "relation": "absent"}
        return "not_projected", existing
    if operation == "reprioritize-sub-issue":
        if not isinstance(result, list):
            return "unknown", None
        body = request.get("body", {})
        issue_id = body.get("sub_issue_id") if isinstance(body, dict) else None
        try:
            issues = [item for item in result if isinstance(item, dict)]
            index = next(
                position
                for position, issue in enumerate(issues)
                if int(str(issue.get("id"))) == int(str(issue_id))
            )
        except (StopIteration, TypeError, ValueError):
            return "not_projected", None
        after_id = body.get("after_id") if isinstance(body, dict) else None
        before_id = body.get("before_id") if isinstance(body, dict) else None
        if after_id is not None and index > 0:
            try:
                if int(str(issues[index - 1].get("id"))) == int(str(after_id)):
                    return "projected", issue_tracker_safety.summarize_issue(issues[index])
            except (TypeError, ValueError):
                return "unknown", None
        if before_id is not None and index < len(issues) - 1:
            try:
                if int(str(issues[index + 1].get("id"))) == int(str(before_id)):
                    return "projected", issue_tracker_safety.summarize_issue(issues[index])
            except (TypeError, ValueError):
                return "unknown", None
        return "not_projected", issue_tracker_safety.summarize_issue(issues[index])
    return "unknown", None


def execute_reconcile_fallback(
    args: argparse.Namespace,
    *,
    gh: Callable[..., subprocess.CompletedProcess[str]],
    stdout: TextIO,
    config: dict | None = None,
) -> int:
    try:
        record = issue_tracker_safety.load_fallback_record(args.fallback_record_file)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise UsageError(f"could not load fallback record: {exc}") from exc
    request = fallback_projection_request(record, args.repo)
    if not args.execute:
        write_json(stdout, dry_run_reconcile_fallback_payload(args, record, config=config))
        return 0
    completed = call_gh(gh, request, api_version=args.api_version)
    if completed.returncode != 0:
        failure = issue_tracker_safety.classify_failure(
            completed.returncode,
            completed.stderr.strip(),
            completed.stdout.strip(),
        )
        payload = {
            "mode": "execute",
            "operation": args.operation,
            "request": compact_request(request),
            "fallback_record_file": args.fallback_record_file,
            "failure": failure,
            "error": {
                "returncode": completed.returncode,
                "stderr": failure["stderr"],
                "class": failure["class"],
            },
        }
        if config is not None:
            payload["config"] = config
        write_json(stdout, payload)
        return completed.returncode
    status, projected = fallback_projection_status(record, parse_request_output(completed, request))
    recommended_action = {
        "projected": "retire_record",
        "not_projected": "retry_tracker_operation",
    }.get(status, "manual_review")
    result = {
        "projection_status": status,
        "recommended_action": recommended_action,
    }
    if projected is not None:
        result["projected"] = projected
    if args.retire_record:
        if status != "projected":
            write_json(
                stdout,
                {
                    "mode": "execute",
                    "operation": args.operation,
                    "request": compact_request(request),
                    "fallback_record_file": args.fallback_record_file,
                    "result": result,
                    "error": {
                        "code": "retirement_not_allowed",
                        "message": "Fallback record can only be retired after projection is verified.",
                    },
                },
            )
            return 1
        if not args.retirement_note:
            raise UsageError("--retirement-note is required with --retire-record")
        result["retired_record"] = issue_tracker_safety.retire_fallback_record(
            args.fallback_record_file,
            record,
            args.retirement_note,
        )
    payload = {
        "mode": "execute",
        "operation": args.operation,
        "request": compact_request(request),
        "fallback_record_file": args.fallback_record_file,
        "result": result,
    }
    if config is not None:
        payload["config"] = config
    write_json(stdout, payload)
    return 0


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
        if (
            getattr(args, "if_duplicate", None) == "allow-with-reason"
            and not getattr(args, "duplicate_override_reason", None)
        ):
            raise UsageError("--duplicate-override-reason is required with --if-duplicate allow-with-reason")
        if (
            getattr(args, "operation", None) == "reconcile-fallback"
            and getattr(args, "retire_record", False)
            and not getattr(args, "retirement_note", None)
        ):
            raise UsageError("--retirement-note is required with --retire-record")
        config = evaluate_issue_tracker_ops_config(args)
        if args.operation == "describe-core":
            write_json(stdout, issue_tracker_core.core_contract_payload())
            return 0
        if args.operation == "describe-adapter":
            payload = issue_tracker_core.adapter_contract_payload(args.adapter)
            if payload is None:
                raise UsageError(f"unknown adapter {args.adapter!r}")
            write_json(stdout, payload)
            return 0
        if args.operation == "plan-operation":
            payload = issue_tracker_core.operation_plan_payload(args.adapter, args.operation_id)
            if payload is None:
                raise UsageError(f"could not plan {args.operation_id!r} for adapter {args.adapter!r}")
            write_json(stdout, payload)
            return 0
        if args.operation == "reconcile-fallback":
            return execute_reconcile_fallback(args, gh=gh, stdout=stdout, config=config)
        if args.operation in {"add-blocked-by", "remove-blocked-by"}:
            if not args.execute:
                write_json(stdout, dry_run_dependency_payload(args, config=config))
                return 0
            if mutation_policy_missing(args, config):
                write_json(stdout, mutation_policy_refusal_payload(args.operation, dry_run_dependency_payload(args)["request"]))
                return 1
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
            preflight_result = preflight_dependency_mutation(
                args,
                request,
                blocking_issue_id,
                gh=gh,
                config=config,
            )
            if preflight_result is not None:
                exit_code, payload = preflight_result
                write_json(stdout, payload)
                return exit_code
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

        if args.operation in {"add-sub-issue", "remove-sub-issue", "reprioritize-sub-issue"}:
            if not args.execute:
                write_json(stdout, dry_run_sub_issue_payload(args, config=config))
                return 0
            if mutation_policy_missing(args, config):
                write_json(stdout, mutation_policy_refusal_payload(args.operation, dry_run_sub_issue_payload(args)["request"]))
                return 1
            if config_refuses_execute(config, args):
                write_json(stdout, config_refusal_payload(args.operation, dry_run_sub_issue_payload(args)["request"], config))
                return 1
            resolved, exit_code = resolve_sub_issue_inputs(args, gh=gh, stdout=stdout)
            if exit_code != 0 or resolved is None:
                return exit_code
            request = sub_issue_mutation_request(args, resolved)
            preflight_result = preflight_sub_issue_mutation(
                args,
                request,
                resolved,
                gh=gh,
                config=config,
            )
            if preflight_result is not None:
                exit_code, payload = preflight_result
                write_json(stdout, payload)
                return exit_code
            return execute_request(
                args.operation,
                request,
                args=args,
                gh=gh,
                stdout=stdout,
                stderr=stderr,
                resolved=resolved,
                config=config,
            )

        if args.operation == "audit-labels":
            if not args.execute:
                write_json(stdout, dry_run_audit_labels_payload(args, config=config))
                return 0
            return execute_audit_labels(args, gh=gh, stdout=stdout, stderr=stderr, config=config)

        request = build_primary_request(args)
        if not args.execute:
            write_json(stdout, dry_run_payload(args.operation, request, config=config, args=args))
            return 0
        if mutation_policy_missing(args, config):
            write_json(stdout, mutation_policy_refusal_payload(args.operation, request))
            return 1
        if config_refuses_execute(config, args):
            write_json(stdout, config_refusal_payload(args.operation, request, config))
            return 1
        preflight_result = preflight_mutation(args, request, gh=gh, config=config)
        if preflight_result is not None:
            exit_code, payload = preflight_result
            write_json(stdout, payload)
            return exit_code
        return execute_request(args.operation, request, args=args, gh=gh, stdout=stdout, stderr=stderr, config=config)
    except UsageError as exc:
        stderr.write(f"{exc}\n")
        return 2


def main() -> int:
    return run()


if __name__ == "__main__":
    sys.exit(main())
