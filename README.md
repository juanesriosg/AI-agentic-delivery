# v14 local-first runtime update

Codex agentic SDLC now defaults to `--mode local` and uses `gpt-5.5` with `model_reasoning_effort=xhigh`. Cloud mode is blocked unless explicitly requested with `--allow-cloud` or `AGENTIC_EXPLICIT_CLOUD=true`. See `LOCAL_FIRST_CODEX_RUNTIME_V14.md`.

# v8 audited/fixed package

Start with `AUDIT_AND_FIX_REPORT.v8.md` and `MANIFEST.v8.md`. This release fixes spec detection, copied-template blocking, scan validation reporting, fallback task routing, local/offline branch behavior, PR guardrails, and AWS/Terraform guardrails.

---

# Agentic Delivery Operating System v7 — Audited and Corrected

This package is the corrected v7 version of the agentic SDLC ecosystem. It keeps the specialized agile agents, branch-spec automation, Codex/local/cloud runtime support, Terraform deployment rules, one-responsibility PR policy, QA/PM gates, and generic spec templates, with additional fixes from the package audit.

Most important v7 corrections:

- Spec templates are safe by default: reusable templates are `draft`, not implementation-ready.
- The orchestrator now validates spec structure before autonomous implementation.
- Draft, template, copied-placeholder, archived, and incomplete specs do not trigger coding.
- Dry-runs do not dirty the repo or mark specs as processed.
- Runtime artifacts are ignored and excluded from the package.
- PR generation satisfies the stricter QA/PM/dev-manager review sections.

Recommended ready-spec flow:

```text
1. Copy specs/_TEMPLATE.agentic-spec.md to specs/<feature>.agentic-spec.md
2. Fill description, requirements, files to touch, tests, risks, acceptance criteria
3. Change status to ready_for_agents only when complete
4. Push to dev/<feature>
5. Run: python .ai/scripts/agentic_sdlc.py watch --mode local --poll-seconds 180
```

# v4 Agile Agent Ecosystem Update

This package now includes a full specialized-agent software delivery lifecycle with product, design, frontend, backend, cloud, QA, PM review, release, visual evidence, agent-to-agent feedback, and persistent `agents.log` artifacts.

Start with these v4 files:

- `AGENTIC_SDLC_V4.md`
- `AGILE_AGENT_ECOSYSTEM.md`
- `VISUAL_QA_WORKFLOW.md`
- `AGENT_FEEDBACK_LOOP.md`
- `.ai/specs/story-lifecycle-v4.yml`
- `.ai/specs/approval-gates-v4.yml`
- `.ai/specs/specialist-agent-routing.yml`
- `.ai/specs/done-v4.yml`
- `.github/workflows/agent-agile-story-orchestration.yml`
- `.github/workflows/agent-stage-gates.yml`
- `.github/workflows/agent-visual-qa.yml`

---

# Agentic Delivery Operating System

This kit defines a practical operating model for autonomous AI coding agents working like mid-level software developers while a human manager focuses on users, stakeholders, data, priorities, architecture, and risk.

The default model is:

- Agents can claim ready tasks.
- Agents can create branches, code, test, self-review, open PRs, and notify the manager.
- Agents cannot merge, deploy to production, delete important assets, force-push, change ownership boundaries, or perform high-risk changes without explicit approval.
- After opening a PR or becoming blocked, an agent continues with the next ready task instead of waiting for the manager.
- The manager reviews outcomes, risks, and PRs at the end of the day.

## How to install in a repo

Copy these files into the repository root:

```text
AGENTS.md
.ai/
.github/
```

Then customize:

```text
.ai/specs/repo-onboarding-checklist.md
.ai/specs/ownership-boundaries.yml
.ai/specs/autonomy-levels.yml
.ai/specs/restricted-operations.yml
.github/CODEOWNERS.example
```

Rename `.github/CODEOWNERS.example` to `.github/CODEOWNERS` after you customize it.

## Operating principle

The system is built around mechanisms, not trust alone:

- Work is small and reversible.
- Quality gates run automatically.
- Every task produces evidence.
- Every PR includes risk, validation, and rollback notes.
- Ownership is explicit.
- High-risk work escalates early.
- Agents keep working from the queue without requiring constant supervision.

