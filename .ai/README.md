# .ai Directory

This directory contains the operating model for autonomous coding agents.

## Contents

```text
agents/       Role definitions for each agent type
skills/       Reusable skills agents must apply
specs/        Schemas, policies, checklists, workflows, rubrics
scripts/      Guardrail scripts
examples/     Example tasks, epics, PRs, and notifications
```

## How to use

Each repo should contain:

```text
AGENTS.md
.ai/specs/repo-onboarding-checklist.md
.ai/specs/ownership-boundaries.yml
.ai/specs/autonomy-levels.yml
.ai/specs/restricted-operations.yml
.github/PULL_REQUEST_TEMPLATE.md
.github/workflows/agent-guardrails.yml
```

The manager should maintain:

- A project board.
- A task queue with `ai:ready` labels.
- Clear epic/task acceptance criteria.
- Repo owner and reviewer mappings.
- Quality gates in CI.
