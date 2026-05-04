/**
 * Hook: <name>
 * Event: <event>
 * Purpose: <policy or automation>
 *
 * Side-effect classification: choose one of read-only, external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation.
 * Approval behavior: require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation.
 * Failure handling: fail closed for unsafe mutations; return a structured reason.
 */

export type SideEffectClassification =
  | "read-only"
  | "external disclosure"
  | "local write"
  | "network write"
  | "process execution"
  | "privileged operation"
  | "irreversible mutation";

export const hookContract = {
  sideEffectClassification: "read-only",
  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
  failureHandling: "fail closed for unsafe mutations",
} as const satisfies {
  sideEffectClassification: SideEffectClassification;
  approvalBehavior: string;
  failureHandling: string;
};

export type HookDecision = {
  allow: boolean;
  reason: string;
  audit?: Record<string, string>;
};

export type HookEvent = {
  kind: string;
  payload: unknown;
};

export async function handle(event: HookEvent | null | undefined): Promise<HookDecision> {
  if (!event || typeof event.kind !== "string" || event.kind.trim() === "") {
    return { allow: false, reason: "missing or invalid event kind" };
  }

  return {
    allow: false,
    reason: "template requires an explicit allow decision",
  };
}
