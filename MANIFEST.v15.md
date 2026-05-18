# Manifest v15 — self-improving agents

v15 builds on v14 local-first Codex execution and adds controlled self-improvement.

## Core files

- `SELF_IMPROVEMENT_V15.md`
- `.ai/specs/self-improvement-policy.yml`
- `.ai/skills/self-improvement-loop.skill.md`
- `.ai/scripts/skill_improvement_loop.py`
- `.github/workflows/agentic-self-improvement.yml`
- `.github/workflows/agentic-skill-improvement-gate.yml`

## Runtime rule

Agents can propose improvements to skills, evals, examples, scripts, and routing rules, but every improvement must be reviewable, evaluated, and approved before it governs future behavior.

## Required branch protection check

Recommended:

```text
Agentic skill improvement gate / skill_improvement_gate
Agentic Codex PR Review / codex_review_gate
```
