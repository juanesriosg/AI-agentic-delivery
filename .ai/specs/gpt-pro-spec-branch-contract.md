# GPT Pro Spec Branch Contract

A branch created by GPT Pro is valid for autonomous implementation only when it follows this contract.

## Branch naming

Allowed:

```text
dev/<feature>
spec/<feature>
chatgpt/<feature>
ai-spec/<feature>
feature/spec/<feature>
```

Recommended:

```text
dev/<feature>
```

## Spec path

Recommended:

```text
specs/<feature>.spec.md
```

## Required front matter

The spec must include all of these fields. `target_branch` and `final_pr_base` point to the human-review PR base, usually `main`.

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
repo: "<owner>/<repo>"
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

## Required behavior

When this branch is pushed:

```text
1. GitHub workflow detects the spec.
2. Codex agentic workflow starts.
3. Agents validate the design.
4. Agents implement validated task commits on this same branch.
5. Agents push to the same branch that contains the spec.
6. Agents create a final PR from this branch to main.
7. PR tags @juanesriosg.
8. Codex AI review is requested before human approval.
```

## Status values

Allowed to run:

```text
ready_for_agents
implementation_ready
approved
ready
```

Blocked:

```text
draft
needs_clarification
blocked
on_hold
paused
archived
```

## Minimum spec quality

The spec must make these decisions explicit:

```text
- description and business need
- US-001 style user scenarios
- FR-001 / NFR-* style requirements
- design / UX
- architecture
- data model or explicit Not applicable
- API contract or explicit Not applicable
- cloud/AWS/Terraform components or explicit Not applicable
- files to touch
- files not to touch
- layer order
- testing strategy
- AC-001 style acceptance criteria
- agent routing
- PR/task decomposition plan with PR-1 style IDs
- risks and guardrails
- clarifications
- definition of done
```

If a decision does not apply, write `Not applicable` and explain why.
