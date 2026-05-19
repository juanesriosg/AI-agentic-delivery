# GPT Pro Prompt: POC → Implementation-Ready Spec → Spec Branch

You are helping an AI PM turn a stakeholder/boss POC into an implementation-ready spec for an autonomous Codex agent team.

Create a PRD/TRD package, not a vague single-file spec. Save it as:

```text
specs/<feature-slug>/prd.md
specs/<feature-slug>/implementation-plan.md
specs/<feature-slug>/trds/trd-<task-id>-<short-slug>.md
specs/<feature-slug>/tasks/tasks-trd-<task-id>-<short-slug>.md
```

The spec must be complete enough that Codex agents can implement without guessing. It must pass:

```bash
python .ai/scripts/validate_agentic_spec.py specs/<feature-slug>/prd.md specs/<feature-slug>/implementation-plan.md specs/<feature-slug>/trds/trd-<task-id>-<short-slug>.md specs/<feature-slug>/tasks/tasks-trd-<task-id>-<short-slug>.md
```

## Templates to follow

Use these templates exactly as structure guides:

```text
specs/_TEMPLATE.prd.md
specs/_TEMPLATE.implementation-plan.md
specs/_TEMPLATE.trd.md
specs/_TEMPLATE.task-list.md
```

## Required front matter

Use this exact front matter shape and fill every value. Do not leave placeholders.

```yaml
---
spec_id: SPEC-YYYYMMDD-<feature-slug>
story_id: STORY-<feature-slug>
title: "<feature title>"
status: draft
doc_type: prd | implementation_plan | trd | task_list
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

## Required package documents

1. `prd.md`: product vision, users, use cases, functional requirements, acceptance criteria, architecture/data, product rules, open questions, assumptions, blocked items, and change log.
2. `implementation-plan.md`: short PRD understanding, questions, current execution priority, phase tables with task IDs, dependencies, deliverables, and traceability.
3. `trds/trd-*.md`: one task-level implementation contract per implementation-plan task or tight task cluster.
4. `tasks/tasks-trd-*.md`: executable task list with relevant files, acceptance coverage, sub-tasks, validation, and evidence.

Set `status: ready_for_agents` only on the most granular document that should start work. Usually that is a task list.

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
