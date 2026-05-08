# Forge Domain Model Review

Status: completed for issue projection

## Scope

This review covers the domain boundaries that affected the Vanilla Harness
Capability Profiles Epic before child issue projection. It checked
terminology, live validation boundaries, Seed-era names that still carried live
responsibilities, and the split between Forge Canon, Forge Core, Forge
Equipment Core, and Armory Equipment Core.

The review does not execute the validation boundary refactor. It records the
decisions and blockers that the prerequisite implementation story must apply.

## Inputs

- `CONTEXT.md`
- `docs/ubiquitous-language.md`
- `docs/agent-equipment-forge.md`
- `docs/smith-runbook.md`
- `docs/forgewright-runbook.md`
- `docs/story-closeout.md`
- `docs/security/threat-model.md`
- `docs/README.md`
- `README.md`
- `AGENTS.md`
- `specs/vanilla-harness-capability-profiles/`
- At review time: `tools/validate_forge_seed.py`
- At review time: `tests/test_validate_forge_seed.py`

## Boundary Decisions

### Forge Canon

Forge Canon is the current conceptual framework and corresponding
documentation that govern Forge work. It includes vocabulary and explanatory
guidance such as the Forge overview, ubiquitous language, vision-facing Forge
interpretation, interface decision guidance, harness capability facts, evidence
taxonomy, security/control guidance, and promotion guidance.

Forge Canon does not include the deterministic tools or process contracts that
enact those concepts. A document may describe a Forge Core contract, but the
contract itself belongs to Forge Core.

### Forge Core

Forge Core is the materialized and enacted Forge process, contract, component,
and deterministic-tool layer. Current Forge Core surfaces include story
closeout contracts, Forgewright handoff and Tooling Gap process, templates,
validation gates, source-disposition checks, and deterministic repository
validators.

The validation boundary refactor should classify existing validator checks
against Forge Core or Armory Integrity Validation rather than leaving them
under Seed Validation.

### Forge Equipment Core

Forge Equipment Core is the minimal Agent Equipment necessary for Agents to
operate Forge functions in a manner that fulfills Forge contracts. The current
Forge Conveyor, root agent-facing routing, and any future skills or workflow
equipment that Agents rely on to perform Forge work belong here when they are
treated as equipped operational capability rather than only documentation.

This epic should not over-promote prose workflow templates into Forge Equipment
Core. Promotion requires the same evidence and validation discipline as other
Agent Equipment.

### Armory Equipment Core

Armory Equipment Core is the minimal Agent Equipment necessary for Agents to
operate Armory functions outside the Forge. Issue-tracker routing, reflection
finding capture, and future operating-model equipment may become Armory
Equipment Core when they are required for general Armory operation rather than
only Forge work.

Forge Equipment Core and Armory Equipment Core may share equipment. Shared
equipment should be named by the functions it serves rather than forced into
one parent.

## Seed-Era Terms

### Forge Seed

Forge Seed is historical scope: the initial coherent version of the Agent
Equipment Forge. It remains valid when discussing the completed seed PRD,
source disposition, historical closeout, and historical implementation plans.

Live docs should not use Forge Seed as the active domain umbrella once the
validation boundary refactor lands.

### Seed Validation

Seed Validation is historical validation of the completed Forge Seed. It is not
the live repository validation umbrella.

Live repository validation should be named Armory Integrity Validation.
Forge-scoped live validation should be named Forge Integrity Validation.
Equipment behavior should use equipment-specific validation.

### Seed Validation Tool

At review time, `tools/validate_forge_seed.py` was the seed-era implementation
of live repository checks. The validation boundary story renames this surface
into live validation tooling, classifies each check, and removes transient
compatibility paths by story closeout.

### Seed Surface

Seed Surface is historical: a file or directory implemented during the Forge
Seed because it had a clear seed role.

Live surfaces should be classified by current responsibility, such as Forge
Canon surface, Forge Core surface, Forge Equipment Core surface, Armory
Equipment Core surface, Equipment Design Bundle, or Equipment Candidate
surface.

## Live Surface Classification

