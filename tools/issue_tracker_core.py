#!/usr/bin/env python3.14
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


CORE_CONTRACT_SCHEMA = "issue_tracker_ops.core_contract.v1alpha1"
ADAPTER_CONTRACT_SCHEMA = "issue_tracker_ops.adapter_contract.v1alpha1"
OPERATION_PLAN_SCHEMA = "issue_tracker_ops.operation_plan.v1alpha1"
WORKFLOW_CONTRACT_SCHEMA = "issue_tracker_ops.workflow_contract.v1alpha1"
WORKFLOW_PLAN_SCHEMA = "issue_tracker_ops.workflow_plan.v1alpha1"


def contract_payload(schema: str, mode: str, operation: str, body: dict) -> dict:
    return {
        "schema": schema,
        "mode": mode,
        "operation": operation,
        **body,
    }


class OperationClass(StrEnum):
    ADVISORY = "advisory"
    READ = "read"
    WRITE = "write"


class OperationId(StrEnum):
    ISSUE_CREATE = "issue.create"
    ISSUE_READ = "issue.read"
    ISSUE_LIST = "issue.list"
    ISSUE_UPDATE = "issue.update"
    ISSUE_CLOSE = "issue.close"
    COMMENT_CREATE = "comment.create"
    LABEL_SET = "label.set"
    ASSIGNEE_SET = "assignee.set"
    DEPENDENCY_ADD_BLOCKED_BY = "dependency.add_blocked_by"
    DEPENDENCY_REMOVE_BLOCKED_BY = "dependency.remove_blocked_by"
    DEPENDENCY_LIST_BLOCKED_BY = "dependency.list_blocked_by"
    DEPENDENCY_LIST_BLOCKING = "dependency.list_blocking"
    SUBISSUE_LIST = "subissue.list"
    SUBISSUE_GET_PARENT = "subissue.get_parent"
    SUBISSUE_ADD = "subissue.add"
    SUBISSUE_REMOVE = "subissue.remove"
    SUBISSUE_REPRIORITIZE = "subissue.reprioritize"
    STATUS_SET = "status.set"
    PRIORITY_SET = "priority.set"
    EVIDENCE_LINK = "evidence.link"
    ATTACHMENT_ADD = "attachment.add"


class WorkflowId(StrEnum):
    ISSUE_REVIEW = "issue.review"
    ISSUE_REPAIR = "issue.repair"
    ISSUE_ENRICHMENT = "issue.enrichment"
    ISSUE_REFACTOR = "issue.refactor"
    ISSUE_ASSIGNMENT = "issue.assignment"
    ISSUE_DUPLICATE_REVIEW = "issue.duplicate_review"
    ISSUE_SELECTION = "issue.selection"
    ISSUE_SESSION_PICKUP = "issue.session_pickup"
    ISSUE_SET_ORCHESTRATION = "issue_set.orchestration"


class CapabilityDisposition(StrEnum):
    EMULATED = "emulated"
    FALLBACK = "fallback"
    NATIVE = "native"
    UNSUPPORTED = "unsupported"


class SideEffectClass(StrEnum):
    EXTERNAL_DISCLOSURE = "external_disclosure"
    EXTERNAL_NETWORK_READ = "external_network_read"
    EXTERNAL_NETWORK_WRITE = "external_network_write"
    EXTERNAL_NOTIFICATION = "external_notification"
    LOCAL_FILESYSTEM_WRITE = "local_filesystem_write"
    NONE = "none"


class AuditRequirement(StrEnum):
    AUTH_SOURCE = "auth_source"
    DRY_RUN_REQUIRED = "dry_run_required"
    EXPLICIT_EXECUTE_REQUIRED = "explicit_execute_required"
    FAILURE_SUMMARY = "failure_summary"
    POLICY_DECISION = "policy_decision"
    REQUEST_SHAPE = "request_shape"
    RESOLVED_IDS = "resolved_ids"
    RESULT_SUMMARY = "result_summary"


@dataclass(frozen=True)
class OperationDefinition:
    operation_id: OperationId
    title: str
    operation_class: OperationClass
    side_effects: tuple[SideEffectClass, ...]
    audit_requirements: tuple[AuditRequirement, ...]
    summary: str

    def to_json(self) -> dict:
        return {
            "operation_id": self.operation_id.value,
            "title": self.title,
            "operation_class": self.operation_class.value,
            "side_effects": [side_effect.value for side_effect in self.side_effects],
            "audit_requirements": [requirement.value for requirement in self.audit_requirements],
            "summary": self.summary,
        }


