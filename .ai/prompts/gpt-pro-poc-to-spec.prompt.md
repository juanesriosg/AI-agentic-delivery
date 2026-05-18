# GPT Pro Prompt: POC → Implementation-Ready Spec → Spec Branch

You are helping an AI PM turn a stakeholder/boss POC into an implementation-ready spec for an autonomous Codex agent team.

Create a Markdown spec file that can be saved as:

```text
specs/<feature-slug>.spec.md
```

The spec must be complete enough that Codex agents can implement without guessing. It must pass:

```bash
python .ai/scripts/validate_agentic_spec.py specs/<feature-slug>.spec.md
```

## Required front matter

Use this exact front matter shape and fill every value. Do not leave placeholders.

```yaml
---
spec_id: SPEC-YYYYMMDD-<feature-slug>
spec_version: "1.0"
story_id: STORY-<feature-slug>
title: "<feature title>"
status: ready_for_agents
priority: medium
risk_level: medium
owner: "@juanesriosg"
manager: "@juanesriosg"
repo: "<github-owner>/<repo>"
source_branch: "dev/<feature-slug>"
target_branch: "main"
final_pr_base: "main"
expected_pr_strategy: source-spec-branch-final-pr
pr_strategy: source-spec-branch-final-pr
autonomy_level: L3
created_at: "YYYY-MM-DD"
updated_at: "YYYY-MM-DD"
---
```

## Required sections

Write these sections using the same headings. Include ID-style rows so the validator and agents can trace work.

```md
# <Feature title>

## Description

## Business need

## User needs and scenarios

| Scenario ID | Scenario | Expected outcome |
|---|---|---|
| US-001 | ... | ... |

## Scope

### In scope
### Out of scope
### Non-goals

## Requirements

| ID | Requirement | Priority | Acceptance signal | Owner agent |
|---|---|---|---|---|
| FR-001 | ... | must | ... | ... |
| NFR-SEC-001 | ... | must | ... | security-engineer |
| NFR-REL-001 | ... | should | ... | backend-engineer |

## Design / UX

## Architecture

## Data model

Write the data model, entities, fields, indexes, relationships, lifecycle, sensitivity, and test data strategy. If not applicable, write `Not applicable` and explain why.

## API contract

Write endpoints/events/contracts, request/response shape, errors, compatibility, auth, idempotency, and examples. If not applicable, write `Not applicable` and explain why.

## AWS / cloud / infrastructure

Write all cloud components and how they will be deployed. If any AWS component is needed, require Terraform. If not applicable, write `Not applicable` and explain why.

## Testing strategy

Include DB tests, API tests, frontend tests, integration tests, E2E tests, visual tests, accessibility tests, security tests, and local/cloud limitations as applicable.

## Layer order

State the exact order. Default for full-stack work: database → API/backend → frontend → QA → PM → final PR.

## Programming paradigm

Choose data-driven, object-oriented, event-driven, functional/procedural, or hybrid. Explain why this is the correct choice for the task.

## Files and areas to touch

| Path / pattern | Expected change | Owner agent | Required? |
|---|---|---|---|
| `...` | ... | ... | yes |

## Files not to touch without approval

| Path / pattern | Reason | Approval required from |
|---|---|---|
| `...` | ... | manager |

## Agent routing

| Agent | Needed? | Reason |
|---|---|---|
| Architecture Design Lead | yes/no | ... |
| Database Engineer | yes/no | ... |
| Backend Engineer | yes/no | ... |
| Frontend Engineer | yes/no | ... |
| QA Evidence Collector | yes | ... |
| Product Manager Acceptance | yes | ... |

## PR / task decomposition plan

| PR | Responsibility | Expected files | Depends on | Target branch |
|---|---|---|---|---|
| PR-1 | ... | `...` | none | `dev/<feature-slug>` |

## Acceptance criteria

| ID | Acceptance criterion | Type | Validated by | Evidence |
|---|---|---|---|---|
| AC-001 | ... | functional | QA Agent | ... |

## Risks and guardrails

## Clarifications

List known answers. If something is unknown, state whether it blocks implementation or allows safe progress.

## Definition of done
```

## Strict rules

- Make design the contract before code.
- Do not leave placeholders.
- Do not push a spec as `ready_for_agents` until it is complete.
- If a layer is not needed, write `Not applicable` and explain why.
- If AWS is needed, require Terraform, not manual console or raw mutating AWS CLI.
- Require QA and PM agent approval before final PR.
- Require Codex AI review before human approval.
- Keep work decomposable into one-responsibility task commits.
- The implementation branch is the same branch as the spec branch.
- The final PR should be from `dev/<feature-slug>` to `main` and should tag `@juanesriosg`.
