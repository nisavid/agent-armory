# Forge Seed Source Disposition

Status: Source Retired

This ledger replaces raw source-handoff preservation after the source-bearing checkpoint. It does not preserve raw source payloads. It preserves source identity evidence, normalized source claim summaries, operator dispositions, source-bearing stamp fields, and source-retirement stamp fields without relying on chat history, host-local scratch artifacts, or Git object reachability.

## Source Manifest

Source-bearing snapshot tree id: `589bf626ffc5e9cdfffc7ee5983022adc1f7a1e2`
Allowed source list digest: `2e1198863b18b42b46b0d4661c23737ef12488f26a24d151bcd0a4847cbcbdcd`

| source_id | source_kind | original_path | git_blob_id | sha256 | normalized_payload_digest | durable_payload |
| --- | --- | --- | --- | --- | --- | --- |
| SRC001 | file | docs/metasmith/source-projection.md | 77ff23d422f33f7d6e220efe8cd406739266f466 | a97d84987af91c404bdbae3b3e05bbf9c29b6fcb07c1ca5fbd3c31767f4b079e | a97d84987af91c404bdbae3b3e05bbf9c29b6fcb07c1ca5fbd3c31767f4b079e | retired source file; digest and normalized claim summaries are preserved in this ledger |
| SRC002 | file | docs/metasmith/handoff/2026-05-02/00-metasmith-handoff-prompt.md | 4b9b50e99ac11f34a46413690615b43572d9866e | 6811ebf9ab5a31dad156075aac5c725466b98dabb5ba0bbfa3efb8c465a78b9f | 6811ebf9ab5a31dad156075aac5c725466b98dabb5ba0bbfa3efb8c465a78b9f | retired source file; digest and normalized claim summaries are preserved in this ledger |
| SRC003 | file | docs/metasmith/handoff/2026-05-02/01-executive-brief.md | 2c5967c9690c3057ec69b00ccf4bab9dab885187 | aadb4036977f9e9bbb7407c066c81eeda5d235300d70cb31f7d308306ea59849 | aadb4036977f9e9bbb7407c066c81eeda5d235300d70cb31f7d308306ea59849 | retired source file; digest and normalized claim summaries are preserved in this ledger |
| SRC004 | file | docs/metasmith/handoff/2026-05-02/02-ubiquitous-language.md | f1a3aabf8892b47f207c9fc97069802638ecfd55 | 950fc27fb947a5be266e0433a6619f9d47600b9571dfaa9f0f4a6c8d04188688 | 950fc27fb947a5be266e0433a6619f9d47600b9571dfaa9f0f4a6c8d04188688 | retired source file; digest and normalized claim summaries are preserved in this ledger |
| SRC005 | file | docs/metasmith/handoff/2026-05-02/03-evidence-and-source-map.md | a453abfc4b2c03b366cdf8a21f4d73cb4014507e | 42a578887b6661f6057727a297f91cdb174566b43a8cd95a7b87ac9d8fea244a | 42a578887b6661f6057727a297f91cdb174566b43a8cd95a7b87ac9d8fea244a | retired source file; digest and normalized claim summaries are preserved in this ledger |
| SRC006 | file | docs/metasmith/handoff/2026-05-02/04-framework-architecture.md | 2de5b278651dd912fca4d1b711a192d260478d46 | a4f70e2deb01a142cd47066dd0df96f900825d8a9d52ed7563ff214668ff09db | a4f70e2deb01a142cd47066dd0df96f900825d8a9d52ed7563ff214668ff09db | retired source file; digest and normalized claim summaries are preserved in this ledger |
| SRC007 | file | docs/metasmith/handoff/2026-05-02/05-decision-method-and-runbook.md | e8077a86449334841b7690f5a7ec0201aa8c038e | 7a28cd372beda57bfca733a8f6fe7d091556666c2eb8a14e25ffe23517f08acd | 7a28cd372beda57bfca733a8f6fe7d091556666c2eb8a14e25ffe23517f08acd | retired source file; digest and normalized claim summaries are preserved in this ledger |
| SRC008 | file | docs/metasmith/handoff/2026-05-02/06-harness-capability-catalog.md | 90fdd4e7d2149d62d5302d4a15c9ca344a438555 | 782eedb989a7f11dcfd6c8c5575037a790ca91e3ba82674ed6bcb01d858bcc25 | 782eedb989a7f11dcfd6c8c5575037a790ca91e3ba82674ed6bcb01d858bcc25 | retired source file; digest and normalized claim summaries are preserved in this ledger |
| SRC009 | file | docs/metasmith/handoff/2026-05-02/07-equipment-templates-and-examples.md | 317d781489952154cf30b4143aeb31c276ffb87e | 8776c9779cd22e7e0286a38a6f208f3f349dc8ab56dac26b647586456cb78ebf | 8776c9779cd22e7e0286a38a6f208f3f349dc8ab56dac26b647586456cb78ebf | retired source file; digest and normalized claim summaries are preserved in this ledger |
| SRC010 | file | docs/metasmith/handoff/2026-05-02/08-initial-smith-task-specs.md | b7440362c70c05610d11dd815e607994a24a8e06 | 2ddcac2e20fa82df57b81f2eb7166e3e2c770d22b34540803b548ec1bd766424 | 2ddcac2e20fa82df57b81f2eb7166e3e2c770d22b34540803b548ec1bd766424 | retired source file; digest and normalized claim summaries are preserved in this ledger |
| SRC011 | file | docs/metasmith/handoff/2026-05-02/09-repository-seed-plan.md | 3e6ca7284ec205a4db5eacfe91814b6e681629e0 | fc3c2482e41adba3666c8beebd9fdbdf0acf243b8912c4d934e49ca6581464cd | fc3c2482e41adba3666c8beebd9fdbdf0acf243b8912c4d934e49ca6581464cd | retired source file; digest and normalized claim summaries are preserved in this ledger |
| SRC012 | file | docs/metasmith/handoff/2026-05-02/10-gap-resolution-and-design-notes.md | c47b2c25cf5696d80e77afd357f19c4d0554f05a | f2a1ebe60caff4e25a728283101d971c4fa04faa30be9929957cf7157a546449 | f2a1ebe60caff4e25a728283101d971c4fa04faa30be9929957cf7157a546449 | retired source file; digest and normalized claim summaries are preserved in this ledger |
| SRC013 | file | docs/metasmith/handoff/2026-05-02/AGENTS.md | 52f2592cdcf1b13b8a77f668395439adf81c047b | 2d9928ff4247bbfef688a4802824d36a040f1c836af0d4d6184281a9e7197828 | 2d9928ff4247bbfef688a4802824d36a040f1c836af0d4d6184281a9e7197828 | retired source file; digest and normalized claim summaries are preserved in this ledger |
| SRC014 | file | docs/metasmith/handoff/2026-05-02/README.md | 4f29620ce271acb992e3e9cba985329f64cce4ef | 76077edd8de744f6fd328f03e60cdbf926a8a44fbe423d92afc075482aac0069 | 76077edd8de744f6fd328f03e60cdbf926a8a44fbe423d92afc075482aac0069 | retired source file; digest and normalized claim summaries are preserved in this ledger |
| SRC015 | file | docs/metasmith/handoff/2026-05-02/harness-capabilities.seed.toml | 88e29e6f889e5499f50930f06f6a567fa10ba9f3 | 4b866edb7d0713f8d81829eb360757486b8c7d7d6b2f6b210ab40564ae5cc400 | 4b866edb7d0713f8d81829eb360757486b8c7d7d6b2f6b210ab40564ae5cc400 | retired source file; digest and normalized claim summaries are preserved in this ledger |
| SRC016 | file | docs/metasmith/handoff/2026-05-02/manifest.json | abb7699a7244babeea509d8e274ae1489200c0b7 | 88ffa8503f40c1203da1ba0da4e1cd291bd5bec589d0980e2a600ce9ae264e2b | 88ffa8503f40c1203da1ba0da4e1cd291bd5bec589d0980e2a600ce9ae264e2b | retired source file; digest and normalized claim summaries are preserved in this ledger |
| SRC017 | file | docs/metasmith/handoff/2026-05-03-agentic-engineering-workflow-equipment.md | 896d729865f36d880cc7b71d961e69096c3bb745 | 6d7cc59c0c43061e754a831374ca3f1d24b137fbe526b16fd57c9e3d1ad7bca8 | 6d7cc59c0c43061e754a831374ca3f1d24b137fbe526b16fd57c9e3d1ad7bca8 | retired source file; digest and normalized claim summaries are preserved in this ledger |
| SRC018 | file | docs/metasmith/handoff/2026-05-03-agentic-engineering-workflow-seed-closeout-addendum.md | 028501d966e5989d14274a4046d2bbc4a9bebcc6 | 0434fb94524b41499b630d479b97481a7a2682cfcbaec83c731bcca8edd5939b | 0434fb94524b41499b630d479b97481a7a2682cfcbaec83c731bcca8edd5939b | retired source file; digest and normalized claim summaries are preserved in this ledger |
| SRC019 | file | docs/metasmith/handoff/2026-05-03-ephemeral-workflow-opportunity-capture.md | d3b54c42ef3708851d2718f48fa9243e47ad1a41 | 4998e2d9f53dc97e0e2607249794426ba54a9e0b16c125acdb222ec4181758e4 | 4998e2d9f53dc97e0e2607249794426ba54a9e0b16c125acdb222ec4181758e4 | retired source file; digest and normalized claim summaries are preserved in this ledger |
| SYN001 | synthetic | tools/validate_framework_seed.py | 387528b54440abe560cd4d8d8e859e05df620347 | d1369a5d1a1c77524dbf4f8c5006b348de36d61e0617340e5c58037758329ad3 | 84909b97e7c53567ae1a02750da0e2ae33550b0b2544c01ee849a636a9359466 | ACCEPTED_SOURCE_REQUIREMENTS and source-projection validation expectations from tools/validate_framework_seed.py before Forge route migration. |

