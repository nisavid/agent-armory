#!/usr/bin/env python3.14
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


FALLBACK_RECORD_SCHEMA = "issue_tracker_ops.fallback_record.v1alpha1"


def mutation_policy(args: Any, config: dict | None) -> dict:
    if config is not None:
        decision = config.get("consumer_action_decision", {})
        state = decision.get("state") if isinstance(decision, dict) else "unknown"
        return {
            "source": "config",
            "state": state if isinstance(state, str) else "unknown",
        }
    return {
        "source": "mutation_policy_ref",
        "ref": getattr(args, "mutation_policy_ref", None),
    }


def find_duplicate_comment(comments: object, body: str) -> dict | None:
    if not isinstance(comments, list):
        return None
    for comment in comments:
        if not isinstance(comment, dict):
            continue
        if comment.get("body") == body:
            return {
                key: comment[key]
                for key in ("id", "html_url", "body")
                if key in comment
            }
    return None


def normalize_title(title: str) -> str:
    return " ".join(title.casefold().split())


def summarize_issue(issue: dict) -> dict:
    return {
        key: issue[key]
        for key in ("id", "number", "html_url", "title", "state")
        if key in issue
    }


def find_duplicate_issue(issues: object, title: str) -> dict | None:
    if not isinstance(issues, list):
        return None
    normalized = normalize_title(title)
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        candidate_title = issue.get("title")
        if isinstance(candidate_title, str) and normalize_title(candidate_title) == normalized:
            return summarize_issue(issue)
    return None


def issue_labels(issue: dict) -> list[str]:
    labels = issue.get("labels", [])
    names: list[str] = []
    if not isinstance(labels, list):
        return names
    for label in labels:
        if isinstance(label, dict) and isinstance(label.get("name"), str):
            names.append(label["name"])
        elif isinstance(label, str):
            names.append(label)
    return sorted(names)


def issue_assignees(issue: dict) -> list[str]:
    assignees = issue.get("assignees", [])
    names: list[str] = []
    if not isinstance(assignees, list):
        return names
    for assignee in assignees:
        if isinstance(assignee, dict) and isinstance(assignee.get("login"), str):
            names.append(assignee["login"])
        elif isinstance(assignee, str):
            names.append(assignee)
    return sorted(names)


def issue_matches_update(issue: object, body: dict) -> bool:
    if not isinstance(issue, dict):
        return False
    for key, value in body.items():
        if key == "labels":
            if sorted(str(item) for item in value) != issue_labels(issue):
                return False
        elif key == "assignees":
            if sorted(str(item) for item in value) != issue_assignees(issue):
                return False
        elif issue.get(key) != value:
            return False
    return True


def find_dependency_relation(relations: object, blocking_issue_id: int) -> dict | None:
    if not isinstance(relations, list):
        return None
    for relation in relations:
        if not isinstance(relation, dict):
            continue
        relation_id = relation.get("id")
        try:
            if int(str(relation_id)) == int(blocking_issue_id):
                return summarize_issue(relation)
        except (TypeError, ValueError):
            continue
    return None


def duplicate_decision(args: Any, existing: dict) -> dict:
    action = getattr(args, "if_duplicate", "block")
    decision = {
        "scope": getattr(args, "duplicate_scope", "open"),
        "action": action,
        "existing": existing,
    }
    override_reason = getattr(args, "duplicate_override_reason", None)
    if override_reason:
        decision["override_reason"] = override_reason
    return decision


def classify_failure(returncode: int, stderr: str, stdout: str = "") -> dict:
    text = f"{stderr}\n{stdout}".casefold()
    failure_class = "unknown"
    retryable = False
    if any(fragment in text for fragment in ("bad credentials", "requires authentication", "authentication failed")):
        failure_class = "auth"
    elif "secondary rate limit" in text:
        failure_class = "secondary-rate-limit"
        retryable = True
    elif "rate limit" in text or "too many requests" in text or "429" in text:
        failure_class = "rate-limit"
        retryable = True
    elif any(fragment in text for fragment in ("resource not accessible", "forbidden", "permission", "403")):
        failure_class = "permission"
    elif "not found" in text or "404" in text:
        failure_class = "not-found"
    elif "validation failed" in text or "unprocessable" in text or "422" in text:
        failure_class = "validation"
    elif "conflict" in text or "409" in text:
        failure_class = "conflict"
        retryable = True
    elif any(fragment in text for fragment in ("timeout", "timed out", "502", "503", "504", "connection reset")):
        failure_class = "outage"
        retryable = True
    return {
        "class": failure_class,
        "returncode": returncode,
        "retryable": retryable,
        "stderr": stderr,
    }


def retry_condition(failure: dict) -> str:
    if failure.get("retryable") is True:
        return "retry after the API condition clears and rerun reconciliation first"
    if failure.get("class") in {"auth", "permission"}:
        return "retry after authentication or permission policy is corrected"
    if failure.get("class") == "validation":
        return "revise the request before retrying"
    return "manual review required before retry"


def compensation_guidance(operation: str, failure: dict) -> str:
    if failure.get("retryable") is True:
        return "Do not assume tracker state changed. Reconcile before retrying the mutation."
    if operation == "create-issue":
        return "Check for a newly created issue before retrying to avoid duplicates."
    if operation == "comment":
        return "Check issue comments before retrying to avoid duplicate notifications."
    if operation in {"add-blocked-by", "remove-blocked-by"}:
        return "Check the native dependency relation before retrying."
    return "Check the target issue state before retrying or applying a compensating update."


def fallback_record(
    *,
    operation: str,
    repo: str,
    request: dict,
    failure: dict,
    mutation_policy: dict,
    idempotency_key: str | None,
) -> dict:
    return {
        "schema": FALLBACK_RECORD_SCHEMA,
        "status": "pending_reconciliation",
        "owner": "issue_tracker_ops_adapter",
        "operation": operation,
        "repo": repo,
        "mutation_policy": mutation_policy,
        "idempotency_key": idempotency_key,
        "intended_tracker_target": {
            "repo": repo,
            "endpoint": request.get("endpoint"),
        },
        "request": request,
        "failure": failure,
        "retry_condition": retry_condition(failure),
        "reconciliation": {
            "required": True,
            "retirement_condition": "intended tracker projection is verified or stakeholder discards the operation",
        },
        "compensation_guidance": compensation_guidance(operation, failure),
        "created_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }


def write_fallback_record(path: str, record: dict) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_fallback_record(path: str) -> dict:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("schema") != FALLBACK_RECORD_SCHEMA:
        raise ValueError("fallback record must use issue_tracker_ops.fallback_record.v1alpha1")
    return payload


def retire_fallback_record(path: str, record: dict, note: str) -> dict:
    retired = dict(record)
    retired["status"] = "retired"
    retired["retirement_note"] = note
    retired["retired_at"] = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    Path(path).write_text(json.dumps(retired, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return retired
