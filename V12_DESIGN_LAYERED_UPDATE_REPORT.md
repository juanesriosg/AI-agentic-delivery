# v12 Update Report — Design First + Layered Testing

## Added

- Design-first spec gate.
- DB → API → frontend sequencing.
- Layer pass files consumed by later automation cycles.
- Task planning with `layer` and `depends_on` fields.
- More explicit agent responsibilities for architecture, data model, API contracts, frontend, QA, and dev-manager review.
- A layered test matrix generator.
- A GitHub workflow for design/layer gate validation.

## New scripts

```text
.ai/scripts/design_gate.py
.ai/scripts/layer_gate.py
.ai/scripts/generate_layered_test_matrix.py
```

## New agents

```text
.ai/agents/architecture-design-lead.agent.md
.ai/agents/data-model-architect.agent.md
.ai/agents/test-strategy-architect.agent.md
.ai/agents/paradigm-selection-agent.agent.md
.ai/agents/dependency-gate-qa.agent.md
.ai/agents/layer-sequencing-orchestrator.agent.md
```

## New specs/standards

```text
.ai/specs/design-first-policy.yml
.ai/specs/layer-dependency-gates.yml
.ai/specs/paradigm-selection-policy.yml
.ai/specs/test-data-strategy-policy.yml
.ai/specs/design-quality-rubric.yml
.ai/specs/integration-e2e-test-policy.yml
.ai/specs/architecture-design-template.md
.ai/specs/data-model-design-template.md
.ai/specs/layered-test-strategy-template.md
.ai/specs/task-dependency-dag.schema.yml
```

## Updated automation

The orchestrator now:

1. runs a design gate before planning implementation;
2. asks the planner to create layer-aware tasks;
3. orders tasks by design/cloud/database/API/frontend/QA/PM/release;
4. blocks API work until database layer evidence exists when the spec depends on data;
5. blocks frontend work until API layer evidence exists when the UI depends on the API;
6. runs layer gates before PR guardrails;
7. writes or requires layer pass files for the next cycle.
