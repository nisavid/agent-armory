# Pressure Scenarios: Agent Test Jigs

Status: Equipment Blueprint
Promotion state: specified

## Deterministic command smoke

Scenario:

A Smith writes a Jig Test Plan that runs one local command in an ephemeral
fixture directory and asserts exit code, stdout contains a marker, stderr is
empty, and no external network effect was attempted.

Expected behavior:

- The runner selects an explicit driver.
- The driver records environment setup, command, stdout, stderr, exit code,
  resource use, attempted effects, and cleanup outcome.
- Deterministic assertions decide the scenario without a Learned Oracle.
- The result is machine-readable and uses `pass` only if setup, execution,
  assertions, and cleanup all satisfy the contract.

## Unsupported isolation

Scenario:

A test needs credential isolation, but the selected driver can isolate the
fixture directory only.

Expected behavior:

- The driver reports unsupported credential isolation.
- The runner does not treat the scenario as a high-rigor capability proof.
- The result records selected-rigor impact and blocks durable capability
  promotion unless the plan accepts the limitation.

## Harness trigger evidence

Scenario:

A Harness Test Suite checks whether a harness exposes a skill trigger signal.
One harness emits a native selection event, another only exposes a surrogate
sentinel in output.

Expected behavior:

- The suite records the evidence class per harness.
- The result does not transfer trigger evidence across harnesses.
- Weaker surrogate evidence is named as a limitation, not hidden behind pass.

## Learned Oracle disagreement

Scenario:

An embedding provider says a freeform answer is similar, an NLI provider is
neutral on a required claim, and a text judge says the answer omits a material
condition.

Expected behavior:

- The runner emits `disagreement`.
- All oracle outputs, thresholds, prompt versions, evidence, and input hashes
  remain attached.
- Codex routes the case to a fresh latest-GPT high-thinking adjudicator and
  records the final decision without deleting the disagreement evidence.

## Local inference unavailable

Scenario:

A test plan includes a semantic assertion but no local inference service is
configured.

Expected behavior:

- Deterministic assertions still run.
- The semantic assertion returns `oracle_error` or `inconclusive` according to
  the accepted provider contract.
- The runner does not infer pass from skipped learned evaluation.

## External network attempt

Scenario:

A fixture or harness attempts to call an external URL while the plan blocks
external network access.

Expected behavior:

- The driver blocks or records the attempt according to its available network
  controls.
- The result names the attempted effect and returns `fail` or `sandbox_error`
  according to whether the control worked.
- The raw destination data remains scratch unless disclosure is approved.

## Fixture contamination

Scenario:

A previous run leaves files, services, or environment variables that could
affect the next run.

Expected behavior:

- Setup or preflight detects the residue.
- The scenario returns `fixture_error` or `infra_error`.
- Cleanup evidence tells the next agent whether manual recovery is needed.

## Review cognitive load

Scenario:

A run produces many assertions, oracle outputs, and artifacts.

Expected behavior:

- The human report summarizes the current decision first.
- Detailed logs, raw model outputs, and traces are grouped behind explicit
  artifact references.
- Labels and actions use the `CONTEXT.md` vocabulary and specific outcome
  language.

## Capability lifecycle consumption

Scenario:

Issue #62 wants to use jig evidence when refreshing or deprecating a Harness
Capability claim.

Expected behavior:

- The lifecycle method consumes structured result statuses and limitations.
- Profile updates remain separate from runner output.
- Durable takeaways route through Harness Capability Profiles, Study Reports,
  Reflection Findings, or follow-up issues only after evidence durability is
  classified.