## Disposition Items

| item_id | source_id | coverage_status | challenge_status | challenge_operator_confirmation_required | arbitration_required | disposition | operator_decision | evidence_target | normalized_claim_summary |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H001 | SRC002 | adequately_captured | unchallenged | false | false | kept_current |  | docs/prd/forge-seed.md | Produce the Forge Seed as canonical docs, templates, examples, specs, and validation surfaces. |
| H002 | SRC002 | adequately_captured | unchallenged | false | false | kept_current |  | CONTEXT.md | Establish the core Forge vocabulary. |
| H003 | SRC002 | adequately_captured | unchallenged | false | false | kept_current |  | docs/agent-equipment-forge.md | Preserve least cognitive privilege as the Forge design rule. |
| H004 | SRC002 | adequately_captured | unchallenged | false | false | kept_current |  | docs/prd/forge-seed.md | Create the Forge Seed repository surfaces without treating the seed structure as final project law. |
| H005 | SRC002 | adequately_captured | unchallenged | false | false | kept_current |  | CONTEXT.md | Define Forge terms and relationships for future Smiths and Forgewrights. |
| H006 | SRC002 | adequately_captured | unchallenged | false | false | kept_current |  | docs/evidence-taxonomy.md | Record source and evidence rules for Forge claims and harness facts. |
| H007 | SRC002 | adequately_captured | unchallenged | false | false | kept_current |  | docs/agent-equipment-forge.md | Describe Forge components and their responsibilities. |
| H008 | SRC002 | adequately_captured | unchallenged | false | false | kept_current |  | docs/interface-decision-guide.md | Provide the interface decision method and runbook guidance. |
| H009 | SRC002 | adequately_captured | unchallenged | false | false | kept_current |  | docs/harness-capabilities.md | Refresh and publish the canonical harness capability catalog. |
| H010 | SRC002 | adequately_captured | unchallenged | false | false | kept_current |  | templates/ | Ship seed templates and annotated Forge Examples. |
| H011 | SRC002 | adequately_captured | unchallenged | false | false | kept_current |  | specs/agent-ops.md | Create downstream specs for the initial Smith tasks. |
| H012 | SRC002 | adequately_captured | unchallenged | false | false | kept_current |  | tools/validate_forge_seed.py | Validate source disposition, seed surfaces, examples, Blueprints, and issue projection. |
| H052 | SRC002 | adequately_captured | unchallenged | false | false | kept_current |  | docs/prd/forge-seed.md | Preserve standard-library validation and non-production seed boundaries. |
| H053 | SRC002 | adequately_captured | unchallenged | false | false | kept_current |  | docs/closeout/forge-seed-documentation.md | Record final implementation, validation, issue projection, and closeout summaries. |
| H013 | SRC003 | adequately_captured | unchallenged | false | false | kept_current |  | docs/agent-equipment-forge.md | Explain why the Agent Armory needs a Forge instead of ad hoc equipment. |
| H014 | SRC003 | adequately_captured | unchallenged | false | false | kept_current |  | docs/agent-equipment-forge.md | Preserve the capability, interface, harness, and context decomposition. |
| H015 | SRC003 | adequately_captured | unchallenged | false | false | kept_current |  | docs/forgewright-runbook.md | Define Forgewright outputs and seed production responsibilities. |
| H016 | SRC004 | adequately_captured | unchallenged | false | false | kept_current |  | CONTEXT.md | Define the Agent Armory and Agent Equipment vocabulary. |
| H017 | SRC004 | adequately_captured | unchallenged | false | false | kept_current |  | CONTEXT.md | Preserve relationships between capabilities, equipment, harnesses, and Agent Profiles. |
| H018 | SRC005 | adequately_captured | unchallenged | false | false | kept_current |  | docs/evidence-taxonomy.md | Define evidence categories for project and harness claims. |
| H019 | SRC005 | adequately_captured | unchallenged | false | false | kept_current |  | docs/evidence-taxonomy.md | Define source hygiene and provenance rules. |
| H020 | SRC006 | adequately_captured | unchallenged | false | false | kept_current |  | docs/agent-equipment-forge.md | Describe responsibilities for capability cards, decisions, components, and specs. |
| H021 | SRC006 | adequately_captured | unchallenged | false | false | kept_current |  | docs/agent-equipment-forge.md | Define context budget and routing expectations. |
| H022 | SRC006 | adequately_captured | unchallenged | false | false | kept_current |  | docs/security-and-control.md | Define security and control requirements for equipment surfaces. |
| H023 | SRC006 | adequately_captured | unchallenged | false | false | kept_current |  | docs/forgewright-runbook.md | Define maintenance and refresh expectations for Forge facts. |
| H024 | SRC007 | adequately_captured | unchallenged | false | false | kept_current |  | docs/interface-decision-guide.md | Encode least cognitive privilege in the decision method. |
| H025 | SRC007 | adequately_captured | unchallenged | false | false | kept_current |  | docs/interface-decision-guide.md | Provide placement guidance for equipment interfaces. |
| H026 | SRC007 | adequately_captured | unchallenged | false | false | kept_current |  | docs/interface-decision-guide.md | Provide the interface decision tree. |
| H027 | SRC007 | adequately_captured | unchallenged | false | false | kept_current |  | docs/smith-runbook.md | Provide the Smith capability creation workflow. |
| H028 | SRC007 | adequately_captured | unchallenged | false | false | kept_current |  | docs/interface-decision-guide.md | Preserve Forge anti-patterns for future reviewers. |
| H029 | SRC008 | adequately_captured | unchallenged | false | false | kept_current |  | docs/harness-capabilities.md | Publish the refreshed harness capability summary matrix. |
| H030 | SRC008 | adequately_captured | unchallenged | false | false | kept_current |  | specs/periodic-actions.md | Preserve the Periodic Actions projection order. |
| H031 | SRC008 | adequately_captured | unchallenged | false | false | kept_current |  | specs/harness-capability-refresh.md | Define refresh cadence and evidence requirements for harness facts. |
| H032 | SRC009 | adequately_captured | unchallenged | false | false | kept_current |  | templates/capability-card.md | Provide the capability card template. |
| H033 | SRC009 | adequately_captured | unchallenged | false | false | kept_current |  | templates/interface-decision-record.md | Provide the interface decision record template. |
| H034 | SRC009 | adequately_captured | unchallenged | false | false | kept_current |  | templates/skill/README.md | Provide the skill reference template. |
| H035 | SRC009 | adequately_captured | unchallenged | false | false | kept_current |  | templates/skill/SKILL.md | Provide the skill body template. |
| H036 | SRC009 | adequately_captured | unchallenged | false | false | kept_current |  | templates/hook/README.md | Provide the hook template. |
| H037 | SRC009 | adequately_captured | unchallenged | false | false | kept_current |  | templates/agents/README.md | Provide the Agent Profile template. |
| H038 | SRC009 | adequately_captured | unchallenged | false | false | kept_current |  | templates/plugin/README.md | Provide the Harness Plugin manifest template. |
| H039 | SRC009 | adequately_captured | unchallenged | false | false | kept_current |  | templates/script/README.md | Provide the deterministic script template. |
| H040 | SRC009 | adequately_captured | unchallenged | false | false | kept_current |  | examples/pr-review/capability-card.md | Provide an annotated PR review Forge Example. |
| H041 | SRC009 | adequately_captured | unchallenged | false | false | kept_current |  | templates/mcp/README.md | Provide the MCP/tool definition template. |
| H042 | SRC009 | adequately_captured | unchallenged | false | false | kept_current |  | templates/config/README.md | Provide the config template. |
| H043 | SRC009 | adequately_captured | unchallenged | false | false | kept_current |  | examples/docs-research/capability-card.md | Provide an annotated documentation research Forge Example. |
| H044 | SRC009 | adequately_captured | unchallenged | false | false | kept_current |  | examples/observability-investigation/capability-card.md | Provide an annotated observability investigation Forge Example. |
| H045 | SRC010 | adequately_captured | unchallenged | false | false | kept_current |  | specs/agent-ops.md | Specify Agent Ops without implementing it in the Seed. |
| H046 | SRC010 | adequately_captured | unchallenged | false | false | kept_current |  | specs/periodic-actions.md | Specify Periodic Actions without implementing it in the Seed. |
| H047 | SRC010 | adequately_captured | unchallenged | false | false | kept_current |  | specs/harness-capability-refresh.md | Specify Harness Capability Refresh without implementing it in the Seed. |
| H048 | SRC011 | adequately_captured | unchallenged | false | false | kept_current |  | docs/plans/2026-05-03-forge-seed.md | Project the proposed seed structure into the reviewed implementation plan. |
| H049 | SRC011 | adequately_captured | unchallenged | false | false | kept_current |  | README.md | Expose the Forge Tour in the README. |
| H050 | SRC012 | adequately_captured | unchallenged | false | false | kept_current |  | docs/forgewright-runbook.md | Preserve accepted corrections from the handoff gap analysis. |
| H051 | SRC012 | adequately_captured | unchallenged | false | false | kept_current |  | docs/agent-equipment-forge.md | Preserve unresolved uncertainties without overstating Seed precedent. |
| H054 | SRC015 | adequately_captured | unchallenged | false | false | kept_current |  | docs/harness-capabilities.toml | Project the structured Codex harness seed into the refreshed catalog. |
| F001 | SRC017 | intentionally_deferred | resolved | true | true | deferred | Operator requested post-Seed follow-up capture. | docs/follow-ups/portable-agentic-engineering-workflow-equipment.md | Portable workflow equipment reflections and post-Seed capture window. |
| F002 | SRC018 | intentionally_deferred | resolved | true | true | deferred | Operator requested post-Seed follow-up capture. | docs/closeout/forge-seed-workflow-lessons.md | Forge Seed closeout lessons remain captured through PR and merge lifecycle. |
| F003 | SRC019 | intentionally_deferred | resolved | true | true | deferred | Operator requested post-Seed follow-up capture. | docs/follow-ups/ephemeral-workflow-opportunity-capture.md | Ephemeral workflow opportunities need a durable capture path. |
| F004 | SRC018 | intentionally_deferred | resolved | true | true | deferred | Operator requested post-Seed follow-up capture. | docs/follow-ups/side-thread-hand-back-workflow.md | Side-thread hand-back workflow is deferred to post-Seed design. |

## Challenge Lineage

No unresolved challenge enters source retirement. Rows marked `resolved` carry operator-directed post-Seed deferment decisions. Rows marked `unchallenged` are retained as disposition coverage already represented by current Forge Seed surfaces.

## Source-Bearing Stamp

source_bearing_snapshot_tree_id: 589bf626ffc5e9cdfffc7ee5983022adc1f7a1e2
source_bearing_stamp_id: source-bearing-2026-05-04
source_manifest_digest: 7ebb526ad69baa2254052deccf3ad9f236b3c785124842329d6d4e2a000cfbb5
source_disposition_digest: 5ac8403d95d2bc971bbbd899a94296cd6286e427e728b09e34cd765df5e2e200
source_bearing_result: passed

## Final Source-Retired Stamp

stamp_target: placeholder-normalized canonical tree
canonical_tree_digest: be6d37b26b6a23fae4cec325d22dc9366abc58ab24aa6af9e07e00dc9f2aaea7
source_retired: true
timestamp: 2026-05-04T13:27:03Z
