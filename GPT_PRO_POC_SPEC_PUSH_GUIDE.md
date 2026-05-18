# GPT Pro POC Spec Push Guide

Use this guide when GPT Pro creates the spec and pushes it to a new branch.

## Your target workflow

```text
1. Boss/stakeholder sends POC.
2. You create GitHub repo and install/index this agentic package.
3. GPT Pro creates an implementation-ready spec.
4. GPT Pro or you push that spec to a new branch.
5. GitHub detects the spec push and starts Codex in cloud mode.
6. Codex agents implement/test/review and push validated commits to the same spec branch.
7. The system opens a final PR from that spec branch to main and tags @juanesriosg.
```

## 1. Create branch

```bash
git switch -c dev/<feature-slug>
```

Example:

```bash
git switch -c dev/register-form
```

## 2. Create spec

Create:

```text
specs/<feature-slug>.spec.md
```

The top of the spec must include all required validator fields. `source_branch` is the branch GPT Pro pushed; `target_branch` / `final_pr_base` is the final PR base:

```yaml
---
spec_id: SPEC-20260515-<feature-slug>
spec_version: "1.0"
story_id: STORY-<feature-slug>
title: "<feature title>"
status: ready_for_agents
priority: medium
risk_level: medium
owner: "@juanesriosg"
manager: "@juanesriosg"
repo: "<owner/repo>"
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

Use `status: draft` until the spec passes:

```bash
python .ai/scripts/validate_agentic_spec.py specs/<feature-slug>.spec.md
```

## 3. Commit and push

```bash
git add specs/<feature-slug>.spec.md
git commit -m "spec: <feature title>"
git push -u origin dev/<feature-slug>
```

The workflow below will then detect the spec and start Codex:

```text
.github/workflows/agentic-poc-spec-to-pr.yml
```

## 4. What GPT Pro must include in the spec

A spec must be design-first and implementation-ready:

```text
- POC description and business/user need
- user scenarios with US-001 style IDs
- functional requirements with FR-001 style IDs
- non-functional requirements with NFR-* IDs
- scope, out of scope, and guardrails
- design and UX behavior
- architecture design
- data model design or explicit Not applicable
- API contract or explicit Not applicable
- cloud/Terraform design or explicit Not applicable
- expected files to touch
- files not to touch
- layer order and dependencies
- testing strategy for DB, API, frontend, integration, E2E, visual, accessibility
- acceptance criteria with AC-001 style IDs
- agent routing
- PR/commit decomposition plan with PR-1 style IDs
- risk and clarification tables
- definition of done
```

## 5. What GPT Pro must not do

```text
- Do not push draft specs as ready_for_agents.
- Do not omit data/API/cloud/frontend decisions.
- Do not leave placeholders like <feature> or {{value}}.
- Do not ask agents to guess high-risk decisions.
- Do not request raw AWS CLI resource creation.
- Do not request broad unscoped refactors.
```

## 6. Manual trigger, if needed

Default local execution:

```bash
python .ai/scripts/poc_to_pr.py \
  --branch dev/<feature-slug> \
  --spec specs/<feature-slug>.spec.md \
  --mode local
```

Dry run:

```bash
python .ai/scripts/poc_to_pr.py \
  --branch dev/<feature-slug> \
  --spec specs/<feature-slug>.spec.md \
  --mode local \
  --dry-run
```

Explicit cloud execution only when you intentionally request it:

```bash
python .ai/scripts/poc_to_pr.py \
  --allow-cloud \
  --branch dev/<feature-slug> \
  --spec specs/<feature-slug>.spec.md \
  --mode cloud
```
