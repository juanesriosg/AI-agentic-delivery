# Self-improvement proposal: concise PR summaries

## Diagnosis
Three manager reviews accepted the code but asked for shorter PR summaries. The repeated issue is not implementation quality; it is review ergonomics.

## Evidence
- `fb-20260517-001`: PR summary too long.
- `fb-20260517-004`: validation evidence buried under narrative.
- `fb-20260517-009`: manager asked for links instead of copied logs.

## Minimal diff
Update `.ai/skills/pr-authoring.skill.md` to require:

- 5 bullets maximum in main PR summary
- evidence links under `docs/agentic-evidence/**`
- detailed logs outside PR body

Add eval case `EVAL-PR-007` for summary usefulness.

## Expected improvement
Manager review time decreases and PR trust increases without reducing evidence quality.

## Risk
Low. The change affects formatting only.

## Rollback
Revert the skill diff and eval case.
