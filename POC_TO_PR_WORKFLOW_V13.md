# v14 correction to this workflow

Step 7 is now: Codex runs the agentic SDLC in **local mode by default** using `gpt-5.5` with `model_reasoning_effort=xhigh`. Cloud mode runs only when explicitly requested.

# POC → Spec Branch → Codex Agents → Final PR Workflow v13

This is the expected workflow for a new project or POC:

```text
1. Boss/stakeholder sends a POC or idea.
2. AI PM creates a GitHub repository and installs this agentic package.
3. AI PM indexes/loads the repo context into GPT Pro / ChatGPT.
4. GPT Pro creates a design-first spec using the repo template.
5. GPT Pro or the AI PM pushes the spec to a new spec branch.
6. GitHub detects the new spec file.
7. Codex runs the agentic SDLC in cloud mode.
8. Agents read the spec, split work, implement DB → API → frontend in order.
9. Agents push validated task commits to the same branch where the spec lives.
10. Agents create a final PR from the spec branch to `main`, tagging the AI PM.
11. Codex AI PR review runs before human approval.
12. AI PM reviews code, evidence, screenshots, tests, and approves or requests changes.
```

This workflow uses the source spec branch as the integration branch. That means the branch created by GPT Pro is not just a documentation branch; it becomes the working branch for the implementation.

## Branch example

```text
main
  ↑ final PR to main, tags @juanesriosg

dev/register-form
  ├── specs/register-form.spec.md
  ├── database/data-model changes
  ├── API/backend changes
  ├── frontend changes
  └── docs/agentic-evidence/**
```

## Why source-spec-branch mode exists

Earlier versions of this package created task branches and task PRs back to the spec branch. That is useful for large teams, but it creates extra review objects.

For your desired workflow, the default is now:

```text
Spec branch = integration branch
Task commits = pushed to the spec branch
Final PR = spec branch → main
```

The agents still preserve one responsibility per task by creating one-responsibility commits and evidence sections. The final PR is the human review object.

## Required files in the spec branch

A spec branch should contain at least one ready spec file:

```text
specs/<feature>.spec.md
```

The spec must include:

```yaml
status: ready_for_agents
```

Draft specs do not trigger implementation.

## GitHub workflow

The automatic workflow is:

```text
.github/workflows/agentic-poc-spec-to-pr.yml
```

It triggers on pushes to:

```text
dev/**
spec/**
chatgpt/**
ai-spec/**
feature/spec/**
```

There is intentionally no `paths:` filter on this workflow. It runs on any push to watched spec/dev branches, then the Python runner decides whether there is a ready spec to process. This is important because agents push implementation commits, layer-gate evidence, and QA/PM evidence back to the same spec branch; those pushes must trigger the next cycle even when the spec file itself did not change.


## Continuation after agent commits

Because the spec branch is the implementation branch, the workflow must continue after agent commits. v13 uses two mechanisms:

```text
1. On every push to a watched branch, scan the branch for ready specs if no spec file changed.
2. Commit task completion markers under docs/agentic-evidence/<spec-id>/<task-id>/task-completed.md so completed DB/API/frontend tasks are not repeated on the next runner.
```

This supports the real cycle:

```text
DB task passes and pushes evidence
  ↓
workflow runs again
  ↓
API task sees DB gate and starts
  ↓
API passes and pushes evidence
  ↓
workflow runs again
  ↓
frontend task sees API gate and starts
```

## Final PR behavior

The workflow creates a final PR from:

```text
dev/<feature>
```

to:

```text
main
```

The PR body includes:

```text
- manager mention
- source spec
- tasks completed
- QA evidence paths
- PM evidence paths
- test evidence paths
- layer gates
- Codex AI review requirement
- rollback guidance
```

## Manager review expectation

The AI PM reviews only after:

```text
- design gate passed
- DB layer passed when applicable
- API layer passed when applicable
- frontend/E2E layer passed when applicable
- QA agent passed
- PM agent passed
- Dev-manager agent passed
- branch conflict guard passed
- Codex AI PR review passed
```

## Cloud mode expectation

Codex cloud mode should do everything that can be done without local-only dependencies:

```text
- read specs
- improve missing design details if safe
- implement code
- run unit tests
- run integration tests available in CI
- run Terraform fmt/validate/plan if configured
- review logs if credentials are configured
- generate missing tests
- detect bugs
- produce evidence
- create the final PR
```

If local-only UI or database access is required, the agent must not fake the result. It should mark the gap clearly and continue cloud-safe work.

## AWS policy

All new AWS components must be represented as code, preferably Terraform in this package. AWS-related changes should follow Well-Architected mechanisms: operations as code, small reversible changes, security, reliability, performance, cost awareness, sustainability, and continuous improvement.


## v14 local-first Codex policy

Agentic SDLC now defaults to local mode with Codex `gpt-5.5` and `model_reasoning_effort=xhigh`. Cloud mode is blocked unless explicitly requested with `--allow-cloud` or `AGENTIC_EXPLICIT_CLOUD=true`. See `LOCAL_FIRST_CODEX_RUNTIME_V14.md`.
