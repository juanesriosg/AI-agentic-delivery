# Manifest v12 — Design First + Layered Testing

This update adds architecture/design readiness, DB → API → frontend dependency gates, programming paradigm selection, and explicit testing strategy per layer.

## New root docs

```text
DESIGN_FIRST_LAYERED_TESTING_V12.md
V12_DESIGN_LAYERED_UPDATE_REPORT.md
MANIFEST.v12.md
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

## New skills

```text
.ai/skills/design-first-sdlc.skill.md
.ai/skills/layered-testing-gates.skill.md
.ai/skills/paradigm-selection.skill.md
.ai/skills/data-model-contract.skill.md
.ai/skills/db-api-front-contract-testing.skill.md
```

## New scripts

```text
.ai/scripts/design_gate.py
.ai/scripts/layer_gate.py
.ai/scripts/generate_layered_test_matrix.py
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

## New workflow

```text
.github/workflows/agentic-design-layer-gates.yml
```

## Updated automation

```text
.ai/scripts/agentic_sdlc.py
.ai/scripts/pr_guardrails.py
.ai/automation/agentic.config.json
AGENTS.md
README.md
START_HERE.md
ONE_RESPONSIBILITY_PR_STANDARD.md
DEV_MANAGER_AGENT_POLICY.md
specs/_TEMPLATE.agentic-spec.md
specs/_TEMPLATE.agentic-spec.yml
```