## Default autonomy

The default autonomy level is `L3: open PR with tests`.

Agents may:

- Read code and docs.
- Create a branch.
- Modify code within task scope.
- Add/update tests.
- Run validation commands.
- Open or prepare a PR.
- Notify the manager.
- Continue with another ready task.

Agents may not:

- Merge PRs.
- Deploy to production.
- Force-push.
- Delete protected files.
- Rewrite git history.
- Remove tests to make a build pass.
- Modify auth, billing, security, infrastructure, migrations, or public APIs without risk escalation.
- Touch non-owned repos without explicit owner approval.

## Recommended GitHub labels

```text
ai:ready
ai:claimed
ai:in-progress
ai:self-testing
ai:pr-ready
ai:blocked
ai:risk-low
ai:risk-medium
ai:risk-high
ai:needs-owner
manager:review
qa:ready
epic:agent-complete
```

## Recommended board columns

```text
Backlog
Ready for Agent
Claimed
In Progress
Self Testing
PR Ready
Manager Review
Changes Requested
QA / Staging
Done
Blocked
```

## Daily manager workflow

At the end of the day, review:

1. PRs in `manager:review`.
2. High-risk items.
3. Blocked items.
4. Epic progress.
5. Delivery metrics and repeated failure patterns.

Use `.ai/specs/daily-review-template.md`.


---

# v2 additions — Local + Codex Cloud agent runtime

This version adds a portable runtime model for agents that can operate both locally and in remote/cloud coding environments such as Codex Cloud.

The kit intentionally avoids depending on a single vendor API. Agents use repository-native files (`AGENTS.md`, `.ai/specs/*`, `.ai/scripts/*`, `.github/*`) so the same instructions work in:

- local developer machines
- ephemeral cloud sandboxes
- GitHub pull request workflows
- task-per-run systems
- long-running local agent loops

## New capabilities

- Task-scoped virtual environment creation.
- Cloud/runtime detection.
- Bootstrap scripts for Python, Node.js, Go, Rust, Java, .NET, and Ruby projects.
- Self-critique before PR creation.
- Clean code and refactoring standards.
- Architecture and design-pattern decision rules.
- Reliability, concurrency, performance, and security standards.
- Scale-readiness review for code intended to survive growth from one user to very large user bases.
- Stronger deletion and destructive-operation policies.
- Codex Cloud runbook and optional `.codex/` wrappers.

## Manager model

The manager assigns outcomes and reviews evidence. Agents own implementation, test evidence, self-review, PR preparation, and continuation to the next ready task when safe.

Agents must not wait idle after opening a PR unless WIP limits are reached, the task queue is empty, or the runtime ends the session.

## Runtime commands

Use these commands in local or cloud environments:

```bash
.ai/scripts/detect-runtime.sh
.ai/scripts/bootstrap-task-env.sh
.ai/scripts/run-agent-quality-gate.sh
.ai/scripts/agent-self-review.py --format markdown
.ai/scripts/check-scale-readiness.py --format markdown
```

For Codex Cloud or another remote agent runner, configure the setup command to call:

```bash
.codex/bootstrap.sh
```

And configure the validation command to call:

```bash
.codex/run-quality-gate.sh
```

If the platform does not support setup/test hooks, include those commands directly in the task prompt.


## v3 addition: spec-first, test-deep, bug-aware agents

Version 3 adds a stronger developer workflow:

- Agents read specs deeply before coding.
- Agents extract acceptance criteria and assumptions.
- Agents ask focused clarifications without stopping all progress.
- Agents maintain a spec-to-test traceability matrix.
- Agents test at the right levels: unit, component, integration, contract, E2E, dev, QA, and regression.
- Agents actively identify and report bugs.
- Features and epics require QA handoff evidence before being called agent-complete.

Key files:

