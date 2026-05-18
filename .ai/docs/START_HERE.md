# v14 start here update

Use local mode by default: `python .ai/scripts/agentic_sdlc.py watch --mode local --poll-seconds 180`. Codex runs with `gpt-5.5` and `model_reasoning_effort=xhigh`. Cloud runs are manual/explicit only. See `.ai/docs/reference/LOCAL_FIRST_CODEX_RUNTIME_V14.md`.

# v8 audited/fixed package

Start with `.ai/docs/reports/AUDIT_AND_FIX_REPORT.v8.md` and `.ai/docs/manifests/MANIFEST.v8.md`. This release fixes spec detection, copied-template blocking, scan validation reporting, fallback task routing, local/offline branch behavior, PR guardrails, and AWS/Terraform guardrails.

---

# Start Here — v7 Corrected Workflow

Use this package when you want the repo to detect completed specs, route work through specialized agents, test through QA/PM/dev-manager gates, and create concise one-responsibility PRs for human review.

## Minimum setup

```bash
python .ai/scripts/agentic_sdlc.py doctor
python .ai/scripts/validate_agentic_spec.py .ai/examples/example-completed-generic-spec.md --format markdown
python .ai/scripts/agentic_sdlc.py --dry-run scan
```

## Start local daytime automation

```bash
python .ai/scripts/agentic_sdlc.py watch --mode local --poll-seconds 180
```

## Spec readiness rule

Reusable templates are `draft`. Real specs must be complete and set:

```yaml
status: ready_for_agents
```

The orchestrator validates the spec before coding. If placeholders remain, it skips implementation and writes a validation report under `.agent/state/spec-validation/`.

# v5 Automated Repo-Level Agentic SDLC

This version adds the automation you requested: a Python CLI that runs at repo level, detects new specs in watched branches, calls Codex/local/cloud agents in SDLC order, creates one-responsibility PRs, writes `agents.log`, enforces QA/PM/dev-manager gates, and supports night cloud continuation.

Start with these v5 files:

- `.ai/docs/reference/AUTOMATED_AGENTIC_WORKFLOW_V5.md`
- `.ai/docs/reference/MORNING_TO_NIGHT_WORKFLOW.md`
- `.ai/docs/reference/ONE_RESPONSIBILITY_PR_STANDARD.md`
- `.ai/docs/reference/DEV_MANAGER_AGENT_POLICY.md`
- `.ai/docs/reference/TERRAFORM_DEPLOYMENT_STANDARD.md`
- `.ai/docs/reference/CLOUD_CONTINUATION_GUIDE.md`
- `.ai/automation/agentic.config.json`
- `.ai/scripts/agentic_sdlc.py`
- `.github/workflows/agentic-spec-autostart.yml`
- `.github/workflows/agentic-night-cloud.yml`
- `.github/workflows/agentic-pr-guardrails.yml`
- `.github/workflows/agentic-terraform-plan.yml`
- `.github/workflows/agentic-terraform-apply.yml`

Minimum v5 commands:

```bash
python .ai/scripts/agentic_sdlc.py doctor
python .ai/scripts/agentic_sdlc.py scan
python .ai/scripts/agentic_sdlc.py run-once --dry-run --max-specs 1
python .ai/scripts/agentic_sdlc.py watch --mode local --poll-seconds 180
```

Recommended daily use:

```text
8:00 AM: start local loop
Daytime: write specs with ChatGPT Pro and push to dev/spec branches
Agents: create small PRs while you work with users/stakeholders
Night: GitHub/Codex cloud workflow continues cloud-safe work
Next morning: review PRs and agent evidence
```

---

# v4 Agile Agent Ecosystem Update

This package now includes a full specialized-agent software delivery lifecycle with product, design, frontend, backend, cloud, QA, PM review, release, visual evidence, agent-to-agent feedback, and persistent `agents.log` artifacts.

Start with these v4 files:

- `.ai/docs/reference/AGENTIC_SDLC_V4.md`
- `.ai/docs/reference/AGILE_AGENT_ECOSYSTEM.md`
- `.ai/docs/reference/VISUAL_QA_WORKFLOW.md`
- `.ai/docs/reference/AGENT_FEEDBACK_LOOP.md`
- `.ai/specs/story-lifecycle-v4.yml`
- `.ai/specs/approval-gates-v4.yml`
- `.ai/specs/specialist-agent-routing.yml`
- `.ai/specs/done-v4.yml`
- `.github/workflows/agent-agile-story-orchestration.yml`
- `.github/workflows/agent-stage-gates.yml`
- `.github/workflows/agent-visual-qa.yml`

---

# Start Here

To use this kit:

1. Copy `AGENTS.md`, `.ai/`, and `.github/` into a repo.
2. Fill `.ai/specs/repo-onboarding-checklist.md`.
3. Customize `.ai/specs/ownership-boundaries.yml`.
4. Customize `.ai/specs/restricted-operations.yml`.
5. Customize `.github/CODEOWNERS.example` and rename to `.github/CODEOWNERS`.
6. Add labels from `.ai/docs/README.md`.
7. Create a project board with lanes from `.ai/specs/board-lanes.md`.
8. Use `.ai/specs/manager-command-prompts.md` to assign work.

Minimum viable setup:

```text
AGENTS.md
.github/PULL_REQUEST_TEMPLATE.md
.github/workflows/agent-guardrails.yml
.ai/specs/autonomy-levels.yml
.ai/specs/restricted-operations.yml
.ai/specs/quality-rubric.yml
.ai/specs/task.schema.yml
```

Recommended first agent task in each repo:

