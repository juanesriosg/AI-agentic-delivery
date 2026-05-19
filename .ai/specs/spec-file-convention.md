# Spec File Convention for ChatGPT-Generated Specs

Specs created with ChatGPT/pro models should be written so an autonomous agent can implement and test them without guessing.

## Preferred PRD/TRD package

Use the PRD/TRD/task-list package by default for real product work:

```text
specs/<story-or-feature>/
  prd.md
  implementation-plan.md
  trds/
    trd-<task-id>-<short-slug>.md
  tasks/
    tasks-trd-<task-id>-<short-slug>.md
```

Templates:

```text
specs/_TEMPLATE.prd.md
specs/_TEMPLATE.implementation-plan.md
specs/_TEMPLATE.trd.md
specs/_TEMPLATE.task-list.md
```

Every file should include `doc_type: prd | implementation_plan | trd | task_list`.

Only the most granular document that should start agent work should use:

```yaml
status: ready_for_agents
```

## Legacy single-file format

The older single-file agentic spec remains supported for small changes.

Use this location:

```text
specs/<feature-or-epic>.spec.md
```

## Required legacy format

```md
# Feature Spec: <short name>

Spec ID: SPEC-YYYYMMDD-short-slug
Owner: <manager or repo owner>
Source branch: dev/<feature>
Target PR branch: dev/<feature>
Autonomy: L3
Risk: low | medium | high

## Business goal
What user, stakeholder, or business outcome this work supports.

## User / stakeholder context
Who needs this and what problem they have.

## Technical goal
What should change in the code/system.

## Scope
What is included.

## Non-goals / out of scope
What the agent must not do.

## Acceptance criteria
- AC-001: Observable, testable behavior.
- AC-002: Observable, testable behavior.
- AC-003: Observable, testable behavior.

## Constraints
- Do not change ...
- Preserve ...
- Use ...

## Data, security, and ownership
- Data touched:
- Auth/permissions impact:
- Repo owner approval needed:
- Compliance concerns:

## Architecture notes
Expected boundaries, patterns, or tradeoffs.

## Test expectations
- Unit:
- Component:
- Integration:
- Contract:
- E2E:
- Dev/manual:
- QA:
- Regression:

## Deployment expectations
- Dev deployment:
- QA deployment:
- Production deployment:
- Rollback:

## Clarifications known upfront
Questions or decisions already identified.
```

## Good acceptance criteria

Good:

```md
- AC-001: Given an authenticated user with role `admin`, when they request `/reports/export`, then the API returns a CSV with columns `id`, `created_at`, and `status` within 5 seconds for 10,000 rows.
```

Weak:

```md
- Make export better and scalable.
```

## Agent interpretation rules

If the spec contains weak or ambiguous acceptance criteria, the agent must ask focused clarification questions. The agent must still continue safe progress such as repo discovery, existing behavior tests, fixtures, and low-risk characterization work.

For PRD/TRD packages, agents must read `.ai/specs/spec-package-convention.md` and use the source-of-truth order `PRD -> Implementation Plan -> TRD -> Task List`.
