# Self-Improving Agents v15

This layer adds a controlled improvement loop for the agent ecosystem.

The goal is **not** to let agents silently rewrite their own rules. The goal is to turn repeated feedback into durable, reviewable improvements to:

- `.ai/agents/*.agent.md`
- `.ai/skills/*.skill.md`
- `.ai/specs/*.yml` and `.ai/specs/*.md`
- `.ai/evals/**`
- helper scripts and quality gates
- examples and prompts that agents load during work

## Principle

Runtime agents do the work. A slower outer-loop improver studies what happened, proposes a small skill/eval/routing change, runs evals, and opens a PR for human review.

The manager owns the objective. Agents may propose better operating instructions, but they may not merge them, weaken safety rules, expand deployment permissions, or silently change policy.

## Operating loop

```text
normal agent task / PR / QA / PM / Codex review
        ↓
feedback captured from review comments, QA notes, PM notes, CI failures, agents.log, and manager corrections
        ↓
feedback harvester builds a signal bundle
        ↓
skill improver diagnoses repeated failure patterns
        ↓
minimal skill/eval/example/script diff is proposed
        ↓
eval runner checks deterministic rules and regression cases
        ↓
skill improvement PR opens for manager review
        ↓
if merged, future agents load the improved skill files
```

## What counts as high-signal feedback

Good feedback contains a concrete correction and a rationale:

```text
Bad: do better tests
Good: when the frontend calls a new API, require an integration or E2E test that proves the UI works against the real API, not only mocked component tests.
```

```text
Bad: too much text
Good: PR summaries should include evidence links and 5 bullets maximum, with detail moved to docs/agentic-evidence.
```

## What may be improved

Allowed improvement targets:

- clearer skill wording
- missing examples
- missing eval cases
- stricter validation scripts
- better routing rules
- better evidence requirements
- better PR templates
- better failure classification
- better agent handoffs

Blocked without manager approval:

- expanding autonomy levels
- allowing production deploys
- weakening SQL read-only policy
- weakening Terraform/AWS guardrails
- weakening branch conflict policy
- weakening Codex PR review requirements
- relaxing QA/PM gates
- deleting eval cases or safety policies

## Cadence

Runtime task loops happen continuously. Self-improvement loops should be slower:

- manual when you notice repeated failure
- daily at most for active projects
- weekly for stable projects
- only after enough evidence exists

Default threshold:

```text
minimum_feedback_events: 3
minimum_distinct_sources: 2
minimum_eval_cases: 5
```

## Commands

Capture feedback manually:

```bash
python .ai/scripts/capture_agent_feedback.py \
  --source manager_review \
  --target-skill .ai/skills/pr-authoring.skill.md \
  --summary "PR summary was too long" \
  --rationale "Keep PR body concise and move evidence to docs/agentic-evidence" \
  --severity medium \
  --accepted false
```

Harvest GitHub feedback when `gh` is authenticated:

```bash
python .ai/scripts/harvest_github_feedback.py --limit 50
```

Run a local self-improvement dry run:

```bash
python .ai/scripts/skill_improvement_loop.py run-once --dry-run
```

Run and create a proposal branch/PR when configured:

```bash
python .ai/scripts/skill_improvement_loop.py run-once --create-branch --open-pr
```

Run deterministic evals:

```bash
python .ai/scripts/skill_eval_runner.py --all
```

Run PR guardrails for skill changes:

```bash
python .ai/scripts/skill_guardrails.py --base main
```

## Review rule

A skill-improvement PR must include:

- diagnosis
- evidence from feedback
- minimal diff
- eval report
- risk assessment
- rollback plan
- files changed
- expected future behavior improvement

No self-improvement PR is complete until the Codex PR review gate and human manager review pass.