@dataclass(frozen=True)
class CapabilityEntry:
    operation_id: OperationId
    disposition: CapabilityDisposition
    adapter_operation: str | None
    runtime_command: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()
    fallback: str | None = None

    def to_json(self) -> dict:
        payload = {
            "operation_id": self.operation_id.value,
            "disposition": self.disposition.value,
            "adapter_operation": self.adapter_operation,
            "runtime_command": list(self.runtime_command),
            "notes": list(self.notes),
            "fallback": self.fallback,
        }
        return {key: value for key, value in payload.items() if value not in (None, [], ())}


@dataclass(frozen=True)
class OperationSafety:
    dry_run_default: bool
    execute_required: bool
    config_preflight_required: bool
    available: bool
    mutation_authority_required: bool = False
    config_authorization_supported: bool = False
    mutation_policy_ref_supported: bool = False

    def to_json(self) -> dict:
        return {
            "dry_run_default": self.dry_run_default,
            "execute_required": self.execute_required,
            "config_preflight_required": self.config_preflight_required,
            "available": self.available,
            "mutation_authority_required": self.mutation_authority_required,
            "config_authorization_supported": self.config_authorization_supported,
            "mutation_policy_ref_supported": self.mutation_policy_ref_supported,
        }


@dataclass(frozen=True)
class OperationPlan:
    adapter: str
    operation: OperationDefinition
    capability: CapabilityEntry
    safety: OperationSafety

    def to_json(self) -> dict:
        return contract_payload(
            OPERATION_PLAN_SCHEMA,
            "plan",
            "plan-operation",
            {
                "adapter": self.adapter,
                "operation_id": self.operation.operation_id.value,
                "title": self.operation.title,
                "operation_class": self.operation.operation_class.value,
                "side_effects": [side_effect.value for side_effect in self.operation.side_effects],
                "audit_requirements": [requirement.value for requirement in self.operation.audit_requirements],
                "capability": self.capability.to_json(),
                "safety": self.safety.to_json(),
            },
        )


@dataclass(frozen=True)
class WorkflowDefinition:
    workflow_id: WorkflowId
    title: str
    summary: str
    required_context: tuple[str, ...]
    read_operations: tuple[OperationId, ...]
    candidate_write_operations: tuple[OperationId, ...]
    output_sections: tuple[str, ...]
    policy_factors: tuple[str, ...]
    judgment_boundary: str
    workflow_class: OperationClass = OperationClass.ADVISORY

    def to_json(self) -> dict:
        return {
            "workflow_id": self.workflow_id.value,
            "workflow_class": self.workflow_class.value,
            "title": self.title,
            "summary": self.summary,
            "required_context": list(self.required_context),
            "read_operations": [operation.value for operation in self.read_operations],
            "candidate_write_operations": [
                operation.value for operation in self.candidate_write_operations
            ],
            "output_sections": list(self.output_sections),
            "policy_factors": list(self.policy_factors),
            "judgment_boundary": self.judgment_boundary,
        }


