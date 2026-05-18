# Skill: Agile Stage Gating

Use this skill to move a story through v4 lifecycle gates.

## Steps

1. Identify the current story state.
2. Read `.ai/specs/story-lifecycle-v4.yml` and `.ai/specs/approval-gates-v4.yml`.
3. Check required artifacts for the current gate.
4. If artifacts are missing, route work to the right specialist agent.
5. If blocking feedback exists, do not promote.
6. Log the gate decision.
7. Update `.agent/stories/<story-id>/state.json`.

## Gate decisions

- `pass`: all required evidence exists and no blocking feedback remains.
- `fail`: a required condition failed and owner agent must fix it.
- `blocked`: human decision or unavailable environment blocks progress.
- `deferred`: manager/repo owner accepted the gap.