```text
.ai/agents/spec-analyst.agent.md
.ai/agents/qa-engineer.agent.md
.ai/agents/exploratory-bug-hunter.agent.md
.ai/specs/spec-comprehension-standard.yml
.ai/specs/clarification-policy.yml
.ai/specs/continuous-progress-policy.yml
.ai/specs/testing-lifecycle.yml
.ai/specs/test-strategy-matrix.yml
.ai/specs/bug-identification-standard.yml
.ai/specs/qa-readiness-standard.yml
.ai/scripts/spec-quality-check.py
.ai/scripts/generate-test-matrix.py
.ai/scripts/agent-bug-scan.py
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

Read `BRANCH_SPEC_WORKFLOW.md`, `.ai/specs/spec-file-convention.md`, and `.ai/specs/spec-implementation-pipeline.md` before installing this in a repo.

## v6 generic spec template

Use `specs/_TEMPLATE.agentic-spec.md` when creating specs with ChatGPT Pro. The template includes description, business need, requirements, files to touch, files not to touch, acceptance criteria, testing expectations, AWS/Terraform expectations, PR decomposition, and done notification requirements.

Validate specs with:

```bash
python .ai/scripts/validate_agentic_spec.py specs/<your-spec>.spec.md
```

## v9 mandatory Codex PR review

Every PR should now be blocked until the required check passes:

```text
Agentic Codex PR Review / codex_review_gate
```

Install `OPENAI_API_KEY` as a repository secret and add that check to branch protection. See `CODEX_PR_REVIEW_GATE_V9.md`.

## v10 data analysis agent

v10 adds a Business Data Analyst Agent that can answer business questions with project context and database evidence. It is read-only by design: all database access must go through `.ai/scripts/safe_sql_query.py`, and only `SELECT`, `WITH ... SELECT`, or safe `EXPLAIN SELECT` are allowed.

Useful commands:

```bash
python .ai/scripts/build_business_context.py
python .ai/scripts/safe_sql_query.py --lint-only --sql "SELECT COUNT(*) FROM users"
python .ai/scripts/data_question.py --question "How many users completed registration last week?"
```

Configure database access with a read-only secret or environment variable:

```bash
AGENTIC_DB_DSN_READONLY='postgresql://readonly_user:***@host:5432/dbname'
```

## v11 branch conflict avoidance

v11 adds strict branch conflict control. Agents scan active non-main branches and path leases before coding. If another branch already changed or reserved a file, the agent blocks that task and moves to another task.

New files:

```text
.ai/scripts/branch_conflict_guard.py
.ai/agents/branch-conflict-coordinator.agent.md
.ai/skills/branch-conflict-avoidance.skill.md
.ai/specs/branch-conflict-policy.yml
.github/workflows/agentic-branch-conflict-guard.yml
BRANCH_CONFLICT_AVOIDANCE_V11.md
```

Required status check to add to branch protection:

```text
Agentic branch conflict guard / branch_conflict_guard
```

## v12 design-first layered testing

v12 adds strict design and layer gates:

```text
design gate → database gate → API gate → frontend gate → QA → PM → Codex AI review → human AI PM review
```

The orchestrator runs `.ai/scripts/design_gate.py` before planning and `.ai/scripts/layer_gate.py` before PR guardrails. This prevents a frontend from being marked done when the API is missing, or an API from being marked done when the database contract is missing.


## v13 POC → Spec Branch → Final PR workflow

For the preferred workflow, create a new branch such as `dev/<feature>`, add a ready spec at `specs/<feature>.spec.md`, and push it. The workflow `.github/workflows/agentic-poc-spec-to-pr.yml` detects the spec, runs Codex agents, pushes validated task commits back to the same spec branch, and creates a final PR from that branch to `main` tagging the AI PM.

Start with `POC_TO_PR_WORKFLOW_V13.md` and `GPT_PRO_POC_SPEC_PUSH_GUIDE.md`.


## v14 local-first Codex policy

Agentic SDLC now defaults to local mode with Codex `gpt-5.5` and `model_reasoning_effort=xhigh`. Cloud mode is blocked unless explicitly requested with `--allow-cloud` or `AGENTIC_EXPLICIT_CLOUD=true`. See `LOCAL_FIRST_CODEX_RUNTIME_V14.md`.

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

See `SELF_IMPROVEMENT_V15.md`.