```md
Use Repo Scout Agent.

Create a repo context pack:
- install/test/lint/typecheck/build commands
- protected paths
- high-risk paths
- owners/reviewers
- missing mechanisms

Do not change production code.
Open a PR with the context pack and recommended guardrails.
```


## v2 first setup for local + cloud agents

1. Copy `AGENTS.md`, `.ai/`, `.github/`, and optional `.codex/` into the repository.
2. Run `.ai/scripts/detect-runtime.sh` to confirm the runtime.
3. Run `.ai/scripts/bootstrap-task-env.sh` to create a task-scoped environment.
4. Run `.ai/scripts/run-agent-quality-gate.sh` before any PR is marked ready.
5. Require the PR template sections `Agent self-review` and `Scale/readiness review`.

Recommended first agent task for every repo:

```md
Use Repo Scout Agent and Cloud Runtime Engineer Agent.
Create or update the repo context pack, document setup/test commands, confirm whether the repo works locally and in Codex Cloud, and add missing guardrails. Do not modify production code.
```


## v3 recommended first run

For each repo, after installing the kit, run a Spec Analyst + Repo Scout onboarding task:

```md
Use Spec Analyst Agent and Repo Scout Agent.

Goal:
Prepare this repo for autonomous agent delivery.

Do not change production code.

Produce:
- repo context pack
- spec comprehension standard check
- default test command inventory
- test strategy recommendation
- protected paths
- clarification/escalation routes
- QA handoff expectations

Open a PR with only documentation/configuration updates.
```

For any real implementation task, start with:

```md
Read the task/spec carefully.
Extract acceptance criteria with IDs.
Ask focused clarifications if needed.
Continue safe progress while waiting.
Build a test traceability matrix.
Implement only unambiguous scope.
Run unit, component, integration, E2E/dev/QA tests as applicable.
Identify and report bugs.
Open a PR with evidence.
Continue with the next ready task if WIP allows.
```


## Branch spec automation

This version supports your workflow of writing specs with ChatGPT/pro models, pushing them to dev/spec branches, and letting agents begin implementation automatically.

Recommended default:

```text
branch: dev/<feature>
spec: specs/<feature>.spec.md
workflow: .github/workflows/agent-spec-ingestion.yml
implementation branch: ai/<spec-id>-<slug>
PR target: dev/<feature>
```

Read `.ai/docs/reference/BRANCH_SPEC_WORKFLOW.md`, `.ai/specs/spec-file-convention.md`, and `.ai/specs/spec-implementation-pipeline.md` before installing this in a repo.

## v9 mandatory Codex PR review

Every PR should now be blocked until the required check passes:

```text
Agentic Codex PR Review / codex_review_gate
```

Install `OPENAI_API_KEY` as a repository secret and add that check to branch protection. See `.ai/docs/reference/CODEX_PR_REVIEW_GATE_V9.md`.

## v10 business questions and SQL analysis

To ask a business/data question, use:

```text
.github/ISSUE_TEMPLATE/data_question.yml
```

Or create a local data-analysis scaffold:

```bash
python .ai/scripts/data_question.py \
  --question "How many users completed registration last week?" \
  --decision "Decide whether registration UX needs improvement"
```

Before querying data, build the business context pack:

```bash
python .ai/scripts/build_business_context.py
```

All SQL must be read-only and run through:

```bash
python .ai/scripts/safe_sql_query.py
```

## v11 addition: prevent parallel branch file conflicts

After installing v11, every agent task performs a branch conflict preflight and postflight. A dev agent must not work on a file already touched by another active non-main branch.

Run manually:

```bash
python .ai/scripts/branch_conflict_guard.py scan --base main
python .ai/scripts/branch_conflict_guard.py guard --mode preflight --base main --path src/example.ts
```

Add this required GitHub status check:

```text
Agentic branch conflict guard / branch_conflict_guard
```

## v12 first command for design readiness

Before implementation, validate a spec with:

```bash
python .ai/scripts/design_gate.py --spec specs/<feature>.spec.md --allow-not-applicable --markdown-output .agent/design-gate.md
```

For full-stack stories, expect separate PRs in this order:

```text
1. database/data model
2. API/backend
3. frontend/UI
```

The watcher will block downstream tasks until upstream layer gates are present on the source branch.


## v13 POC → Spec Branch → Final PR workflow

For the preferred workflow, create a new branch such as `dev/<feature>`, add a ready spec at `specs/<feature>.spec.md`, and push it. The workflow `.github/workflows/agentic-poc-spec-to-pr.yml` detects the spec, runs Codex agents, pushes validated task commits back to the same spec branch, and creates a final PR from that branch to `main` tagging the AI PM.

Start with `.ai/docs/reference/POC_TO_PR_WORKFLOW_V13.md` and `.ai/docs/reference/GPT_PRO_POC_SPEC_PUSH_GUIDE.md`.


## v14 local-first Codex policy

Agentic SDLC now defaults to local mode with Codex `gpt-5.5` and `model_reasoning_effort=xhigh`. Cloud mode is blocked unless explicitly requested with `--allow-cloud` or `AGENTIC_EXPLICIT_CLOUD=true`. See `.ai/docs/reference/LOCAL_FIRST_CODEX_RUNTIME_V14.md`.

## v15 self-improving agents

The package now includes a controlled self-improvement loop. Agents can capture review feedback and propose small updates to skills, evals, examples, scripts, or routing rules, but they cannot silently rewrite their own policy or merge those changes.

Run a dry run:

```bash
python .ai/scripts/skill_improvement_loop.py run-once --dry-run
```

Required review gates for skill changes:

```text
Agentic skill improvement gate / skill_improvement_gate
Agentic Codex PR Review / codex_review_gate
```

See `.ai/docs/reference/SELF_IMPROVEMENT_V15.md`.

