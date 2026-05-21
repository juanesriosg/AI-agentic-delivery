# Skill: PR Guardrails Remediation

## Goal

Turn guardrail failures into productive corrective action so agent work is not wasted.

## Principles

- Guardrails are quality signals, not dead ends.
- Remediate before restarting a long coding run.
- Preserve useful work and split it when scope is too broad.
- Fix evidence, tests, and PR structure rather than weakening policy.
- Prefer deterministic fixes first, then agent judgment.

## Workflow

1. Run `python .ai/scripts/pr_guardrails_remediator.py --report pr_guardrails.out`.
2. Read `.agent/remediation/pr-guardrails-remediation.md`.
3. Apply the recommended fix.
4. Rerun `python .ai/scripts/pr_guardrails.py ...`.
5. Commit only after guardrails pass.

## Failure classification

| Failure | Preferred remediation |
|---|---|
| Too many lines/files | Split by responsibility or ignore runtime/evidence noise if policy supports it |
| Missing evidence directory | Move/copy evidence to expected task-id path; do not invent results |
| Pending evidence | Run checks and replace placeholders with real outputs |
| No tests | Add tests or explicit non-applicable evidence |
| Multiple domains | Split into DB → API → frontend/cloud/security PRs |
| Branch conflict | Switch task or extract a new component/file |

## Quality bar

A remediation is complete only when:

- guardrails pass;
- the PR still has one responsibility;
- real validation evidence exists;
- no useful implementation work was silently discarded;
- the remediation report explains what changed.
