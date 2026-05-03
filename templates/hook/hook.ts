/**
 * Hook: <name>
 * Event: <event>
 * Purpose: <policy or automation>
 *
 * Side-effect classification: read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation.
 * Approval behavior: require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation.
 * Failure handling: fail closed for unsafe mutations; return a structured reason.
 */

export const hookContract = {
  sideEffectClassification: "read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation",
  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
  failureHandling: "fail closed for unsafe mutations",
} as const;

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
  if (!event || !event.kind) {
    return { allow: false, reason: "missing event kind" };
  }

  return {
    allow: false,
    reason: "template requires an explicit allow decision",
  };
}
