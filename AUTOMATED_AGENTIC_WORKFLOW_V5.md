# Automated Agentic Workflow v5

This package adds the automation layer for your ideal workflow:

1. You use ChatGPT Pro models to create specs, test apps, analyze data, and define product intent.
2. You push a spec file to a watched branch such as `dev/register-form` or `chatgpt/export-report`.
3. The repo-level automation detects the new spec.
4. The automation asks Codex to split the spec into one-responsibility implementation tasks.
5. Each task is assigned to specialized agents: frontend, backend, database, cloud/Terraform, security, QA, PM acceptance, release, and PR documentation.
6. Each agent writes logs and evidence.
7. QA and PM gates must pass before the story is considered ready.
8. A PR is opened, tagging the AI PM / human manager, with concise evidence, screenshots when relevant, test results, rollback notes, and `agents.log`.

The automation exists in two modes:

| Mode | When | What it does |
|---|---|---|
| Local daytime | While your computer is on | Watches branches, creates worktrees, runs Codex locally, tests local app behavior, captures screenshots, opens PRs. |
| Cloud/night | While your computer is off | Runs in GitHub Actions / Codex CI, continues cloud-safe work, debugs Lambdas/API/CI failures, analyzes logs/data/spec gaps, prepares PRs and follow-up tasks. |

## Install in a repo

Copy the package into the repository root, then run:

```bash
python .ai/scripts/agentic_sdlc.py doctor
python .ai/scripts/agentic_sdlc.py scan
```

Start the daytime local loop:

```bash
python .ai/scripts/agentic_sdlc.py watch --mode local --poll-seconds 180
```

Run one pass manually:

```bash
python .ai/scripts/agentic_sdlc.py run-once --mode local --max-specs 1
```

Generate prompts without calling Codex:

```bash
python .ai/scripts/agentic_sdlc.py run-once --dry-run --max-specs 1
```

## Spec branch convention

Recommended:

```text
branch: dev/<story-slug>
file: specs/<story-slug>.spec.md
```

Example:

```text
dev/register-form
specs/register-form.spec.md
```

The implementation branch created by agents is:

```text
ai/<story-slug>/<task-slug>
```

The PR target is the source spec branch by default:

```text
ai/register-form/frontend-form-ui  ->  dev/register-form
```

## One responsibility per PR

The script asks the planning agent to split a spec into small implementation tasks. Each task must have one responsibility, for example:

```text
frontend form UI
backend registration endpoint
database migration
cloud infrastructure
security validation
QA evidence only
```

A dev-manager agent checks PR scope before the PR is opened. If a branch changes too many unrelated areas, the PR is blocked and the agent must split the work.

## Agent cycle

For every task, the automation runs this loop:

```text
Spec analysis
Task split
Specialist implementation
Self-review
Unit/component test
Integration/API test
E2E/user-flow test when applicable
Visual/accessibility QA when applicable
QA regression
PM acceptance
Dev-manager PR gate
Release readiness
PR documentation
PR creation + manager tag
```

## AWS / deployment rule

Agents must not create AWS resources manually. New AWS components must be represented as Terraform and deployed by GitHub workflows.

Allowed patterns:

```text
infra/terraform/**
terraform/**
.github/workflows/*terraform*.yml
scripts/deploy/** calling terraform, not raw resource creation
```

Blocked patterns unless explicitly approved:

```text
aws lambda create-function
aws ec2 run-instances
aws rds create-db-instance
aws dynamodb create-table
kubectl apply directly to production
manual console deployment instructions
```

## Evidence model

Runtime data is written under `.agent/`.

Reviewable PR evidence is copied to:

```text
docs/agentic-evidence/<story-id>/<task-id>/
```

Expected files:

```text
agents.log.md
qa-checklist.md
pm-checklist.md
test-evidence.md
visual-evidence.md
scale-security-architecture-review.md
pr-notification.md
```

## Cloud/night continuation

The included workflow `.github/workflows/agentic-night-cloud.yml` can run on schedule or manually. It uses the same script but runs in cloud mode:

```text
python .ai/scripts/agentic_sdlc.py --allow-cloud run-once --mode cloud --max-specs 2
```

Cloud mode avoids local-only assumptions. It focuses on tasks that can be done from the repo and cloud environment: code, tests, CI failures, Lambda/API debugging, Terraform plans, logs, static analysis, spec gap analysis, and PR preparation.