@dataclass(frozen=True)
class AdapterContract:
    adapter_id: str
    title: str
    tracker: str
    promotion_state: str
    capabilities: tuple[CapabilityEntry, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_json(self) -> dict:
        return {
            "adapter": self.adapter_id,
            "title": self.title,
            "tracker": self.tracker,
            "promotion_state": self.promotion_state,
            "capabilities": {
                capability.operation_id.value: capability.to_json()
                for capability in sorted(self.capabilities, key=lambda item: item.operation_id.value)
            },
            "notes": list(self.notes),
        }


WRITE_AUDIT_REQUIREMENTS = (
    AuditRequirement.REQUEST_SHAPE,
    AuditRequirement.DRY_RUN_REQUIRED,
    AuditRequirement.EXPLICIT_EXECUTE_REQUIRED,
    AuditRequirement.POLICY_DECISION,
    AuditRequirement.RESULT_SUMMARY,
)

DEPENDENCY_WRITE_AUDIT_REQUIREMENTS = (
    AuditRequirement.REQUEST_SHAPE,
    AuditRequirement.DRY_RUN_REQUIRED,
    AuditRequirement.EXPLICIT_EXECUTE_REQUIRED,
    AuditRequirement.POLICY_DECISION,
    AuditRequirement.RESOLVED_IDS,
    AuditRequirement.RESULT_SUMMARY,
)

READ_AUDIT_REQUIREMENTS = (
    AuditRequirement.REQUEST_SHAPE,
    AuditRequirement.AUTH_SOURCE,
    AuditRequirement.RESULT_SUMMARY,
    AuditRequirement.FAILURE_SUMMARY,
)


CORE_OPERATIONS: tuple[OperationDefinition, ...] = (
    OperationDefinition(
        OperationId.ISSUE_CREATE,
        "Create issue",
        OperationClass.WRITE,
        (SideEffectClass.EXTERNAL_NETWORK_WRITE, SideEffectClass.EXTERNAL_DISCLOSURE),
        WRITE_AUDIT_REQUIREMENTS,
        "Create a new issue in the selected tracker.",
    ),
    OperationDefinition(
        OperationId.ISSUE_READ,
        "Read issue",
        OperationClass.READ,
        (SideEffectClass.EXTERNAL_NETWORK_READ,),
        READ_AUDIT_REQUIREMENTS,
        "Read one issue from the selected tracker.",
    ),
    OperationDefinition(
        OperationId.ISSUE_LIST,
        "List issues",
        OperationClass.READ,
        (SideEffectClass.EXTERNAL_NETWORK_READ,),
        READ_AUDIT_REQUIREMENTS,
        "List issues from the selected tracker.",
    ),
    OperationDefinition(
        OperationId.ISSUE_UPDATE,
        "Update issue",
        OperationClass.WRITE,
        (SideEffectClass.EXTERNAL_NETWORK_WRITE, SideEffectClass.EXTERNAL_DISCLOSURE),
        WRITE_AUDIT_REQUIREMENTS,
        "Update mutable issue fields in the selected tracker.",
    ),
    OperationDefinition(
        OperationId.ISSUE_CLOSE,
        "Close issue",
        OperationClass.WRITE,
        (SideEffectClass.EXTERNAL_NETWORK_WRITE, SideEffectClass.EXTERNAL_NOTIFICATION),
        WRITE_AUDIT_REQUIREMENTS,
        "Close an issue with tracker-supported state semantics.",
    ),
    OperationDefinition(
        OperationId.COMMENT_CREATE,
        "Create comment",
        OperationClass.WRITE,
        (
            SideEffectClass.EXTERNAL_NETWORK_WRITE,
            SideEffectClass.EXTERNAL_DISCLOSURE,
            SideEffectClass.EXTERNAL_NOTIFICATION,
        ),
        WRITE_AUDIT_REQUIREMENTS,
        "Add a comment to an issue.",
    ),
    OperationDefinition(
        OperationId.LABEL_SET,
        "Set labels",
        OperationClass.WRITE,
        (SideEffectClass.EXTERNAL_NETWORK_WRITE,),
        WRITE_AUDIT_REQUIREMENTS,
        "Replace or set tracker labels or equivalent predicates.",
    ),
    OperationDefinition(
        OperationId.ASSIGNEE_SET,
        "Set assignees",
        OperationClass.WRITE,
        (SideEffectClass.EXTERNAL_NETWORK_WRITE, SideEffectClass.EXTERNAL_NOTIFICATION),
        WRITE_AUDIT_REQUIREMENTS,
        "Set tracker assignees or equivalent owner fields.",
    ),
    OperationDefinition(
        OperationId.DEPENDENCY_ADD_BLOCKED_BY,
        "Add blocked-by dependency",
        OperationClass.WRITE,
        (SideEffectClass.EXTERNAL_NETWORK_WRITE,),
        DEPENDENCY_WRITE_AUDIT_REQUIREMENTS,
        "Record that one issue is blocked by another issue.",
    ),
    OperationDefinition(
        OperationId.DEPENDENCY_REMOVE_BLOCKED_BY,
        "Remove blocked-by dependency",
        OperationClass.WRITE,
        (SideEffectClass.EXTERNAL_NETWORK_WRITE,),
        DEPENDENCY_WRITE_AUDIT_REQUIREMENTS,
        "Remove a blocked-by relationship.",
    ),
    OperationDefinition(
        OperationId.DEPENDENCY_LIST_BLOCKED_BY,
        "List blockers",
        OperationClass.READ,
        (SideEffectClass.EXTERNAL_NETWORK_READ,),
        READ_AUDIT_REQUIREMENTS,
        "List issues that block a selected issue.",
    ),
    OperationDefinition(
        OperationId.DEPENDENCY_LIST_BLOCKING,
        "List blocked issues",
        OperationClass.READ,
        (SideEffectClass.EXTERNAL_NETWORK_READ,),
        READ_AUDIT_REQUIREMENTS,
        "List issues blocked by a selected issue.",
    ),
    OperationDefinition(
        OperationId.SUBISSUE_LIST,
        "List sub-issues",
        OperationClass.READ,
        (SideEffectClass.EXTERNAL_NETWORK_READ,),
        READ_AUDIT_REQUIREMENTS,
        "List sub-issues attached to a parent issue.",
    ),
    OperationDefinition(
        OperationId.SUBISSUE_GET_PARENT,
        "Get parent issue",
        OperationClass.READ,
        (SideEffectClass.EXTERNAL_NETWORK_READ,),
        READ_AUDIT_REQUIREMENTS,
        "Read the parent issue for a selected sub-issue.",
    ),
    OperationDefinition(
        OperationId.SUBISSUE_ADD,
        "Add sub-issue",
        OperationClass.WRITE,
        (SideEffectClass.EXTERNAL_NETWORK_WRITE,),
        DEPENDENCY_WRITE_AUDIT_REQUIREMENTS,
        "Attach a child issue to a parent issue when the tracker supports it.",
    ),
    OperationDefinition(
        OperationId.SUBISSUE_REMOVE,
        "Remove sub-issue",
        OperationClass.WRITE,
        (SideEffectClass.EXTERNAL_NETWORK_WRITE,),
        DEPENDENCY_WRITE_AUDIT_REQUIREMENTS,
        "Remove a child issue from a parent issue when the tracker supports it.",
    ),
    OperationDefinition(
        OperationId.SUBISSUE_REPRIORITIZE,
        "Reprioritize sub-issue",
        OperationClass.WRITE,
        (SideEffectClass.EXTERNAL_NETWORK_WRITE,),
        DEPENDENCY_WRITE_AUDIT_REQUIREMENTS,
        "Move a child issue within its parent issue's sub-issue order.",
    ),
    OperationDefinition(
        OperationId.STATUS_SET,
        "Set workflow status",
        OperationClass.WRITE,
        (SideEffectClass.EXTERNAL_NETWORK_WRITE,),
        WRITE_AUDIT_REQUIREMENTS,
        "Set workflow status, board column, or equivalent lifecycle state.",
    ),
    OperationDefinition(
        OperationId.PRIORITY_SET,
        "Set priority",
        OperationClass.WRITE,
        (SideEffectClass.EXTERNAL_NETWORK_WRITE,),
        WRITE_AUDIT_REQUIREMENTS,
        "Set priority or equivalent selection metadata.",
    ),
    OperationDefinition(
        OperationId.EVIDENCE_LINK,
        "Link evidence",
        OperationClass.WRITE,
        (SideEffectClass.EXTERNAL_NETWORK_WRITE, SideEffectClass.EXTERNAL_DISCLOSURE),
        WRITE_AUDIT_REQUIREMENTS,
        "Attach evidence by tracker-native link or issue content update.",
    ),
    OperationDefinition(
        OperationId.ATTACHMENT_ADD,
        "Add attachment",
        OperationClass.WRITE,
        (SideEffectClass.EXTERNAL_NETWORK_WRITE, SideEffectClass.EXTERNAL_DISCLOSURE),
        WRITE_AUDIT_REQUIREMENTS,
        "Attach binary or file evidence when the tracker supports it.",
    ),
)


WORKFLOW_JUDGMENT_BOUNDARY = (
    "This workflow may inspect tracker state and prepare recommendations without "
    "mutating the tracker. Accepted writes must be converted into deterministic "
    "Issue Ops operations and executed through the adapter's dry-run and write gates."
)


WORKFLOW_DEFINITIONS: tuple[WorkflowDefinition, ...] = (
    WorkflowDefinition(
        WorkflowId.ISSUE_REVIEW,
        "Review issue quality",
        "Inspect one issue for quality, readiness, policy fit, and repair needs.",
        (
            "issue body",
            "labels",
            "comments or linked evidence",
            "dependency context",
            "parent and sub-issue context",
        ),
        (
            OperationId.ISSUE_READ,
            OperationId.DEPENDENCY_LIST_BLOCKED_BY,
            OperationId.DEPENDENCY_LIST_BLOCKING,
            OperationId.SUBISSUE_GET_PARENT,
            OperationId.SUBISSUE_LIST,
        ),
        (
            OperationId.ISSUE_UPDATE,
            OperationId.COMMENT_CREATE,
            OperationId.LABEL_SET,
        ),
        (
            "evidence_boundary",
            "quality_findings",
            "recommendations",
            "candidate_operations",
            "unresolved_judgment",
        ),
        (
            "configured issue standards",
            "label axes",
            "readiness labels",
            "dependency disposition",
            "brief status",
        ),
        WORKFLOW_JUDGMENT_BOUNDARY,
    ),
    WorkflowDefinition(
        WorkflowId.ISSUE_REPAIR,
        "Prepare issue repairs",
        "Turn review findings into deterministic candidate issue updates.",
        (
            "review findings",
            "current issue body",
            "current labels",
            "dependency context",
        ),
        (
            OperationId.ISSUE_READ,
            OperationId.DEPENDENCY_LIST_BLOCKED_BY,
            OperationId.DEPENDENCY_LIST_BLOCKING,
            OperationId.SUBISSUE_LIST,
        ),
        (
            OperationId.ISSUE_UPDATE,
            OperationId.COMMENT_CREATE,
            OperationId.LABEL_SET,
            OperationId.DEPENDENCY_ADD_BLOCKED_BY,
            OperationId.DEPENDENCY_REMOVE_BLOCKED_BY,
            OperationId.SUBISSUE_ADD,
            OperationId.SUBISSUE_REMOVE,
        ),
        (
            "repair_summary",
            "body_patch",
            "metadata_changes",
            "candidate_operations",
            "verification_notes",
        ),
        (
            "configured issue standards",
            "label axes",
            "dependency semantics",
            "brief status",
            "stakeholder authority",
        ),
        WORKFLOW_JUDGMENT_BOUNDARY,
    ),
    WorkflowDefinition(
        WorkflowId.ISSUE_ENRICHMENT,
        "Prepare issue enrichment",
        "Add source links, evidence, findings, and handoff context to an issue plan.",
        (
            "issue body",
            "source links",
            "file references",
            "evidence artifacts",
            "privacy boundary",
        ),
        (
            OperationId.ISSUE_READ,
            OperationId.DEPENDENCY_LIST_BLOCKED_BY,
        ),
        (
            OperationId.ISSUE_UPDATE,
            OperationId.COMMENT_CREATE,
            OperationId.EVIDENCE_LINK,
            OperationId.ATTACHMENT_ADD,
        ),
        (
            "evidence_boundary",
            "enrichment_candidates",
            "disclosure_review",
            "candidate_operations",
        ),
        (
            "external disclosure policy",
            "evidence durability",
            "source authority",
            "privacy or secret boundary",
        ),
        WORKFLOW_JUDGMENT_BOUNDARY,
    ),
    WorkflowDefinition(
        WorkflowId.ISSUE_REFACTOR,
        "Prepare issue structure refactor",
        "Plan changes to issue structure, parentage, dependencies, and body organization.",
        (
            "issue body",
            "related issues",
            "dependency context",
            "parent and sub-issue context",
        ),
        (
            OperationId.ISSUE_READ,
            OperationId.ISSUE_LIST,
            OperationId.DEPENDENCY_LIST_BLOCKED_BY,
            OperationId.DEPENDENCY_LIST_BLOCKING,
            OperationId.SUBISSUE_GET_PARENT,
            OperationId.SUBISSUE_LIST,
        ),
        (
            OperationId.ISSUE_UPDATE,
            OperationId.COMMENT_CREATE,
            OperationId.DEPENDENCY_ADD_BLOCKED_BY,
            OperationId.DEPENDENCY_REMOVE_BLOCKED_BY,
            OperationId.SUBISSUE_ADD,
            OperationId.SUBISSUE_REMOVE,
            OperationId.SUBISSUE_REPRIORITIZE,
        ),
        (
            "structure_findings",
            "refactor_plan",
            "candidate_operations",
            "compatibility_notes",
        ),
        (
            "parent issue policy",
            "sub-issue policy",
            "dependency semantics",
            "issue taxonomy",
        ),
        WORKFLOW_JUDGMENT_BOUNDARY,
    ),
    WorkflowDefinition(
        WorkflowId.ISSUE_ASSIGNMENT,
        "Prepare issue assignment",
        "Recommend owner, assignee, or delegation changes under configured policy.",
        (
            "issue body",
            "current assignees",
            "labels",
            "role and ownership policy",
        ),
        (
            OperationId.ISSUE_READ,
            OperationId.ISSUE_LIST,
        ),
        (
            OperationId.ASSIGNEE_SET,
            OperationId.LABEL_SET,
            OperationId.COMMENT_CREATE,
        ),
        (
            "assignment_context",
            "recommendations",
            "candidate_operations",
            "operator_questions",
        ),
        (
            "assignee choice",
            "role boundaries",
            "delegation policy",
            "readiness labels",
            "stakeholder authority",
        ),
        WORKFLOW_JUDGMENT_BOUNDARY,
    ),
    WorkflowDefinition(
        WorkflowId.ISSUE_DUPLICATE_REVIEW,
        "Review duplicate or related issues",
        "Compare one issue against open and closed tracker work before disposition.",
        (
            "issue body",
            "candidate related issues",
            "dependency context",
            "PRD linkage",
            "Reflection Finding routing",
        ),
        (
            OperationId.ISSUE_READ,
            OperationId.ISSUE_LIST,
            OperationId.DEPENDENCY_LIST_BLOCKED_BY,
            OperationId.DEPENDENCY_LIST_BLOCKING,
            OperationId.SUBISSUE_GET_PARENT,
            OperationId.SUBISSUE_LIST,
        ),
        (
            OperationId.ISSUE_UPDATE,
            OperationId.ISSUE_CLOSE,
            OperationId.COMMENT_CREATE,
            OperationId.LABEL_SET,
            OperationId.DEPENDENCY_ADD_BLOCKED_BY,
            OperationId.SUBISSUE_ADD,
        ),
        (
            "comparison_scope",
            "duplicate_candidates",
            "recommended_disposition",
            "candidate_operations",
        ),
        (
            "duplicate policy",
            "open and closed issue scope",
            "dependency semantics",
            "PRD linkage",
            "out-of-scope records",
        ),
        WORKFLOW_JUDGMENT_BOUNDARY,
    ),
    WorkflowDefinition(
        WorkflowId.ISSUE_SELECTION,
        "Select next issue or issue set",
        "Explain next-work ordering across readiness, priority, status, and blockers.",
        (
            "candidate issue set",
            "workflow status",
            "priority signals",
            "readiness labels",
            "dependency context",
        ),
        (
            OperationId.ISSUE_LIST,
            OperationId.DEPENDENCY_LIST_BLOCKED_BY,
            OperationId.DEPENDENCY_LIST_BLOCKING,
        ),
        (
            OperationId.PRIORITY_SET,
            OperationId.STATUS_SET,
            OperationId.LABEL_SET,
            OperationId.COMMENT_CREATE,
        ),
        (
            "candidate_set",
            "ordering_explanation",
            "blocked_candidates",
            "recommendations",
            "candidate_operations",
        ),
        (
            "workflow status",
            "priority fields",
            "readiness labels",
            "dependency disposition",
            "stakeholder overrides",
            "work kind",
            "engagement mode",
        ),
        WORKFLOW_JUDGMENT_BOUNDARY,
    ),
    WorkflowDefinition(
        WorkflowId.ISSUE_SESSION_PICKUP,
        "Prepare session pickup",
        "Summarize an issue into a bounded work-session start plan.",
        (
            "issue body",
            "comments or linked handoff",
            "labels",
            "dependency context",
            "parent and sub-issue context",
        ),
        (
            OperationId.ISSUE_READ,
            OperationId.DEPENDENCY_LIST_BLOCKED_BY,
            OperationId.DEPENDENCY_LIST_BLOCKING,
            OperationId.SUBISSUE_GET_PARENT,
            OperationId.SUBISSUE_LIST,
        ),
        (
            OperationId.COMMENT_CREATE,
            OperationId.LABEL_SET,
            OperationId.STATUS_SET,
        ),
        (
            "evidence_boundary",
            "pickup_summary",
            "blocked_or_ready_state",
            "next_actions",
            "candidate_operations",
        ),
        (
            "brief status",
            "readiness labels",
            "dependency disposition",
            "session intent",
            "stakeholder overrides",
        ),
        WORKFLOW_JUDGMENT_BOUNDARY,
    ),
    WorkflowDefinition(
        WorkflowId.ISSUE_SET_ORCHESTRATION,
        "Orchestrate issue set",
        "Plan coordinated changes across related issues without direct mutation.",
        (
            "issue-set membership",
            "parent and sub-issue context",
            "dependency graph",
            "priority and status policy",
            "delegation policy",
        ),
        (
            OperationId.ISSUE_LIST,
            OperationId.DEPENDENCY_LIST_BLOCKED_BY,
            OperationId.DEPENDENCY_LIST_BLOCKING,
            OperationId.SUBISSUE_GET_PARENT,
            OperationId.SUBISSUE_LIST,
        ),
        (
            OperationId.PRIORITY_SET,
            OperationId.STATUS_SET,
            OperationId.LABEL_SET,
            OperationId.ASSIGNEE_SET,
            OperationId.DEPENDENCY_ADD_BLOCKED_BY,
            OperationId.DEPENDENCY_REMOVE_BLOCKED_BY,
            OperationId.SUBISSUE_ADD,
            OperationId.SUBISSUE_REMOVE,
            OperationId.SUBISSUE_REPRIORITIZE,
            OperationId.COMMENT_CREATE,
        ),
        (
            "issue_set_map",
            "ordering_explanation",
            "coordination_risks",
            "candidate_operations",
            "operator_questions",
        ),
        (
            "priority fields",
            "workflow status",
            "readiness labels",
            "delegation policy",
            "dependency disposition",
            "stakeholder overrides",
        ),
        WORKFLOW_JUDGMENT_BOUNDARY,
    ),
)


def core_operations_by_id() -> dict[str, OperationDefinition]:
    return {operation.operation_id.value: operation for operation in CORE_OPERATIONS}


def workflow_definitions_by_id() -> dict[str, WorkflowDefinition]:
    return {workflow.workflow_id.value: workflow for workflow in WORKFLOW_DEFINITIONS}


def core_contract_payload() -> dict:
    operations = core_operations_by_id()
    return contract_payload(
        CORE_CONTRACT_SCHEMA,
        "describe",
        "describe-core",
        {
            "operation_ids": sorted(operations),
            "operation_classes": sorted(item.value for item in OperationClass),
            "audit_requirements": sorted(item.value for item in AuditRequirement),
            "capability_dispositions": sorted(item.value for item in CapabilityDisposition),
            "side_effect_classes": sorted(item.value for item in SideEffectClass),
            "operations": {
                operation_id: operations[operation_id].to_json()
                for operation_id in sorted(operations)
            },
        },
    )


def workflow_contract_payload() -> dict:
    workflows = workflow_definitions_by_id()
    return contract_payload(
        WORKFLOW_CONTRACT_SCHEMA,
        "describe",
        "describe-workflows",
        {
            "workflow_ids": sorted(workflows),
            "workflows": {
                workflow_id: workflows[workflow_id].to_json()
                for workflow_id in sorted(workflows)
            },
        },
    )


GITHUB_ISSUES_BASELINE_ADAPTER = AdapterContract(
    adapter_id="github-issues-baseline",
    title="GitHub Issues Baseline",
    tracker="github_issues",
    promotion_state="bootstrap_implemented_core_inspectable",
    notes=(
        "GitHub Projects fields are follow-up adapter work.",
        "Capabilities describe the current bootstrap script and declared fallback surfaces.",
        "Bootstrap runtime read and write commands require --execute; fallback surfaces may use their own controls.",
    ),
    capabilities=(
        CapabilityEntry(
            OperationId.ISSUE_CREATE,
            CapabilityDisposition.NATIVE,
            "create-issue",
            ("create-issue",),
            ("Creates GitHub Issues through the REST issues endpoint.",),
        ),
        CapabilityEntry(
            OperationId.ISSUE_READ,
            CapabilityDisposition.NATIVE,
            "read-issue",
            ("read-issue",),
            ("Reads one GitHub issue through the REST issues endpoint.",),
        ),
        CapabilityEntry(
            OperationId.ISSUE_LIST,
            CapabilityDisposition.NATIVE,
            "list-issues",
            ("list-issues",),
            ("Lists GitHub Issues through the REST issues endpoint and skips pull requests by default.",),
        ),
        CapabilityEntry(
            OperationId.ISSUE_UPDATE,
            CapabilityDisposition.NATIVE,
            "update-issue",
            ("update-issue",),
            ("Updates GitHub issue title, body, state, state reason, labels, and assignees.",),
        ),
        CapabilityEntry(
            OperationId.ISSUE_CLOSE,
            CapabilityDisposition.NATIVE,
            "update-issue",
            ("update-issue", "--state", "closed"),
            ("Uses the existing issue update operation with closed state.",),
        ),
        CapabilityEntry(
            OperationId.COMMENT_CREATE,
            CapabilityDisposition.NATIVE,
            "comment",
            ("comment",),
            ("Creates GitHub issue comments.",),
        ),
        CapabilityEntry(
            OperationId.LABEL_SET,
            CapabilityDisposition.NATIVE,
            "update-issue",
            ("update-issue", "--label"),
            ("Uses the GitHub issue update labels field.",),
        ),
        CapabilityEntry(
            OperationId.ASSIGNEE_SET,
            CapabilityDisposition.NATIVE,
            "update-issue",
            ("update-issue", "--assignee"),
            ("Uses the GitHub issue update assignees field.",),
        ),
        CapabilityEntry(
            OperationId.DEPENDENCY_ADD_BLOCKED_BY,
            CapabilityDisposition.NATIVE,
            "add-blocked-by",
            ("add-blocked-by",),
            ("Uses GitHub native issue dependencies.",),
        ),
        CapabilityEntry(
            OperationId.DEPENDENCY_REMOVE_BLOCKED_BY,
            CapabilityDisposition.NATIVE,
            "remove-blocked-by",
            ("remove-blocked-by",),
            ("Uses GitHub native issue dependencies.",),
        ),
        CapabilityEntry(
            OperationId.DEPENDENCY_LIST_BLOCKED_BY,
            CapabilityDisposition.NATIVE,
            "list-blocked-by",
            ("list-blocked-by",),
            ("Uses GitHub native issue dependencies.",),
        ),
        CapabilityEntry(
            OperationId.DEPENDENCY_LIST_BLOCKING,
            CapabilityDisposition.NATIVE,
            "list-blocking",
            ("list-blocking",),
            ("Uses GitHub native issue dependencies.",),
        ),
        CapabilityEntry(
            OperationId.SUBISSUE_LIST,
            CapabilityDisposition.NATIVE,
            "list-sub-issues",
            ("list-sub-issues",),
            ("Uses GitHub native sub-issue listing.",),
        ),
        CapabilityEntry(
            OperationId.SUBISSUE_GET_PARENT,
            CapabilityDisposition.NATIVE,
            "get-parent-issue",
            ("get-parent-issue",),
            ("Uses GitHub native parent issue lookup.",),
        ),
        CapabilityEntry(
            OperationId.SUBISSUE_ADD,
            CapabilityDisposition.NATIVE,
            "add-sub-issue",
            ("add-sub-issue",),
            ("Uses GitHub native sub-issue creation.",),
        ),
        CapabilityEntry(
            OperationId.SUBISSUE_REMOVE,
            CapabilityDisposition.NATIVE,
            "remove-sub-issue",
            ("remove-sub-issue",),
            ("Uses GitHub native sub-issue removal.",),
        ),
        CapabilityEntry(
            OperationId.SUBISSUE_REPRIORITIZE,
            CapabilityDisposition.NATIVE,
            "reprioritize-sub-issue",
            ("reprioritize-sub-issue",),
            ("Uses GitHub native sub-issue reprioritization.",),
        ),
        CapabilityEntry(
            OperationId.STATUS_SET,
            CapabilityDisposition.FALLBACK,
            None,
            (),
            ("GitHub Projects fields are not part of the baseline runtime adapter.",),
            "Represent workflow status with configured labels or tracker comments until Projects support lands.",
        ),
        CapabilityEntry(
            OperationId.PRIORITY_SET,
            CapabilityDisposition.FALLBACK,
            None,
            (),
            ("GitHub Projects fields are not part of the baseline runtime adapter.",),
            "Represent priority with configured labels or tracker comments until Projects support lands.",
        ),
        CapabilityEntry(
            OperationId.EVIDENCE_LINK,
            CapabilityDisposition.EMULATED,
            "comment",
            ("comment",),
            ("Records evidence links in issue bodies or comments rather than a tracker-native evidence object.",),
        ),
        CapabilityEntry(
            OperationId.ATTACHMENT_ADD,
            CapabilityDisposition.UNSUPPORTED,
            None,
            (),
            ("The bootstrap REST adapter does not upload or attach binary files.",),
        ),
    ),
)


ADAPTERS = {GITHUB_ISSUES_BASELINE_ADAPTER.adapter_id: GITHUB_ISSUES_BASELINE_ADAPTER}


def adapter_contract(adapter_id: str) -> AdapterContract | None:
    return ADAPTERS.get(adapter_id)


def adapter_contract_payload(adapter_id: str) -> dict | None:
    adapter = adapter_contract(adapter_id)
    if adapter is None:
        return None
    return contract_payload(
        ADAPTER_CONTRACT_SCHEMA,
        "describe",
        "describe-adapter",
        adapter.to_json(),
    )


def operation_plan_payload(adapter_id: str, operation_id: str) -> dict | None:
    operation = core_operations_by_id().get(operation_id)
    adapter = adapter_contract(adapter_id)
    if operation is None or adapter is None:
        return None
    capabilities = {capability.operation_id.value: capability for capability in adapter.capabilities}
    capability = capabilities.get(operation_id)
    if capability is None:
        capability = CapabilityEntry(
            operation.operation_id,
            CapabilityDisposition.UNSUPPORTED,
            None,
            (),
            ("Adapter does not declare this operation.",),
        )
    available = capability.disposition != CapabilityDisposition.UNSUPPORTED
    write_operation = operation.operation_class == OperationClass.WRITE
    network_operation = operation.operation_class in {OperationClass.READ, OperationClass.WRITE}
    safety = OperationSafety(
        dry_run_default=network_operation and available,
        execute_required=network_operation and available,
        config_preflight_required=False,
        available=available,
        mutation_authority_required=write_operation and available,
        config_authorization_supported=write_operation and available,
        mutation_policy_ref_supported=write_operation and available,
    )
    return OperationPlan(
        adapter.adapter_id,
        operation,
        capability,
        safety,
    ).to_json()


def workflow_plan_payload(adapter_id: str, workflow_id: str) -> dict | None:
    adapter = adapter_contract(adapter_id)
    workflow = workflow_definitions_by_id().get(workflow_id)
    if adapter is None or workflow is None:
        return None
    operation_ids = [
        operation.value
        for operation in (
            *workflow.read_operations,
            *workflow.candidate_write_operations,
        )
    ]
    operation_plans = {}
    for operation_id in operation_ids:
        plan = operation_plan_payload(adapter_id, operation_id)
        if plan is None:
            raise RuntimeError(
                f"workflow {workflow_id!r} references unplannable operation {operation_id!r}"
            )
        operation_plans[operation_id] = plan
    return contract_payload(
        WORKFLOW_PLAN_SCHEMA,
        "plan",
        "plan-workflow",
        {
            "adapter": adapter_id,
            **workflow.to_json(),
            "operation_plans": operation_plans,
        },
    )
