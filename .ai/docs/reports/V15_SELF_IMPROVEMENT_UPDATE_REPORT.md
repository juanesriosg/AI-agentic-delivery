# v15 update report — self-improving agents

## Summary

v15 adds a controlled self-improvement loop for the agent ecosystem.

The agents can now collect feedback, synthesize repeated failures, propose small improvements to skills/evals/examples/scripts, run evals, and open a PR for human review.

They still cannot silently rewrite their own policy, merge their own improvements, expand autonomy, weaken safety, or bypass manager approval.

## Added

```text
.ai/docs/reference/SELF_IMPROVEMENT_V15.md
.ai/agents/feedback-harvester.agent.md
.ai/agents/skill-improver.agent.md
.ai/agents/eval-designer.agent.md
.ai/agents/skill-improvement-reviewer.agent.md
.ai/skills/self-improvement-loop.skill.md
.ai/skills/feedback-capture.skill.md
.ai/skills/evaluation-design.skill.md
.ai/specs/self-improvement-policy.yml
.ai/specs/skill-file-standard.md
.ai/specs/improvement-proposal.schema.yml
.ai/specs/eval-case.schema.yml
.ai/specs/skill-improvement-gate.yml
.ai/evals/skill-improvement/eval-cases.json
.ai/scripts/capture_agent_feedback.py
.ai/scripts/skill_improvement_loop.py
.ai/scripts/skill_eval_runner.py
.ai/scripts/skill_guardrails.py
.ai/scripts/harvest_github_feedback.py
.github/workflows/agentic-self-improvement.yml
.github/workflows/agentic-skill-improvement-gate.yml
.github/ISSUE_TEMPLATE/agent_feedback.yml
.github/codex/prompts/skill-improvement.md
docs/agentic-feedback/README.md
docs/agentic-self-improvement/README.md
```

## Updated

```text
AGENTS.md
README.md
.ai/docs/START_HERE.md
.ai/automation/agentic.config.json
.github/PULL_REQUEST_TEMPLATE.md
.ai/docs/manifests/MANIFEST.v15.md
```

## Behavior

Self-improvement is separate from normal execution:

```text
runtime agents do work
feedback is captured
outer-loop skill improver proposes updates
skill evals run
skill guardrails run
Codex AI review runs
manager approves or rejects
```

## Safety controls

The loop blocks:

- silent policy changes
- self-merge
- autonomy expansion without approval
- production deploy permission changes
- SQL read-only weakening
- Terraform/AWS guardrail weakening
- QA/PM gate weakening
- Codex PR review weakening
- branch conflict policy weakening
- eval deletion without replacement

## Validation

Validated with Python compile checks, JSON parse checks, workflow YAML parsing, feedback capture simulation, eval runner pass/fail cases, skill guardrail pass/fail cases, and package cleanup checks.
