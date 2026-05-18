# Spec File Convention for ChatGPT-Generated Specs

Specs created with ChatGPT/pro models should be written so an autonomous agent can implement and test them without guessing.

Use this location by default:

```text
specs/<feature-or-epic>.spec.md
```

## Required format

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
