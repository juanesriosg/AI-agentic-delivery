# Skill: self-improvement-loop

## Purpose
Turn repeated agent mistakes and human corrections into durable, reviewable improvements to the agent operating system.

## Operating context
This skill applies to Codex/local agents, repo-level scripts, PR workflows, QA/PM gates, data analysis agents, and AWS/Terraform agents. It uses repository files, feedback logs, eval cases, CI gates, and human review.

## Principles
- Runtime work and learning are separate loops.
- Skills are reviewable files, not invisible memory.
- A single complaint is not automatically a new rule.
- Improve the smallest durable mechanism that explains a class of failures.
- Add evals when behavior changes.
- Do not weaken safety to improve speed.
- Measure usefulness, not activity.
- Human manager owns the objective and final merge.

## Procedure
1. Capture feedback through the normal work surface.
2. Cluster signals by root cause.
3. Decide if the failure belongs in a skill, example, eval, script, routing rule, or spec template.
4. Propose a minimal diff.
5. Run evals and guardrails.
6. Open a self-improvement PR.
7. Wait for Codex AI review and human manager approval.
8. If merged, monitor whether future outcomes improve.

## Quality bar
A self-improvement diff must be evidence-backed, narrow, evaluated, reversible, and safe.

## Uncertainty behavior
Ask for human approval before changing objectives, autonomy, security boundaries, data access, deployment rights, or review gates.

## Feedback hooks
Read:

- `.agent/feedback/feedback.jsonl`
- `docs/agentic-feedback/**`
- `docs/agentic-evidence/**`
- PR comments and review summaries
- Codex PR review output
- QA/PM checklists
- CI failure logs