| Surface | Current classification | Notes |
| --- | --- | --- |
| `CONTEXT.md` | Armory and Forge vocabulary register | Project-wide vocabulary; not only Forge Canon. |
| `docs/ubiquitous-language.md` | Forge Canon vocabulary surface | Forge-applied subset of the project vocabulary. |
| `docs/agent-equipment-forge.md` | Forge Canon | Conceptual Forge overview and component model. |
| `docs/vision.md` | Armory/Forge Canon input | Experience and architecture north star used by Forge and non-Forge Armory work. |
| `docs/smith-runbook.md` | Forge Core contract documentation | Procedure for Smith work; describes enacted workflow expectations. |
| `docs/forgewright-runbook.md` | Forge Core contract documentation | Procedure for Forge maintenance and Tooling Gap intake. |
| `docs/story-closeout.md` | Forge Core contract documentation | Story closeout process and review gates. |
| `templates/` | Forge Core | Standard starting surfaces supplied by the Forge. |
| `examples/` | Forge Canon teaching surfaces | Demonstrations of the Forge method, not published equipment. |
| `specs/<equipment>/` | Equipment Design Bundles or Equipment Blueprints | Candidate-specific design and validation-planning records. |
| `docs/harness-capabilities.md` | Forge Canon catalog front door | Human-facing summary of structured Vanilla Harness Capability Profiles. |
| `docs/harness-capabilities/vanilla/` | Forge Canon structured profile surface | Target location for per-harness Vanilla Harness Capability Profiles. |
| At review time: `tools/validate_forge_seed.py` | Transitional live validation implementation | Split or rename under Armory/Forge Integrity Validation. |
| At review time: `tests/test_validate_forge_seed.py` | Transitional validation test suite | Follow the validation boundary split. |
| `AGENTS.md` | Agent-facing operating and routing policy | Includes Forge Conveyor behavior; relevant to Forge Equipment Core and broader Armory operation. |

## Findings

### F1: Validator Status Lock

At review time, the validator required `Status: Forge Seed` on canonical docs.
That status label conflated historical seed origin with live Canon and Core
responsibility.

Disposition: accepted. The validation boundary refactor must replace the
status lock with live classification or a status scheme that does not force
current docs to look like historical seed artifacts.

Implementation disposition: active canonical docs use live Armory Canon, Forge
Canon, and Forge Core status labels under Armory Integrity Validation.

### F2: Live Closeout Mentions Seed Validation

At review time, `docs/story-closeout.md` named Seed Validation as the rerun
target for validation changes. Current vocabulary says live repository checks
belong to Armory Integrity Validation and Forge-scoped checks belong to Forge
Integrity Validation.

Disposition: accepted. This review updates the live closeout wording where it
can do so without executing the validation refactor. The implementation story
still owns command and test renames.

Implementation disposition: live closeout now names
`tools/validate_armory_integrity.py --final-closeout`.

### F3: Threat Model Names Seed Validation Tool As Current Boundary

At review time, `docs/security/threat-model.md` described
`tools/validate_forge_seed.py` as the local validation boundary. The live
threat model should name Armory Integrity Validation tooling after the
validation boundary refactor.

Disposition: accepted as a prerequisite-story update. Keep the current threat
model accurate until the tool is renamed or split; then update the trust
boundary and attacker-controlled-input sections.

Implementation disposition: the live threat model names
`tools/validate_armory_integrity.py` and Armory Integrity Validation.

### F4: Historical Plans Preserve Old Names

Dated plans and closeout records still contain Seed-era terms and the retired
Forge Entry Bundle name.

Disposition: accepted as historical. Do not rewrite historical plans solely for
terminology cleanup. Live docs and active specs use Equipment Design Bundle.

### F5: Equipment Core Boundaries Need Operating-Model Review

The Forge Equipment Core and Armory Equipment Core boundaries depend on how
agent operating contracts are discovered, invoked, updated, and enforced.

Disposition: accepted. The Agentic Engineering Operating Model Review remains
a separate high-priority follow-up, with a checkpoint before manual refresh is
considered feature-complete.

## Required Follow-Up Work

The validation boundary refactor story owns this implementation shape:

- define the live Armory Integrity Validation command and Forge Integrity
  Validation suite;
- classify each current `tools/validate_forge_seed.py` check;
- remove or archive checks whose only purpose is proving the completed Forge
  Seed migration;
- re-home live provenance, source-disposition, route, documentation, template,
  spec, and bundle-shape checks;
- split equipment-candidate shape validation from equipment-specific behavior
  validation;
- replace the hardcoded `Status: Forge Seed` canonical-doc rule;
- rename or split `tools/validate_forge_seed.py` and
  `tests/test_validate_forge_seed.py`;
- update `docs/security/threat-model.md`, `docs/story-closeout.md`, active
  specs, tool help, JSON output, and closeout commands;
- add a deterministic check proving no transient compatibility path remains in
  live surfaces at story closeout.

The issue projection story must:

- include this review as input evidence for projected child issues;
- keep validation-boundary work as the first dependency;
- avoid projecting Manager Core implementation as independent of the live
  validation command name;
- separately track the Agentic Engineering Operating Model Review.

## Result

The domain model is coherent enough for child issue projection once the above
follow-up work is represented in the projected issue batch. The current blocker
is not further naming discussion; it is executing the validation boundary
refactor before Manager Core migration.
