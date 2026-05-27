# Defer Agent Test Jig Driver Selection

Status: Accepted

Issue #61 defines Agent Test Jigs as a design package and does not implement a
runner or driver. The first Jig Driver selection is deferred until the
implementation gate applies the driver rubric against OpenClaw, Hermes Agent,
Codex, containers, process sandboxes, temporary worktrees, ephemeral
directories, mock services, network controls, and hybrid approaches. This
keeps the design from prematurely treating a convenient local execution path
as a validated isolation boundary.

## Considered Options

- Select a process-sandbox or hybrid local driver during the design package.
- Select a container-first driver during the design package.
- Defer driver selection until the first implementation slice applies the
  rubric with executable constraints in view.

## Consequences

- The #61 bundle records the driver lifecycle contract and selection rubric,
  but no first driver is accepted yet.
- Follow-up implementation issues must apply the rubric before writing driver
  code.
- Capability and Harness Test Suite claims cannot rely on local jig validation
  until a driver has been selected, implemented, and validated.
